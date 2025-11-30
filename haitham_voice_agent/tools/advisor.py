import logging
import psutil
import datetime
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

from haitham_voice_agent.memory.manager import get_memory_manager

class Advisor:
    """
    Honest Advisor Module
    Handles Resource Monitoring, Digital Wellbeing, and Safety Checks.
    """
    
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.last_resource_check = datetime.datetime.now()
        self.resource_check_interval = 300 # 5 minutes
        self.memory = get_memory_manager()
        
        # Safety Config
        self.protected_paths = [
            Path.home() / "Documents",
            Path.home() / "Desktop",
            Path.home() / "Pictures",
            Path.home() / "HVA_Workspace"
        ]
        
    def check_resources(self) -> Optional[str]:
        """
        Check system resources and return warning if high.
        """
        now = datetime.datetime.now()
        if (now - self.last_resource_check).total_seconds() < 60:
            # Don't check too often to save resources itself
            return None
            
        self.last_resource_check = now
        
        # Check Memory
        mem = psutil.virtual_memory()
        if mem.percent > 85:
            # Find memory hog
            hog = self._find_memory_hog()
            return f"⚠️ **High Memory Usage**\nRAM is at {mem.percent}%.\nTop consumer: {hog}"
            
        # Check CPU (blocking call, so use interval=None or 0.1)
        cpu = psutil.cpu_percent(interval=0.1)
        if cpu > 90:
            return f"⚠️ **High CPU Usage**\nProcessor is at {cpu}%."
            
        return None

    def check_wellbeing(self) -> Optional[str]:
        """
        Check session duration and suggest breaks.
        """
        now = datetime.datetime.now()
        duration = now - self.start_time
        
        # Check every hour roughly (logic can be refined)
        hours = duration.total_seconds() / 3600
        
        if hours > 2 and hours < 2.1: # Trigger once around 2 hours
            return "🧘 **Health Tip**\nYou've been active for over 2 hours.\nHow about a short break? ☕️"
            
        if hours > 4 and hours < 4.1:
            return "🧘 **Health Tip**\n4 hours straight! Your eyes need rest.\nPlease take a walk. 🚶"
            
        return None

    def validate_action(self, tool: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate critical actions before execution.
        Returns: {"safe": bool, "warning": str}
        """
        if tool == "files" and action == "delete_folder":
            path_str = params.get("path") or params.get("directory")
            if not path_str:
                return {"safe": True}
                
            # Resolve path (simple version)
            path = Path(path_str.replace("~", str(Path.home())))
            
            # Check if protected
            for protected in self.protected_paths:
                if path == protected or protected in path.parents:
                    # It is a protected folder or inside one? 
                    # Actually, deleting a subfolder in Documents is fine.
                    # Deleting Documents ITSELF is bad.
                     if path == protected:
                         warning_msg = f"🛑 **Safety Alert**\nYou are trying to delete a protected system folder: `{path.name}`.\nI cannot allow this."
                         # Log to memory
                         self.memory.save_thought(f"Safety Violation Attempt: User tried to delete {path.name}", tags=["safety", "violation"])
                         return {
                             "safe": False, 
                             "warning": warning_msg
                         }
            
            # Check if path doesn't exist
            if not path.exists():
                 return {"safe": False, "warning": f"Path not found: {path}"}
                 
        return {"safe": True}

    def _find_memory_hog(self) -> str:
        """Find the process consuming most memory"""
        try:
            processes = []
            for proc in psutil.process_iter(['name', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if not processes:
                return "Unknown"
                
            hog = max(processes, key=lambda p: p['memory_percent'])
            return f"{hog['name']} ({hog['memory_percent']:.1f}%)"
        except Exception:
            return "Unknown"

# Singleton
_advisor = None

def get_advisor():
    global _advisor
    if _advisor is None:
        _advisor = Advisor()
    return _advisor
