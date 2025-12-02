from fastapi import APIRouter, HTTPException
from haitham_voice_agent.tools.voice.stt import STTHandler
from haitham_voice_agent.dispatcher import get_dispatcher
import logging

router = APIRouter(prefix="/voice", tags=["voice"])
logger = logging.getLogger(__name__)

# Global STT Handler instance
# We might want to move this to a dependency injection or a global state manager
stt_handler = STTHandler()

@router.post("/start")
async def start_listening():
    """Start voice listening"""
    try:
        # In a real scenario, this might be a long-running process or trigger a background task
        # For now, we'll just simulate the listening start
        # You might want to use WebSocket for streaming audio or status updates
        
        # Note: The actual STT loop is usually blocking or runs in a separate thread/process
        # Here we just trigger a single listen for demonstration or command input
        
        logger.info("Starting voice listening...")
        result = await stt_handler.listen()
        return {"status": "success", "transcript": result}
    except Exception as e:
        logger.error(f"Error in start_listening: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_listening():
    """Stop voice listening"""
    # This would signal the STT loop to stop
    return {"status": "stopped"}
