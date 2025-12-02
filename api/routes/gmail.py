from fastapi import APIRouter, HTTPException
from haitham_voice_agent.dispatcher import get_dispatcher

router = APIRouter(prefix="/gmail", tags=["gmail"])

@router.get("/unread")
async def get_unread_emails():
    """Get unread emails count and preview"""
    dispatcher = get_dispatcher()
    gmail_tool = dispatcher.tools.get("gmail")
    
    if not gmail_tool:
        raise HTTPException(status_code=503, detail="Gmail tool not available")
        
    try:
        # Check available methods in ConnectionManager (gmail tool)
        if hasattr(gmail_tool, "get_unread_count"):
            unread = await gmail_tool.get_unread_count()
            return unread
        elif hasattr(gmail_tool, "list_messages"):
             # Fallback to listing unread messages
             messages = await gmail_tool.list_messages(query="is:unread", max_results=5)
             return {"count": len(messages), "messages": messages}
        else:
            return {"error": "Method not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
