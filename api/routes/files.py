from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import logging
from pathlib import Path

from haitham_voice_agent.tools.memory.voice_tools import VoiceMemoryTools
from haitham_voice_agent.tools.projects import project_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class ScanRequest(BaseModel):
    paths: List[str]

class IngestRequest(BaseModel):
    path: str
    project_id: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None

@router.post("/scan")
async def scan_files(request: ScanRequest):
    """Scan paths for files related to critical projects"""
    memory_tools = VoiceMemoryTools()
    await memory_tools.ensure_initialized()
    
    results = []
    for path_str in request.paths:
        path = Path(path_str)
        if not path.exists():
            continue
            
        if path.is_file():
            suggestion = await memory_tools.memory_system.suggest_file_project(str(path))
            if suggestion:
                results.append(suggestion)
        elif path.is_dir():
            # Shallow scan of directory
            for item in path.glob("*"):
                if item.is_file():
                    suggestion = await memory_tools.memory_system.suggest_file_project(str(item))
                    if suggestion:
                        results.append(suggestion)
                        
    return {"results": results}

@router.post("/ingest")
async def ingest_file(request: IngestRequest):
    """Ingest a file into the 3-layer memory system"""
    memory_tools = VoiceMemoryTools()
    await memory_tools.ensure_initialized()
    
    success = await memory_tools.memory_system.ingest_file(
        path=request.path,
        project_id=request.project_id,
        description=request.description,
        tags=request.tags
    )
    
    if success:
        return {"status": "success", "message": f"File ingested into project {request.project_id}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to ingest file")
