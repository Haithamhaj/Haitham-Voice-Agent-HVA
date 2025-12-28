from fastapi import APIRouter, HTTPException, BackgroundTasks, File, UploadFile
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import shutil
import os
from pathlib import Path

from haitham_voice_agent.tools.memory.memory_system import memory_system
from haitham_voice_agent.intelligence.smart_summarizer import smart_summarizer
from haitham_voice_agent.intelligence.knowledge_graph_builder import knowledge_graph_builder
from haitham_voice_agent.intelligence.deep_dive_generator import deep_dive_generator
from haitham_voice_agent.tools.workspace_manager import workspace_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class KnowledgeRequest(BaseModel):
    path: str
    project_id: Optional[str] = None

class PodcastRequest(BaseModel):
    path: str
    host_name: str = "Sarah"
    guest_name: str = "Mike"

@router.get("/files")
async def list_knowledge_files(project_id: Optional[str] = None):
    """List files that can be analyzed"""
    try:
        # Use MemorySystem to search for all files or specific project
        # Ideally we'd have a list_files method, but search works
        results = await memory_system.search_files("", project_id=project_id, limit=50)
        return {"files": results}
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_knowledge_file(
    file: UploadFile = File(...), 
    project_id: str = "general"
):
    """Upload and Ingest a new file"""
    try:
        # Save file to disk (Inbox)
        inbox_dir = workspace_manager.get_inbox_path()
        file_path = inbox_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"File uploaded to {file_path}")
        
        # Ingest (builds tree & summary automatically)
        await memory_system.ingest_file(
            path=str(file_path),
            project_id=project_id,
            description=f"Uploaded via Knowledge Studio",
            tags=["uploaded"]
        )
        
        return {"status": "success", "path": str(file_path)}
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tree")
async def build_knowledge_tree(req: KnowledgeRequest):
    """Get or Build the Knowledge Tree for a file"""
    try:
        # 1. Check if nodes exist
        # For now, we'll just re-build or fetch.
        # Ideally we'd have a 'get_tree' method in GraphStore.
        # Let's extract relations from GraphStore
        
        # We need the ID used in graph store, which is usually the path
        relations = await memory_system.graph_store.get_related(req.path)
        
        if not relations:
            # Trigger build
            logger.info("Tree not found, building...")
            # We need content.
            # Assuming file is on disk
            from haitham_voice_agent.intelligence.content_extractor import content_extractor
            content = content_extractor.extract_text(req.path)
            
            if content:
                await knowledge_graph_builder.build_document_tree(req.path, content, req.path.split('/')[-1])
                relations = await memory_system.graph_store.get_related(req.path)
            else:
                return {"error": "Content not found"}
                
        # Format for UI D3.js (Node/Links)
        topics = [r for r in relations if r['relation'] == 'has_topic']
        
        return {
            "root": req.path.split('/')[-1],
            "topics": topics,
            "raw_relations": relations
        }
    except Exception as e:
        logger.error(f"Tree error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/podcast")
async def generate_podcast(req: PodcastRequest):
    """Generate a Deep Dive Podcast Script"""
    try:
        # Get Content
        from haitham_voice_agent.intelligence.content_extractor import content_extractor
        content = content_extractor.extract_text(req.path)
        
        if not content:
            raise HTTPException(status_code=404, detail="File content not found")
            
        # Update names
        deep_dive_generator.host_name = req.host_name
        deep_dive_generator.guest_name = req.guest_name
        
        # Generate
        result = await deep_dive_generator.generate_script(content, title=req.path.split('/')[-1])
        return result
        
    except Exception as e:
        logger.error(f"Podcast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summary")
async def recursive_summary(req: KnowledgeRequest):
    """Generate Deep Recursive Summary"""
    try:
        # Get Content
        from haitham_voice_agent.intelligence.content_extractor import content_extractor
        content = content_extractor.extract_text(req.path)
        
        if not content:
            raise HTTPException(status_code=404, detail="File content not found")
            
        # Generate
        result = await smart_summarizer.recursive_summarize(content)
        return result
        
    except Exception as e:
        logger.error(f"Summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
