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
    logger.info("Initializing Memory System...")
    await memory_system.initialize()
    logger.info("Memory System Initialized")

@app.get("/")
async def root():
    return {"message": "HVA API is running"}

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

from api.routes import voice, memory, gmail, calendar, tasks, system, chat, files, usage, checkpoints

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
app.include_router(checkpoints.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
