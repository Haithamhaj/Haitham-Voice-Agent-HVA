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
        # Use memory_system directly for structured results
        from haitham_voice_agent.tools.memory.memory_system import memory_system
        
        # Ensure initialized
        await memory_system.initialize()
        
        # Search Memories (Notes, Thoughts)
        memories = await memory_system.search_memories(query=query, limit=20)
        
        # Search Files (Indexed Documents)
        files = await memory_system.search_files(query=query, limit=50)
        
        # Format results for frontend
        formatted_results = []
        
        # Add Memories
        for mem in memories:
            formatted_results.append({
                "id": mem.id,
                "content": mem.ultra_brief or mem.raw_content[:200],
                "text": mem.raw_content,
                "type": mem.type.value if hasattr(mem.type, "value") else str(mem.type),
                "project": mem.project,
                "timestamp": mem.timestamp.isoformat() if hasattr(mem.timestamp, "isoformat") else str(mem.timestamp),
                "metadata": {
                    "type": mem.type.value if hasattr(mem.type, "value") else str(mem.type),
                    "project": mem.project,
                    "source": "memory"
                }
            })
            
        # Add Files
        for f in files:
            formatted_results.append({
                "id": f.get("path"), # Use path as ID for files
                "content": f.get("description") or f.get("path"),
                "text": f.get("description", ""),
                "type": "file",
                "project": f.get("project_id", "Unknown"),
                "timestamp": f.get("last_modified", ""),
                "score": f.get("score", 0),
                "metadata": {
                    "type": "file",
                    "project": f.get("project_id"),
                    "path": f.get("path"),
                    "source": "file_index"
                }
            })
            
        # Sort by score/relevance (if available) or just mix them
        # For now, just return combined list
        return formatted_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
