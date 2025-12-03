from fastapi import APIRouter, HTTPException
from haitham_voice_agent.tools.voice.stt import STTHandler
from haitham_voice_agent.dispatcher import get_dispatcher
import logging

router = APIRouter(prefix="/voice", tags=["voice"])
logger = logging.getLogger(__name__)

# Global STT Handler instance
# We might want to move this to a dependency injection or a global state manager
stt_handler = STTHandler()

from api.connection_manager import manager

@router.post("/start")
async def start_listening():
    """Start voice listening"""
    try:
        logger.info("Starting voice listening...")
        await manager.broadcast({"type": "status", "listening": True})
        
        # This might block, so we should probably run it in a thread or background task
        # But for now, let's just await it.
        # Ideally, STTHandler should have a callback for partial results to stream back.
        
        from fastapi.concurrency import run_in_threadpool
        result = await run_in_threadpool(stt_handler.listen_realtime)
        
        await manager.broadcast({"type": "status", "listening": False})
        return {"status": "success", "transcript": result}
    except Exception as e:
        logger.error(f"Error in start_listening: {e}")
        await manager.broadcast({"type": "status", "listening": False})
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_listening():
    """Stop voice listening"""
    # Force update status to False
    await manager.broadcast({"type": "status", "listening": False})
    return {"status": "stopped"}
