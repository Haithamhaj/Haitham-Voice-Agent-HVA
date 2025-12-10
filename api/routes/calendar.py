from fastapi import APIRouter, HTTPException
from haitham_voice_agent.dispatcher import get_dispatcher
from datetime import datetime

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/today")
async def get_today_events():
    """Get today's calendar events"""
    dispatcher = get_dispatcher()
    calendar_tool = dispatcher.tools.get("calendar")
    
    if not calendar_tool:
        raise HTTPException(status_code=503, detail="Calendar tool not available")
        
    try:
        if hasattr(calendar_tool, "get_today_events"):
            events = await calendar_tool.get_today_events()
            return events
        elif hasattr(calendar_tool, "list_events"):
             # Fallback
             events = await calendar_tool.list_events(day_str="upcoming")
             return events
        else:
            return {"error": "Method not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
