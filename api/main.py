from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HVA_API")

# Add project root to path to allow importing haitham_voice_agent
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

app = FastAPI(title="HVA API", version="2.0")

# CORS for Electron (and local development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, we might want to restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.connection_manager import manager
from haitham_voice_agent.tools.memory.memory_system import memory_system

@app.on_event("startup")
async def startup_event():
    logger.info("Starting HVA API...")
    # Initialize tools
    from haitham_voice_agent.tools.memory.voice_tools import VoiceMemoryTools
    await VoiceMemoryTools().ensure_initialized()
    
    # Start Adaptive Sync (Background)
    from haitham_voice_agent.intelligence.adaptive_sync import AdaptiveSync
    import asyncio
    asyncio.create_task(AdaptiveSync().sync_knowledge_base())
    logger.info("Memory System Initialized")
    
    # Start Guardian (Background)
    from haitham_voice_agent.intelligence.guardian import SystemGuardian
    guardian = SystemGuardian()
    asyncio.create_task(guardian.start_monitoring())
    logger.info("Guardian Initialized")



@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "HVA API"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

from api.routes import voice, memory, gmail, calendar, tasks, system, chat, files, usage, checkpoints, finetune, knowledge

# Include routers
app.include_router(voice.router)
app.include_router(chat.router)
app.include_router(memory.router)
app.include_router(gmail.router)
app.include_router(calendar.router)
app.include_router(tasks.router)
app.include_router(system.router)
app.include_router(files.router, prefix="/files", tags=["files"])
app.include_router(usage.router)
app.include_router(usage.router)
app.include_router(checkpoints.router)
app.include_router(finetune.router)
app.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])

# Mount Static Files (Frontend)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Path to the built frontend
frontend_path = project_root / "desktop" / "dist_renderer"

if frontend_path.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Allow API routes to pass through (already handled above)
        if full_path.startswith("api/") or full_path.startswith("ws"):
            return None # Should be handled by other routes
            
        # Serve index.html for SPA routing
        if "." not in full_path:
            return FileResponse(str(frontend_path / "index.html"))
            
        # Serve specific file if exists
        file_path = frontend_path / full_path
        if file_path.exists():
            return FileResponse(str(file_path))
        
        # Fallback to index.html
        return FileResponse(str(frontend_path / "index.html"))
else:
    logger.warning(f"Frontend build not found at {frontend_path}. Run 'npm run build' in desktop/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
