import logging
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional

from .system_profiler import SystemProfiler
from .quick_indexer import QuickIndexer
from .deep_search import DeepSearch
from .file_watcher import FileWatcher

logger = logging.getLogger(__name__)

class SystemAwareness:
    """
    Main Controller for System Awareness Module.
    Orchestrates Layer 1, 2, and 3.
    """
    
    def __init__(self):
        self.profiler = SystemProfiler()
        self.indexer = QuickIndexer()
        self.searcher = DeepSearch()
        
        # Watcher for Desktop and Downloads
        self.watcher = FileWatcher(
            folders=["~/Desktop", "~/Downloads", "~/Documents"],
            callback=self._on_file_change
        )
        
        self._initialized = False
        
    def start(self):
        """Initialize and start monitoring"""
        if self._initialized: return
        
        logger.info("Starting System Awareness Module...")
        
        # Load Data Immediately (Smart Startup)
        self.profiler.load_profile()
        self.indexer.load_index()
        
        # Start Background Updates
        threading.Thread(target=self.profiler.run_profile, daemon=True).start()
        
        if not self.indexer.index.get("last_updated"):
            threading.Thread(target=self.indexer.update_index, daemon=True).start()
            
        # Start Watcher
        self.watcher.start()
        
        self._initialized = True
        
    def _on_file_change(self):
        """Callback when files change"""
        logger.info("File change detected. Updating Quick Index...")
        # Run update in background thread to not block watcher
        threading.Thread(target=self.indexer.update_index, daemon=True).start()
        
    def find_file(self, query: str) -> List[Dict[str, Any]]:
        """
        Smart Find with Fuzzy Matching:
        1. Check Quick Index (Layer 2)
        2. If not found, use Deep Search (Layer 3)
        """
        # 1. Quick Index (Fuzzy)
        results = self.indexer.find_in_index(query)
        if results:
            logger.info(f"Found '{query}' in Quick Index ({len(results)} results)")
            return results
            
        # 2. Deep Search
        logger.info(f"'{query}' not in Quick Index. Trying Deep Search...")
        return self.searcher.search(query)
        
    def get_app_path(self, app_name: str) -> Optional[str]:
        """Get app path from Layer 1 with Fuzzy Matching"""
        if not self.profiler.profile:
            self.profiler.load_profile()
            
        apps = self.profiler.profile.get("apps", [])
        query = app_name.lower().strip()
        
        # 1. Exact Match
        for app in apps:
            if app["name"].lower() == query:
                return app["path"]
                
        # 2. Substring Match (Fuzzy)
        # "code" -> "Visual Studio Code"
        # "chrome" -> "Google Chrome"
        for app in apps:
            if query in app["name"].lower():
                return app["path"]
                
        return None
        
    def get_recent_files(self) -> List[Dict[str, Any]]:
        """Get recent files from Layer 2"""
        return self.indexer.index.get("recent_files", [])
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get combined system status"""
        return {
            "storage": self.profiler.profile.get("storage", {}),
            "device": self.profiler.profile.get("device", {}),
            "index_status": {
                "last_updated": self.indexer.index.get("last_updated"),
                "desktop_files": len(self.indexer.index.get("desktop", [])),
                "downloads_files": len(self.indexer.index.get("downloads", []))
            }
        }

# Singleton
_instance = None

def get_system_awareness() -> SystemAwareness:
    global _instance
    if not _instance:
        _instance = SystemAwareness()
    return _instance
