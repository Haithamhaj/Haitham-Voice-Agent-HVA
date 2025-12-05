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
            
            # Create File Index Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS file_index (
                    path TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    description TEXT,
                    tags TEXT, -- JSON list
                    last_modified TEXT,
                    embedding_id TEXT,
                    file_hash TEXT
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_file_project ON file_index(project_id)")
            
            # Migration: Add file_hash if missing
            try:
                await db.execute("ALTER TABLE file_index ADD COLUMN file_hash TEXT")
            except Exception:
                pass # Column likely exists

            # Create Token Usage Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS token_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model TEXT NOT NULL,
                    input_tokens INTEGER NOT NULL,
                    output_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    cost REAL NOT NULL,
                    context TEXT -- JSON dict for extra metadata (e.g. tool used)
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON token_usage(timestamp)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_usage_model ON token_usage(model)")
            
            # Create Checkpoints Table (Time Machine)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    data TEXT NOT NULL, -- JSON list of operations
                    status TEXT DEFAULT 'active' -- active, rolled_back
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_checkpoint_timestamp ON checkpoints(timestamp)")
            
            # Create optimization cache table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS optimization_cache (
                    hash TEXT PRIMARY KEY,
                    context TEXT NOT NULL,
                    result TEXT,
                    timestamp TEXT NOT NULL,
                    cost_saved REAL DEFAULT 0.0
                )
            """)
            
            # Create learning events table (Adaptive Learning)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS learning_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_hash TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    old_path TEXT,
                    new_path TEXT,
                    old_category TEXT,
                    new_category TEXT,
                    timestamp TEXT NOT NULL,
                    description TEXT,
                    embedding_id TEXT,
                    confidence REAL DEFAULT 1.0,
                    times_applied INTEGER DEFAULT 0,
                    last_feedback TEXT
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_learning_hash ON learning_events(file_hash)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_learning_confidence ON learning_events(confidence)")
            
            await db.commit()
            logger.info("SQLite schema initialized")

    async def get_optimization_cache(self, file_hash: str, context: str) -> Optional[Dict[str, Any]]:
        """Get cached result for optimization guard"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT * FROM optimization_cache WHERE hash = ? AND context = ?", 
                    (file_hash, context)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        data = dict(row)
                        if data["result"]:
                            data["result"] = json.loads(data["result"])
                        return data
            return None
        except Exception as e:
            logger.error(f"Failed to get optimization cache: {e}")
            return None

    async def save_optimization_cache(self, file_hash: str, context: str, result: Dict[str, Any], cost_saved: float = 0.0):
        """Save result to optimization cache"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO optimization_cache (hash, context, result, timestamp, cost_saved)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    file_hash,
                    context,
                    json.dumps(result),
                    datetime.now().isoformat(),
                    cost_saved
                ))
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to save optimization cache: {e}")

    async def log_learning_event(self, file_hash: str, event_type: str, old_path: str, new_path: str, 
                                  old_category: str, new_category: str, description: str = "", embedding_id: str = None):
        """Log a learning event (manual file move/rename)"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO learning_events 
                    (file_hash, event_type, old_path, new_path, old_category, new_category, timestamp, description, embedding_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_hash, event_type, old_path, new_path, old_category, new_category,
                    datetime.now().isoformat(), description, embedding_id
                ))
                await db.commit()
                logger.info(f"Logged learning event: {old_category} -> {new_category}")
        except Exception as e:
            logger.error(f"Failed to log learning event: {e}")

    async def get_learning_events_by_category(self, new_category: str, min_confidence: float = 0.5):
        """Get learning events for a specific category with minimum confidence"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT * FROM learning_events 
                    WHERE new_category = ? AND confidence >= ?
                    ORDER BY confidence DESC, times_applied DESC
                    LIMIT 10
                """, (new_category, min_confidence)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get learning events: {e}")
            return []

    async def update_learning_confidence(self, event_id: int, delta: float, feedback: str):
        """Update confidence score for a learning event"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get current confidence
                async with db.execute("SELECT confidence, times_applied FROM learning_events WHERE id = ?", (event_id,)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        return
                    
                    current_confidence = row[0]
                    times_applied = row[1]
                
                # Calculate new confidence (clamp between 0.1 and 2.0)
                new_confidence = max(0.1, min(2.0, current_confidence + delta))
                
                # Update
                await db.execute("""
                    UPDATE learning_events 
                    SET confidence = ?, times_applied = ?, last_feedback = ?
                    WHERE id = ?
                """, (new_confidence, times_applied + 1, feedback, event_id))
                await db.commit()
                logger.info(f"Updated learning event {event_id}: confidence={new_confidence}, feedback={feedback}")
        except Exception as e:
            logger.error(f"Failed to update learning confidence: {e}")


    async def index_file(self, path: str, project_id: str, description: str = "", tags: List[str] = None, embedding_id: str = None, file_hash: str = None) -> bool:
        """Index a file"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO file_index (path, project_id, description, tags, last_modified, embedding_id, file_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    path, 
                    project_id, 
                    description, 
                    json.dumps(tags or []), 
                    datetime.now().isoformat(), 
                    embedding_id,
                    file_hash
                ))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to index file {path}: {e}")
            return False

    async def get_file_index(self, path: str) -> Optional[Dict[str, Any]]:
        """Get file index entry"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM file_index WHERE path = ?", (path,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        data = dict(row)
                        if data["tags"]:
                            data["tags"] = json.loads(data["tags"])
                        return data
            return None
        except Exception as e:
            logger.error(f"Failed to get file index {path}: {e}")
            return None

    async def search_file_index(self, query_text: str) -> List[Dict[str, Any]]:
        """Search file index by description or tags"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                search_term = f"%{query_text}%"
                async with db.execute("""
                    SELECT * FROM file_index 
                    WHERE description LIKE ? OR tags LIKE ? OR path LIKE ?
                """, (search_term, search_term, search_term)) as cursor:
                    rows = await cursor.fetchall()
                    results = []
                    for row in rows:
                        data = dict(row)
                        if data["tags"]:
                            data["tags"] = json.loads(data["tags"])
                        results.append(data)
                    return results
        except Exception as e:
            logger.error(f"Failed to search file index: {e}")
            return []

    async def find_path_by_name(self, name: str) -> Optional[str]:
        """
        Find the full path of a file or folder by its name.
        Returns the most recently modified match if duplicates exist.
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                # Search for path ending with /name or exactly name
                # We order by last_modified DESC to get the most relevant/recent one
                async with db.execute("""
                    SELECT path FROM file_index 
                    WHERE path LIKE ? OR path LIKE ?
                    ORDER BY last_modified DESC
                    LIMIT 1
                """, (f"%/{name}", f"%/{name}/")) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return row['path']
                    
                    # Fallback: Look for children to infer folder existence
                    # If we have files like ".../Coaching/file.pdf", then ".../Coaching" exists
                    await cursor.execute("""
                        SELECT path FROM file_index 
                        WHERE path LIKE ? 
                        LIMIT 1
                    """, (f"%/{name}/%",))
                    row = await cursor.fetchone()
                    if row:
                        full_path = row['path']
                        parts = full_path.split('/')
                        if name in parts:
                            # Return path up to the folder name
                            # e.g. /Users/haitham/Documents/Coaching
                            idx = parts.index(name)
                            return '/'.join(parts[:idx+1])
                            
            return None
        except Exception as e:
            logger.error(f"Failed to find path by name {name}: {e}")
            return None

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

    async def count_memories(self) -> int:
        """Count total memories"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT COUNT(*) FROM memories") as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0
        except Exception as e:
            logger.error(f"Failed to count memories: {e}")
            return 0

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

    async def log_token_usage(self, model: str, input_tokens: int, output_tokens: int, cost: float, context: Dict[str, Any] = None) -> bool:
        """Log token usage and cost"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO token_usage (timestamp, model, input_tokens, output_tokens, total_tokens, cost, context)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    model,
                    input_tokens,
                    output_tokens,
                    input_tokens + output_tokens,
                    cost,
                    json.dumps(context or {})
                ))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to log token usage: {e}")
            return False

    async def get_token_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for the last N days"""
        try:
            modifier = f"-{days} days"
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                # Total Stats
                async with db.execute("""
                    SELECT 
                        SUM(cost) as total_cost,
                        SUM(total_tokens) as total_tokens,
                        COUNT(*) as request_count
                    FROM token_usage
                    WHERE timestamp > date('now', ?)
                """, (modifier,)) as cursor:
                    total_row = await cursor.fetchone()
                    total_stats = dict(total_row) if total_row else {}

                # Stats by Model
                async with db.execute("""
                    SELECT 
                        model,
                        SUM(cost) as cost,
                        SUM(total_tokens) as tokens,
                        COUNT(*) as count
                    FROM token_usage
                    WHERE timestamp > date('now', ?)
                    GROUP BY model
                    ORDER BY cost DESC
                """, (modifier,)) as cursor:
                    model_rows = await cursor.fetchall()
                    model_stats = [dict(row) for row in model_rows]

                # Daily Stats (for Chart)
                # Group by date (YYYY-MM-DD)
                async with db.execute("""
                    SELECT 
                        substr(timestamp, 1, 10) as date,
                        SUM(cost) as cost,
                        SUM(total_tokens) as tokens
                    FROM token_usage
                    WHERE timestamp > date('now', ?)
                    GROUP BY date
                    ORDER BY date ASC
                """, (modifier,)) as cursor:
                    daily_rows = await cursor.fetchall()
                    daily_stats = [dict(row) for row in daily_rows]

                return {
                    "period_days": days,
                    "total_cost": total_stats.get("total_cost") or 0.0,
                    "total_tokens": total_stats.get("total_tokens") or 0,
                    "request_count": total_stats.get("request_count") or 0,
                    "by_model": model_stats,
                    "daily_stats": daily_stats
                }
        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
            return {}

    async def get_token_usage_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get raw usage logs"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT * FROM token_usage 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    results = []
                    for row in rows:
                        data = dict(row)
                        if data["context"]:
                            try:
                                data["context"] = json.loads(data["context"])
                            except:
                                data["context"] = {}
                        results.append(data)
                    return results
        except Exception as e:
            logger.error(f"Failed to get usage logs: {e}")
            return []
