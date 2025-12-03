from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from haitham_voice_agent.tools.files import FileTools
import logging

router = APIRouter(prefix="/files", tags=["files"])
logger = logging.getLogger(__name__)
file_tools = FileTools()

class OpenFileRequest(BaseModel):
    path: str

@router.post("/open")
async def open_file(request: OpenFileRequest):
    """Open a file or directory"""
    result = await file_tools.open_file(request.path)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["message"])
    return result
