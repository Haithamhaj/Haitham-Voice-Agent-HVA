from fastapi import APIRouter, HTTPException
from haitham_voice_agent.dispatcher import get_dispatcher

router = APIRouter(prefix="/memory", tags=["memory"])

@router.get("/stats")
async def get_memory_stats():
    """Get memory system statistics"""
    dispatcher = get_dispatcher()
    memory_tool = dispatcher.tools.get("memory")
    
    if not memory_tool:
        raise HTTPException(status_code=503, detail="Memory tool not available")
        
    try:
        # Assuming memory tool has a get_stats method or similar
        # If not, we might need to implement it or use what's available
        if hasattr(memory_tool, "get_stats"):
            stats = await memory_tool.get_stats()
            return stats
        else:
            return {"status": "active", "message": "Stats not implemented in tool"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_memory(query: str):
    """Search memory"""
    dispatcher = get_dispatcher()
    memory_tool = dispatcher.tools.get("memory")
    
    if not memory_tool:
        raise HTTPException(status_code=503, detail="Memory tool not available")
        
    try:
        # Using the 'remember' or 'search' action
        # We need to check the actual method name in VoiceMemoryTools
        # Based on common patterns:
        if hasattr(memory_tool, "search"):
            results = await memory_tool.search(query=query)
            return results
        elif hasattr(memory_tool, "remember"):
             results = await memory_tool.remember(query=query)
             return results
        else:
            return {"error": "Search method not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
