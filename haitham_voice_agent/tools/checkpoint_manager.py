import logging
import json
import uuid
import shutil
import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from haitham_voice_agent.tools.memory.storage.sqlite_store import SQLiteStore
from haitham_voice_agent.tools.memory.memory_system import memory_system

logger = logging.getLogger(__name__)

class CheckpointManager:
    """
    Manages file operation checkpoints and rollbacks (Time Machine).
    """
    
    def __init__(self):
        # We access the store via the global memory system
        self.store = memory_system.sqlite_store
        
    async def create_checkpoint(self, action_type: str, description: str, operations: List[Dict[str, str]], meta: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new checkpoint.
        
        Args:
            action_type: Type of action (e.g., "deep_organize")
            description: User-friendly description
            operations: List of dicts with 'src' and 'dst' keys showing what was moved.
            meta: Optional metadata (model, cost, tokens)
        """
        checkpoint_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Store meta inside the data JSON
        data_to_store = {
            "operations": operations,
            "meta": meta or {}
        }
        
        try:
            async with aiosqlite.connect(self.store.db_path) as db:
                await db.execute("""
                    INSERT INTO checkpoints (id, timestamp, action_type, description, data, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    checkpoint_id,
                    timestamp,
                    action_type,
                    description,
                    json.dumps(data_to_store),
                    "active"
                ))
                await db.commit()
                
            logger.info(f"Checkpoint created: {checkpoint_id} ({description})")
            return checkpoint_id
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            return None

    async def get_checkpoints(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent checkpoints"""
        try:
            async with aiosqlite.connect(self.store.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT * FROM checkpoints 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get checkpoints: {e}")
            return []

    async def rollback_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Rollback a specific checkpoint.
        Reverses the operations (moves files from 'dst' back to 'src').
        """
        logger.info(f"Rolling back checkpoint: {checkpoint_id}")
        
        report = {
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            # 1. Get Checkpoint Data
            async with aiosqlite.connect(self.store.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM checkpoints WHERE id = ?", (checkpoint_id,)) as cursor:
                    row = await cursor.fetchone()
                    
            if not row:
                return {"error": "Checkpoint not found"}
                
            checkpoint = dict(row)
            if checkpoint["status"] == "rolled_back":
                return {"error": "Checkpoint already rolled back"}
                
            raw_data = json.loads(checkpoint["data"])
            
            # Handle backward compatibility (old format was list, new is dict)
            if isinstance(raw_data, list):
                operations = raw_data
            else:
                operations = raw_data.get("operations", [])
            
            # 2. Reverse Operations
            # We iterate in reverse order just in case
            for op in reversed(operations):
                src_original = Path(op["src"])
                dst_current = Path(op["dst"])
                
                try:
                    if not dst_current.exists():
                        report["failed"] += 1
                        report["errors"].append(f"File missing: {dst_current}")
                        continue
                        
                    # Ensure parent of original source exists
                    src_original.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move back
                    shutil.move(str(dst_current), str(src_original))
                    report["success"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to rollback {dst_current} -> {src_original}: {e}")
                    report["failed"] += 1
                    report["errors"].append(f"{dst_current.name}: {str(e)}")
            
            # 3. Update Status
            async with aiosqlite.connect(self.store.db_path) as db:
                await db.execute("UPDATE checkpoints SET status = 'rolled_back' WHERE id = ?", (checkpoint_id,))
                await db.commit()
                
            return report
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return {"error": str(e)}

# Singleton
_checkpoint_manager = None

def get_checkpoint_manager():
    global _checkpoint_manager
    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager()
    return _checkpoint_manager
