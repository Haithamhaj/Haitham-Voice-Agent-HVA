import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class QuickIndexer:
    """
    Layer 2: Quick Access Index
    Cache contents of key folders and recent files.
    """
    
    def __init__(self, storage_path: str = "~/HVA_Memory/system/quick_index.json"):
        self.storage_path = Path(storage_path).expanduser()
        self.index = {
            "desktop": [],
            "downloads": [],
            "documents": [],
            "recent_files": [],
            "favorites": [],
            "last_updated": None
        }
        self.max_items_per_folder = 50
        
    def update_index(self) -> Dict[str, Any]:
        """Update the quick index"""
        logger.info("Updating Quick Index (Layer 2)...")
        
        home = Path.home()
        
        self.index["desktop"] = self._index_folder(home / "Desktop")
        self.index["downloads"] = self._index_folder(home / "Downloads")
        self.index["documents"] = self._index_folder(home / "Documents")
        self.index["recent_files"] = self._get_recent_files()
        self.index["last_updated"] = datetime.now().isoformat()
        
        self._save_index()
        return self.index
        
    def _index_folder(self, path: Path) -> List[Dict[str, Any]]:
        """List files in a folder (non-recursive, top-level only)"""
        items = []
        if not path.exists():
            return items
            
        try:
            # Sort by modification time (newest first)
            entries = sorted(path.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
            
            for entry in entries[:self.max_items_per_folder]:
                # Strict Noise Filtering
                if entry.name.startswith('.'): continue
                if entry.name in [".DS_Store", "__pycache__", "Icon\r"]: continue
                if entry.suffix in [".app", ".localized"]: continue # Skip apps in docs/downloads usually
                
                items.append({
                    "name": entry.name,
                    "path": str(entry),
                    "type": "folder" if entry.is_dir() else "file",
                    "size": self._format_size(entry.stat().st_size) if entry.is_file() else "-",
                    "modified": datetime.fromtimestamp(entry.stat().st_mtime).strftime("%Y-%m-%d")
                })
        except Exception as e:
            logger.warning(f"Error indexing {path}: {e}")
            
        return items
        
    def _get_recent_files(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently modified files using mdfind"""
        items = []
        try:
            # Find files modified in the last 24 hours, excluding Library and hidden files
            cmd = [
                "mdfind",
                'kMDItemContentModificationDate > $time.now(-1d) && kMDItemContentType != "public.folder"'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            paths = result.stdout.strip().split('\n')
            
            # Filter and process
            count = 0
            for p_str in paths:
                if not p_str: continue
                
                p = Path(p_str)
                # Exclude system files
                if "Library" in p.parts or p.name.startswith('.'):
                    continue
                    
                if p.exists():
                    items.append({
                        "name": p.name,
                        "path": str(p),
                        "modified": datetime.fromtimestamp(p.stat().st_mtime).strftime("%H:%M")
                    })
                    count += 1
                    if count >= limit:
                        break
                        
        except Exception as e:
            logger.warning(f"Error getting recent files: {e}")
            
        return items
        
    def _format_size(self, size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def _save_index(self):
        """Save index to disk"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save quick index: {e}")

    def load_index(self):
        """Load index from disk"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load quick index: {e}")

    def find_in_index(self, query: str) -> List[Dict[str, Any]]:
        """Search in the quick index"""
        results = []
        query = query.lower()
        
        # Helper to search a list
        def search_list(lst, source):
            for item in lst:
                if query in item["name"].lower():
                    item["source"] = source
                    results.append(item)
                    
        search_list(self.index.get("desktop", []), "Desktop")
        search_list(self.index.get("downloads", []), "Downloads")
        search_list(self.index.get("documents", []), "Documents")
        search_list(self.index.get("recent_files", []), "Recent")
        
        return results
