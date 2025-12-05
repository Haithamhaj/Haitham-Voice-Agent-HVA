import os
import logging
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from haitham_voice_agent.tools.memory.voice_tools import VoiceMemoryTools
from haitham_voice_agent.tools.memory.storage.sqlite_store import SQLiteStore
from haitham_voice_agent.config import Config

logger = logging.getLogger(__name__)

class AdaptiveSync:
    """
    Adaptive Sync & Learning System
    Detects offline file moves/renames and updates the Knowledge Base.
    """
    
    def __init__(self):
        self.memory_tools = VoiceMemoryTools()
        # We need direct access to SQLite for low-level index checks
        self.sqlite_store = SQLiteStore()
        
    async def ensure_initialized(self):
        await self.memory_tools.ensure_initialized()
        # SQLiteStore is initialized by memory_tools usually, but safe to init again
        await self.sqlite_store.initialize()

    def calculate_file_hash(self, file_path: Path) -> Optional[str]:
        """Calculate MD5 hash of a file (Digital Fingerprint)"""
        try:
            if not file_path.exists() or not file_path.is_file():
                return None
                
            # Limit to first 10MB to avoid freezing on huge files
            MAX_SIZE = 10 * 1024 * 1024 
            file_size = file_path.stat().st_size
            
            # Upgrade to SHA-256 for better collision resistance
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                if file_size > MAX_SIZE:
                    # Read head and tail for speed on large files
                    hasher.update(f.read(1024 * 1024)) # 1MB Head
                    f.seek(-1024 * 1024, 2)
                    hasher.update(f.read(1024 * 1024)) # 1MB Tail
                else:
                    # Read all
                    buf = f.read(65536)
                    while len(buf) > 0:
                        hasher.update(buf)
                        buf = f.read(65536)
                        
            return hasher.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to hash {file_path}: {e}")
            return None

    async def sync_knowledge_base(self, scan_roots: List[str] = None, index_new: bool = False) -> Dict[str, int]:
        """
        Scan file system and sync with DB.
        Detects:
        1. Moved files (Same Hash, Different Path) -> Update DB + Learn
        2. Renamed files (Same Hash, Different Name) -> Update DB + Learn
        3. New files -> Index (if index_new=True)
        """
        logger.info("🔄 Starting Adaptive Sync (Offline Learning)...")
        await self.ensure_initialized()
        
        if not scan_roots:
            scan_roots = [
                str(Path.home() / "Documents"),
                str(Path.home() / "Applications"),
                str(Path.home() / "Software")
            ]
            
        stats = {
            "scanned": 0,
            "learned_moves": 0,
            "new_indexed": 0,
            "errors": 0
        }
        
        for root_str in scan_roots:
            root = Path(root_str)
            if not root.exists():
                continue
                
            for current_path in root.rglob("*"):
                if current_path.is_file() and not current_path.name.startswith("."):
                    try:
                        stats["scanned"] += 1
                        
                        # 1. Calculate Hash
                        file_hash = self.calculate_file_hash(current_path)
                        if not file_hash:
                            continue
                            
                        # 2. Check DB for this Hash
                        # We need a method to find by hash. Let's add it or use raw query.
                        # For now, we'll use a raw query helper here or assume we add it to SQLiteStore.
                        # Let's use raw query via sqlite_store connection for now to avoid modifying store yet.
                        
                        existing_record = await self._find_file_by_hash(file_hash)
                        
                        if existing_record:
                            old_path = Path(existing_record["path"])
                            
                            # 3. Detect Change
                            if old_path.resolve() != current_path.resolve():
                                # MOVED or RENAMED!
                                logger.info(f"🎓 LEARNING: Detected move {old_path.name} -> {current_path.name}")
                                logger.info(f"   Old Path: {old_path}")
                                logger.info(f"   New Path: {current_path}")
                                
                                # Extract categories from paths
                                old_category = self._extract_category(old_path)
                                new_category = self._extract_category(current_path)
                                
                                # Log learning event
                                await self.sqlite_store.log_learning_event(
                                    file_hash=file_hash,
                                    event_type="manual_move",
                                    old_path=str(old_path),
                                    new_path=str(current_path),
                                    old_category=old_category,
                                    new_category=new_category,
                                    description=existing_record["description"],
                                    embedding_id=existing_record.get("embedding_id")
                                )
                                
                                # Update DB
                                await self.memory_tools.memory_system.index_file(
                                    path=str(current_path),
                                    project_id=existing_record["project_id"], 
                                    description=existing_record["description"],
                                    tags=json.loads(existing_record["tags"]) if existing_record["tags"] else [],
                                    file_hash=file_hash
                                )
                                stats["learned_moves"] += 1
                            else:
                                # logger.info(f"No change for {current_path.name}")
                                pass
                        else:
                            # New File
                            if index_new:
                                logger.info(f"🆕 Indexing new file: {current_path.name}")
                                await self.memory_tools.memory_system.index_file(
                                    path=str(current_path),
                                    project_id="default",
                                    description=f"Discovered during sync: {current_path.name}",
                                    tags=["discovered", "sync"],
                                    file_hash=file_hash
                                )
                                stats["new_indexed"] += 1
                            else:
                                # logger.info(f"New file found (not in DB): {current_path.name}")
                                pass
                            
                    except Exception as e:
                        logger.error(f"Error syncing {current_path}: {e}")
                        stats["errors"] += 1
                        
        # --- PASSIVE FEEDBACK: Check auto-applied events ---
        # If files organized using learned patterns are still in place, increase confidence
        # If they were moved again, decrease confidence
        try:
            import aiosqlite
            async with aiosqlite.connect(self.sqlite_store.db_path) as db:
                db.row_factory = aiosqlite.Row
                # Get all auto_applied events from last 7 days
                async with db.execute("""
                    SELECT * FROM learning_events 
                    WHERE event_type = 'auto_applied' 
                    AND timestamp > datetime('now', '-7 days')
                """) as cursor:
                    auto_events = await cursor.fetchall()
                    
                for event in auto_events:
                    event_dict = dict(event)
                    new_path = Path(event_dict['new_path'])
                    file_hash = event_dict['file_hash']
                    
                    # Check if file is still at new_path
                    if new_path.exists():
                        current_hash = self.calculate_file_hash(new_path)
                        if current_hash == file_hash:
                            # File stayed in place! Increase confidence
                            # Find the original learning event (manual_move) for this category
                            async with db.execute("""
                                SELECT id FROM learning_events 
                                WHERE event_type = 'manual_move' 
                                AND new_category = ?
                                ORDER BY confidence DESC
                                LIMIT 1
                            """, (event_dict['new_category'],)) as cursor2:
                                original_event = await cursor2.fetchone()
                                if original_event:
                                    await self.sqlite_store.update_learning_confidence(
                                        event_id=original_event[0],
                                        delta=+0.1,
                                        feedback="confirmed"
                                    )
                                    logger.info(f"✅ Increased confidence for {event_dict['new_category']} (file stayed in place)")
                    else:
                        # File was moved again! Decrease confidence
                        async with db.execute("""
                            SELECT id FROM learning_events 
                            WHERE event_type = 'manual_move' 
                            AND new_category = ?
                            ORDER BY confidence DESC
                            LIMIT 1
                        """, (event_dict['new_category'],)) as cursor2:
                            original_event = await cursor2.fetchone()
                            if original_event:
                                await self.sqlite_store.update_learning_confidence(
                                    event_id=original_event[0],
                                    delta=-0.3,
                                    feedback="rejected"
                                )
                                logger.info(f"❌ Decreased confidence for {event_dict['new_category']} (file was moved again)")
        except Exception as e:
            logger.warning(f"Passive feedback check failed: {e}")
        # -----------------------------------
                        
        logger.info(f"✅ Adaptive Sync Complete: {stats}")
        return stats

    async def audit_fingerprints(self) -> Dict[str, int]:
        """
        Audit and backfill missing/outdated fingerprints (hashes).
        Ensures 100% coverage with SHA-256.
        """
        logger.info("🕵️‍♂️ Starting Digital Fingerprint Audit...")
        await self.ensure_initialized()
        
        stats = {"checked": 0, "updated": 0, "errors": 0}
        
        try:
            import aiosqlite
            async with aiosqlite.connect(self.sqlite_store.db_path) as db:
                db.row_factory = aiosqlite.Row
                # Get all files
                async with db.execute("SELECT path, file_hash FROM file_index") as cursor:
                    rows = await cursor.fetchall()
                    
                for row in rows:
                    path_str = row["path"]
                    current_hash = row["file_hash"]
                    file_path = Path(path_str)
                    
                    stats["checked"] += 1
                    
                    if not file_path.exists():
                        continue
                        
                    # Check if hash is missing or looks like MD5 (32 chars) vs SHA-256 (64 chars)
                    needs_update = not current_hash or len(current_hash) != 64
                    
                    if needs_update:
                        new_hash = self.calculate_file_hash(file_path)
                        if new_hash:
                            await db.execute(
                                "UPDATE file_index SET file_hash = ? WHERE path = ?",
                                (new_hash, path_str)
                            )
                            stats["updated"] += 1
                            logger.info(f"Updated fingerprint for {file_path.name} (SHA-256)")
                            
                await db.commit()
                
        except Exception as e:
            logger.error(f"Audit failed: {e}")
            stats["errors"] += 1
            
        logger.info(f"✅ Audit Complete: {stats}")
        return stats

    async def _find_file_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Helper to find file by hash"""
        try:
            import aiosqlite
            import json
            async with aiosqlite.connect(self.sqlite_store.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM file_index WHERE file_hash = ?", (file_hash,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return dict(row)
            return None
        except Exception:
            return None

    def _extract_category(self, file_path: Path) -> str:
        """Extract category from file path (e.g., 'Documents/Technology' -> 'Technology')"""
        try:
            # Get relative path from Documents root
            docs_root = Path.home() / "Documents"
            if str(file_path).startswith(str(docs_root)):
                rel_path = file_path.relative_to(docs_root)
                parts = rel_path.parts
                if len(parts) > 1:
                    # Return first subfolder as category
                    return parts[0]
            return "Uncategorized"
        except Exception:
            return "Uncategorized"

