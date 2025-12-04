import logging
import aiosqlite
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from haitham_voice_agent.config import Config

logger = logging.getLogger(__name__)

class GraphStore:
    """
    Lightweight Graph Store backed by SQLite.
    Stores nodes and edges to represent relationships.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Config.MEMORY_DB_PATH
        
    async def initialize(self):
        """Initialize graph schema"""
        async with aiosqlite.connect(self.db_path) as db:
            # Nodes table (optional, mostly for properties)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS graph_nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    properties TEXT -- JSON
                )
            """)
            
            # Edges table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS graph_edges (
                    source TEXT NOT NULL,
                    target TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    properties TEXT, -- JSON
                    PRIMARY KEY (source, target, relation)
                )
            """)
            
            await db.execute("CREATE INDEX IF NOT EXISTS idx_edge_source ON graph_edges(source)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_edge_target ON graph_edges(target)")
            await db.commit()
            logger.info("GraphStore schema initialized")

    async def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any] = None):
        """Add or update a node"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO graph_nodes (id, type, properties)
                    VALUES (?, ?, ?)
                """, (node_id, node_type, json.dumps(properties or {})))
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to add node {node_id}: {e}")

    async def add_edge(self, source: str, target: str, relation: str, properties: Dict[str, Any] = None):
        """Add an edge between two nodes"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO graph_edges (source, target, relation, properties)
                    VALUES (?, ?, ?, ?)
                """, (source, target, relation, json.dumps(properties or {})))
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to add edge {source} -> {target}: {e}")

    async def get_related(self, node_id: str, relation: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get nodes related to the given node"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                sql = "SELECT target, relation, properties FROM graph_edges WHERE source = ?"
                params = [node_id]
                
                if relation:
                    sql += " AND relation = ?"
                    params.append(relation)
                    
                async with db.execute(sql, params) as cursor:
                    rows = await cursor.fetchall()
                    results = []
                    for row in rows:
                        data = dict(row)
                        if data["properties"]:
                            data["properties"] = json.loads(data["properties"])
                        results.append(data)
                    return results
        except Exception as e:
            logger.error(f"Failed to get relations for {node_id}: {e}")
            return []
