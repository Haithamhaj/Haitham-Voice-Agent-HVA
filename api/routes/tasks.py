from fastapi import APIRouter, HTTPException
from haitham_voice_agent.dispatcher import get_dispatcher

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/")
async def get_tasks():
    """Get all tasks"""
    dispatcher = get_dispatcher()
    task_tool = dispatcher.tools.get("tasks")
    
    if not task_tool:
        raise HTTPException(status_code=503, detail="Task tool not available")
        
    try:
        if hasattr(task_tool, "list_tasks"):
            tasks = await task_tool.list_tasks()
            return tasks
        else:
            return {"error": "Method not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
