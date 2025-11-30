import subprocess
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DeepSearch:
    """
    Layer 3: Deep Search
    Use macOS Spotlight (mdfind) for real-time search.
    No storage/caching.
    """
    
    def search(self, query: str, limit: int = 20, only_in: str = None) -> List[Dict[str, Any]]:
        """
        Execute Spotlight search
        
        Args:
            query: Search term
            limit: Max results
            only_in: Limit search to specific directory
            
        Returns:
            List of found files with details
        """
        logger.info(f"Deep Search (Layer 3) for: '{query}'")
        
        results = []
        try:
            cmd = ["mdfind"]
            
            if only_in:
                cmd.extend(["-onlyin", only_in])
                
            # Construct query
            # We search for name match OR content match
            # "kMDItemDisplayName == '*query*'c" is case-insensitive name match
            # But mdfind default is broad. Let's stick to default for now, or refine if needed.
            # Default mdfind searches everything.
            cmd.append(query)
            
            process = subprocess.run(cmd, capture_output=True, text=True)
            paths = process.stdout.strip().split('\n')
            
            count = 0
            for p_str in paths:
                if not p_str: continue
                
                p = Path(p_str)
                
                # Filter out system/hidden files
                if "Library" in p.parts or p.name.startswith('.'):
                    continue
                    
                if p.exists():
                    results.append({
                        "name": p.name,
                        "path": str(p),
                        "type": "folder" if p.is_dir() else "file",
                        "size": self._get_size(p)
                    })
                    count += 1
                    if count >= limit:
                        break
                        
        except Exception as e:
            logger.error(f"Deep search failed: {e}")
            
        return results

    def _get_size(self, path: Path) -> str:
        try:
            if path.is_file():
                size = path.stat().st_size
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024:
                        return f"{size:.1f} {unit}"
                    size /= 1024
                return f"{size:.1f} TB"
        except:
            pass
        return "-"
