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
            tasks = task_tool.list_tasks()
            return tasks
        else:
            return {"error": "Method not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    dispatcher = get_dispatcher()
    task_tool = dispatcher.tools.get("tasks")
    
    if not task_tool:
        raise HTTPException(status_code=503, detail="Task tool not available")
        
    try:
        # We assume inbox for now, or we could look it up
        # The TaskManager.delete_task handles project_id="inbox" default
        success = task_tool.delete_task(task_id)
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
