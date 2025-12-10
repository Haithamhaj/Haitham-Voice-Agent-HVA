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

        # Use ConnectionManager's search_emails method
        # Filter for Primary category only to avoid spam/promotions
        result = await gmail_tool.search_emails(query="is:unread category:primary", limit=20)
        
        if result.get("error"):
            return result
            
        return {
            "count": result.get("count", 0),
            "messages": result.get("emails", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
