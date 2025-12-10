import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path

from haitham_voice_agent.domain.models import Task, TaskStatus
from haitham_voice_agent.tools.workspace_manager import workspace_manager

logger = logging.getLogger(__name__)

class TaskManager:
    """
    Manages tasks using local JSON files in the workspace.
    """
    
    def __init__(self, user_id: str = "haitham-local"):
        self.user_id = user_id
        
    def _load_tasks(self, project_id: str) -> List[Task]:
        """Load tasks from a project's tasks.json"""
        file_path = workspace_manager.project_tasks_file(project_id)
        if not file_path.exists():
            return []
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Task.from_dict(t) for t in data]
        except Exception as e:
            logger.error(f"Failed to load tasks for {project_id}: {e}")
            return []
            
    def _save_tasks(self, project_id: str, tasks: List[Task]):
        """Save tasks to a project's tasks.json"""
        file_path = workspace_manager.project_tasks_file(project_id)
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([t.to_dict() for t in tasks], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save tasks for {project_id}: {e}")

    def create_task(self, title: str, 
                    project_id: str = "inbox",
                    description: str = "",
                    due_date: Any = None,
                    language: str = "ar") -> Task:
        """Create a new task"""
        now = datetime.now().isoformat()
        
        # Safe strict due_date handling
        final_due_date = None
        if due_date:
            if isinstance(due_date, datetime):
                final_due_date = due_date.isoformat()
            elif isinstance(due_date, str):
                final_due_date = due_date # Assume ISO or handle parsing if needed later
        
        task = Task(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            project_id=project_id,
            title=title,
            description=description,
            status="open",
            created_at=now,
            updated_at=now,
            language=language,
            due_date=final_due_date
        )
        
        tasks = self._load_tasks(project_id)
        tasks.append(task)
        self._save_tasks(project_id, tasks)
        
        logger.info(f"Created task: {title} in {project_id}")
        return task

    def delete_task(self, task_id: str, project_id: str = "inbox") -> bool:
        """Delete a task by ID"""
        tasks = self._load_tasks(project_id)
        original_count = len(tasks)
        
        tasks = [t for t in tasks if t.id != task_id]
        
        if len(tasks) < original_count:
            self._save_tasks(project_id, tasks)
            logger.info(f"Deleted task {task_id} from {project_id}")
            return True
            
        # If not found in primary project, try searching others?
        # For now, strict project scoping
        return False

    def list_tasks(self, project_id: Optional[str] = None, 
                   status: Optional[TaskStatus] = None) -> List[Task]:
        """List tasks, optionally filtered by project and status"""
        all_tasks = []
        
        if project_id:
            all_tasks = self._load_tasks(project_id)
        else:
            # Scan all projects (simplified: just check inbox and known projects)
            # For now, let's just check inbox and iterate over projects dir
            projects_dir = workspace_manager.projects_root
            project_ids = ["inbox"] + [d.name for d in projects_dir.iterdir() if d.is_dir()]
            
            for pid in project_ids:
                all_tasks.extend(self._load_tasks(pid))
                
        if status:
            all_tasks = [t for t in all_tasks if t.status == status]
            
        return all_tasks

    def update_task(self, task_id: str, project_id: str, **updates) -> Optional[Task]:
        """Update a task"""
        tasks = self._load_tasks(project_id)
        for i, task in enumerate(tasks):
            if task.id == task_id:
                # Apply updates
                task_dict = task.to_dict()
                task_dict.update(updates)
                task_dict["updated_at"] = datetime.now().isoformat()
                
                updated_task = Task.from_dict(task_dict)
                tasks[i] = updated_task
                self._save_tasks(project_id, tasks)
                return updated_task
                
        return None

    def complete_task(self, task_id: str, project_id: str) -> Optional[Task]:
        """Mark a task as completed"""
        return self.update_task(task_id, project_id, status="completed")

    def delete_task(self, task_id: str, project_id: str) -> bool:
        """Delete a task"""
        tasks = self._load_tasks(project_id)
        initial_len = len(tasks)
        tasks = [t for t in tasks if t.id != task_id]
        
        if len(tasks) < initial_len:
            self._save_tasks(project_id, tasks)
            return True
        return False

    # Aliases
    add_task = create_task

# Singleton
task_manager = TaskManager()
