import os
import re
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Default workspace root
HVA_WORKSPACE_ROOT = Path.home() / "HVA_Workspace"

class WorkspaceManager:
    """
    Manages the local filesystem workspace for HVA.
    Enforces structure:
    ~/HVA_Workspace/
      projects/
        <project_id>/
          notes/
          tasks/
          attachments/
      inbox/
        notes/
        tasks/
    """
    
    def __init__(self, root_path: Optional[Path] = None):
        self.root = root_path or HVA_WORKSPACE_ROOT
        self.projects_root = self.root / "projects"
        self.inbox_root = self.root / "inbox"
        self._ensure_root_structure()
        
    def _ensure_root_structure(self):
        """Ensure basic workspace folders exist"""
        self.root.mkdir(parents=True, exist_ok=True)
        self.projects_root.mkdir(exist_ok=True)
        self.inbox_root.mkdir(exist_ok=True)
        
        # Ensure inbox has subfolders
        (self.inbox_root / "notes").mkdir(exist_ok=True)
        (self.inbox_root / "tasks").mkdir(exist_ok=True)
        
    def get_project_folder(self, project_id: str) -> Path:
        """Get path to a project folder, creating it if needed"""
        if project_id.lower() == "inbox":
            return self.inbox_root
            
        # Sanitize project_id
        safe_id = self._sanitize_filename(project_id)
        project_path = self.projects_root / safe_id
        
        if not project_path.exists():
            self.ensure_project_structure(safe_id)
            
        return project_path
        
    def ensure_project_structure(self, project_id: str, project_name: str = ""):
        """Create standard folders for a project"""
        if project_id.lower() == "inbox":
            return
            
        safe_id = self._sanitize_filename(project_id)
        project_path = self.projects_root / safe_id
        
        project_path.mkdir(parents=True, exist_ok=True)
        (project_path / "notes").mkdir(exist_ok=True)
        (project_path / "tasks").mkdir(exist_ok=True)
        (project_path / "attachments").mkdir(exist_ok=True)
        
        # Create index.md if not exists
        index_file = project_path / "index.md"
        if not index_file.exists():
            name = project_name or safe_id.replace("_", " ").title()
            index_file.write_text(f"# {name}\n\nProject Overview\n", encoding="utf-8")
            
    def project_notes_dir(self, project_id: str) -> Path:
        return self.get_project_folder(project_id) / "notes"
        
    def project_tasks_file(self, project_id: str) -> Path:
        return self.get_project_folder(project_id) / "tasks" / "tasks.json"
        
    def project_attachments_dir(self, project_id: str) -> Path:
        # Inbox doesn't strictly have attachments in this spec, but let's allow it or map to root
        folder = self.get_project_folder(project_id)
        # If inbox, maybe we want an attachments folder there too?
        # The spec said inbox/notes and inbox/tasks. Let's add attachments to inbox too for consistency.
        if project_id.lower() == "inbox":
            (folder / "attachments").mkdir(exist_ok=True)
            return folder / "attachments"
        return folder / "attachments"

    def _sanitize_filename(self, name: str) -> str:
        """Make a string safe for filenames"""
        # Replace spaces with underscores, remove non-alphanumeric (except -_)
        s = name.lower().replace(" ", "_")
        return re.sub(r'[^\w\-]', '', s)

# Singleton instance
workspace_manager = WorkspaceManager()
