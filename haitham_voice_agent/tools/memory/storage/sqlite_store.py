import aiosqlite
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from haitham_voice_agent.config import Config
from ..models.memory import Memory, MemoryType, MemorySource, SensitivityLevel

logger = logging.getLogger(__name__)

class SQLiteStore:
    """
    Async SQLite storage for Memory objects
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Config.MEMORY_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"SQLiteStore initialized at {self.db_path}")

    async def initialize(self):
        """Initialize database schema"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    project TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    type TEXT NOT NULL,
                    tags TEXT NOT NULL, -- JSON list
                    ultra_brief TEXT NOT NULL,
                    executive_summary TEXT NOT NULL, -- JSON list
                    detailed_summary TEXT NOT NULL,
                    raw_content TEXT,
                    decisions TEXT NOT NULL, -- JSON list
                    action_items TEXT NOT NULL, -- JSON list
                    open_questions TEXT NOT NULL, -- JSON list
                    key_insights TEXT NOT NULL, -- JSON list
                    people_mentioned TEXT NOT NULL, -- JSON list
                    projects_mentioned TEXT NOT NULL, -- JSON list
                    conversation_id TEXT,
                    parent_memory_id TEXT,
                    related_memory_ids TEXT NOT NULL, -- JSON list
                    language TEXT NOT NULL,
                    sentiment TEXT NOT NULL,
                    importance INTEGER NOT NULL,
                    confidence REAL NOT NULL,
                    sensitivity TEXT NOT NULL,
                    access_count INTEGER NOT NULL,
                    last_accessed TEXT,
                    version INTEGER NOT NULL,
                    created_by TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    updated_at TEXT,
                    status TEXT DEFAULT 'active',
                    structured_data TEXT, -- JSON dict
                    nag_count INTEGER DEFAULT 0
                )
            """)
            
            # Create indices for common queries
            await db.execute("CREATE INDEX IF NOT EXISTS idx_project ON memories(project)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_type ON memories(type)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            
            await db.commit()
            logger.info("SQLite schema initialized")

    async def save_memory(self, memory: Memory) -> bool:
        """Save or update memory"""
        try:
            data = memory.to_dict()
            
            # Serialize list fields to JSON
            list_fields = [
                "tags", "executive_summary", "decisions", "action_items", 
                "open_questions", "key_insights", "people_mentioned", 
                "projects_mentioned", "related_memory_ids", "structured_data"
            ]
            
            for field in list_fields:
                data[field] = json.dumps(data[field])
            
            # Remove embedding (stored in Vector DB)
            if "embedding" in data:
                del data["embedding"]
                
            async with aiosqlite.connect(self.db_path) as db:
                columns = ", ".join(data.keys())
                placeholders = ", ".join(["?" for _ in data])
                values = list(data.values())
                
                sql = f"""
                    INSERT OR REPLACE INTO memories ({columns})
                    VALUES ({placeholders})
                """
                
                await db.execute(sql, values)
                await db.commit()
                
            logger.debug(f"Saved memory {memory.id} to SQLite")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save memory {memory.id}: {e}")
            return False

    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieve memory by ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    data = dict(row)
                    
                    # Deserialize JSON fields
                    list_fields = [
                        "tags", "executive_summary", "decisions", "action_items", 
                        "open_questions", "key_insights", "people_mentioned", 
                        "projects_mentioned", "related_memory_ids", "structured_data"
                    ]
                    
                    for field in list_fields:
                        if data[field]:
                            data[field] = json.loads(data[field])
                        else:
                            data[field] = []
                            
                    return Memory.from_dict(data)
                    
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            return None

    async def search_memories(
        self, 
        query_text: Optional[str] = None,
        project: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10
    ) -> List[Memory]:
        """
        Basic SQL search (filters + simple text match)
        Note: Full semantic search happens in VectorStore
        """
        try:
            conditions = []
            params = []
            
            if project:
                conditions.append("project = ?")
                params.append(project)
                
            if memory_type:
                conditions.append("type = ?")
                params.append(memory_type.value)
                
            if query_text:
                # Simple LIKE search on summary and content
                conditions.append("(detailed_summary LIKE ? OR raw_content LIKE ?)")
                search_term = f"%{query_text}%"
                params.extend([search_term, search_term])
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            sql = f"SELECT * FROM memories {where_clause} ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(sql, params) as cursor:
                    rows = await cursor.fetchall()
                    
                    results = []
                    for row in rows:
                        data = dict(row)
                        # Deserialize JSON fields (same logic as get_memory)
                        list_fields = [
                            "tags", "executive_summary", "decisions", "action_items", 
                            "open_questions", "key_insights", "people_mentioned", 
                            "projects_mentioned", "related_memory_ids", "structured_data"
                        ]
                        for field in list_fields:
                            if data[field]:
                                data[field] = json.loads(data[field])
                            else:
                                data[field] = []
                        
                        results.append(Memory.from_dict(data))
                        
                    return results
                    
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete memory by ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    async def get_stale_items(self, days: int = 3) -> List[Memory]:
        """
        Get active projects that haven't been updated in 'days'
        """
        try:
            # Calculate threshold date
            # SQLite 'now' is UTC, ensure we compare correctly or use python date
            # Let's use python date for consistency with timestamp format in DB (ISO)
            # Actually, DB stores ISO strings. SQLite date functions work with ISO strings.
            
            sql = """
                SELECT * FROM memories 
                WHERE type = 'project' 
                AND status = 'active' 
                AND (
                    updated_at < date('now', ?) 
                    OR (updated_at IS NULL AND timestamp < date('now', ?))
                )
                ORDER BY importance DESC
            """
            
            modifier = f"-{days} days"
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(sql, (modifier, modifier)) as cursor:
                    rows = await cursor.fetchall()
                    
                    results = []
                    for row in rows:
                        data = dict(row)
                        # Deserialize JSON fields
                        list_fields = [
                            "tags", "executive_summary", "decisions", "action_items", 
                            "open_questions", "key_insights", "people_mentioned", 
                            "projects_mentioned", "related_memory_ids", "structured_data"
                        ]
                        for field in list_fields:
                            if data[field]:
                                data[field] = json.loads(data[field])
                            else:
                                data[field] = []
                        
                        results.append(Memory.from_dict(data))
                        
                    return results
                    
        except Exception as e:
            logger.error(f"Failed to get stale items: {e}")
            return []
