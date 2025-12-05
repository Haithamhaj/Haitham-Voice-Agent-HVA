from fastapi import APIRouter, HTTPException
import sqlite3
import json
import logging
from typing import List, Dict, Any

router = APIRouter(prefix="/checkpoints", tags=["checkpoints"])
logger = logging.getLogger(__name__)

DB_PATH = "/Users/haitham/.hva/memory/hva_memory.db"

@router.get("/")
async def get_checkpoints(limit: int = 10):
    """Get recent system checkpoints"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'")
        if not cursor.fetchone():
            return []

        cursor.execute("""
            SELECT id, timestamp, action_type, description, data 
            FROM checkpoints 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        checkpoints = []
        
        for row in rows:
            data = {}
            if row["data"]:
                try:
                    data = json.loads(row["data"])
                except:
                    pass
                    
            checkpoints.append({
                "id": row["id"],
                "timestamp": row["timestamp"],
                "action_type": row["action_type"],
                "description": row["description"],
                "data": data
            })
            
        conn.close()
        return checkpoints
        
    except Exception as e:
        logger.error(f"Error fetching checkpoints: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{checkpoint_id}/rollback")
async def rollback_checkpoint(checkpoint_id: str):
    """Rollback a specific checkpoint"""
    try:
        from haitham_voice_agent.tools.checkpoint_manager import get_checkpoint_manager
        cm = get_checkpoint_manager()
        
        report = await cm.rollback_checkpoint(checkpoint_id)
        return report
        
    except Exception as e:
        logger.error(f"Error rolling back checkpoint {checkpoint_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
