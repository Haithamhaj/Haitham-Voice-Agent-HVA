from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional, List
import logging

from haitham_voice_agent.tools.memory.memory_system import memory_system

router = APIRouter(prefix="/usage", tags=["usage"])
logger = logging.getLogger(__name__)

@router.get("/stats")
async def get_usage_stats(days: int = Query(30, description="Number of days to look back")) -> Dict[str, Any]:
    """
    Get token usage statistics and cost.
    """
    try:
        if not memory_system.sqlite_store:
            raise HTTPException(status_code=503, detail="Database not initialized")
            
        stats = await memory_system.sqlite_store.get_token_usage_stats(days=days)
        return stats
    except Exception as e:
        logger.error(f"Error fetching usage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_usage_logs(limit: int = Query(50, description="Number of logs to fetch")) -> List[Dict[str, Any]]:
    """
    Get raw token usage logs.
    """
    try:
        if not memory_system.sqlite_store:
            raise HTTPException(status_code=503, detail="Database not initialized")
            
        logs = await memory_system.sqlite_store.get_token_usage_logs(limit=limit)
        return logs
    except Exception as e:
        logger.error(f"Error fetching usage logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
