import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from haitham_voice_agent.tools.workspace_manager import workspace_manager

logger = logging.getLogger(__name__)

class ProjectManager:
    """
    Manages the Project Registry.
    Stores project metadata in projects.json.
    """
    
    def __init__(self):
        self.registry_file = workspace_manager.root / "projects.json"
        self._ensure_registry()
        
    def _ensure_registry(self):
        if not self.registry_file.exists():
            self._save_registry({"projects": []})
            
    def _load_registry(self) -> Dict[str, Any]:
        try:
            return json.loads(self.registry_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Failed to load project registry: {e}")
            return {"projects": []}
            
    def _save_registry(self, data: Dict[str, Any]):
        self.registry_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        
    async def create_project(self, name: str, description: str = "", tags: List[str] = None, is_critical: bool = False, auto_index_mode: str = "off") -> Dict[str, Any]:
        """Create a new project"""
        registry = self._load_registry()
        
        # Check for duplicates
        slug = workspace_manager._sanitize_filename(name)
        for p in registry["projects"]:
            if p["id"] == slug:
                return {"success": False, "message": f"Project '{name}' already exists (ID: {slug})"}
                
        project_id = slug
        now = datetime.now().isoformat()
        
        new_project = {
            "id": project_id,
            "name": name,
            "description": description,
            "tags": tags or [],
            "status": "active",
            "created_at": now,
            "updated_at": now,
            "path": str(workspace_manager.get_project_folder(project_id)),
            "is_critical": is_critical,
            "auto_index_mode": auto_index_mode, # off, ask, auto
            "watched_folders": []
        }
        
        registry["projects"].append(new_project)
        self._save_registry(registry)
        
        # Ensure folder structure
        workspace_manager.ensure_project_structure(project_id, name)
        
        return {"success": True, "message": f"Created project: {name}", "project": new_project}
        
    async def list_projects(self, status: str = "active") -> Dict[str, Any]:
        """List projects by status"""
        registry = self._load_registry()
        projects = [p for p in registry["projects"] if status == "all" or p.get("status") == status]
        return {"success": True, "projects": projects, "count": len(projects)}

    async def list_critical_projects(self) -> List[Dict[str, Any]]:
        """List critical projects"""
        registry = self._load_registry()
        return [p for p in registry["projects"] if p.get("is_critical", False)]
        
    async def get_project(self, name_or_id: str) -> Dict[str, Any]:
        """Get project details"""
        registry = self._load_registry()
        target = name_or_id.lower()
        
        for p in registry["projects"]:
            if p["id"] == target or p["name"].lower() == target:
                return {"success": True, "project": p}
                
        return {"success": False, "message": "Project not found"}

# Singleton
project_manager = ProjectManager()
