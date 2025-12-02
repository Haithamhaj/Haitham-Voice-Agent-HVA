from fastapi import APIRouter, HTTPException
from haitham_voice_agent.dispatcher import get_dispatcher

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/status")
async def get_system_status():
    """Get system status"""
    dispatcher = get_dispatcher()
    system_tool = dispatcher.tools.get("system")
    
    if not system_tool:
        raise HTTPException(status_code=503, detail="System tool not available")
        
    try:
        if hasattr(system_tool, "get_status"):
            status = await system_tool.get_status()
            return status
        else:
            return {"status": "online", "message": "System tool active"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
