"""
File and Folder Tools (Smart User Sandbox)

Safe file operations for HVA.
Implements "Smart User Sandbox":
- Allow: User Home Directory (~/)
- Block: System Directories (/etc, /var, /Applications)
- Blacklist: Sensitive User Dirs (~/.ssh, ~/Library, ~/.bashrc)
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import getpass

logger = logging.getLogger(__name__)

class FileTools:
    """File operations with Smart Sandbox Security"""
    
    # Sensitive directories to block explicitly
    BLACKLIST_DIRS = {
        '.ssh', '.aws', '.kube', 'Library', 'Applications', 
        '.bashrc', '.zshrc', '.profile', '.env'
    }
    
    def __init__(self):
        self.home_dir = Path.home().resolve()
        logger.info(f"FileTools initialized (Sandbox: {self.home_dir})")
    
    def _validate_path(self, path_str: str) -> Optional[Path]:
        """
        Validate and resolve path.
        Returns Path object if safe, None if blocked.
        """
        if not path_str:
            return None
            
        try:
            # 1. Handle Aliases
            clean_path = path_str.strip()
            if clean_path.lower() in ["~", "home", "هيثم", "haitham"]:
                return self.home_dir
                
            # 2. Resolve Path
            # Expand user (~) and resolve absolute path
            target_path = Path(clean_path).expanduser().resolve()
            
            # 3. Sandbox Check: Must be inside User Home
            if not str(target_path).startswith(str(self.home_dir)):
                logger.warning(f"Blocked access outside home: {target_path}")
                return None
                
            # 4. Blacklist Check: Sensitive folders
            # Check if any part of the relative path is blacklisted
            try:
                rel_path = target_path.relative_to(self.home_dir)
                if any(part in self.BLACKLIST_DIRS for part in rel_path.parts):
                    logger.warning(f"Blocked sensitive path: {target_path}")
                    return None
                # Block hidden files/folders generally (except .hva or specific allowed ones)
                # Policy: Block hidden unless it's .hva or explicitly allowed?
                # For now, let's just block the explicit blacklist.
            except ValueError:
                pass # Should not happen due to check #3
                
            return target_path
            
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return None

    async def list_files(
        self,
        directory: str = None,
        folder_name: str = None,
        folder: str = None,
        pattern: Optional[str] = None,
        recursive: bool = False
    ) -> Dict[str, Any]:
        """List files in a directory (Sandboxed)"""
        try:
            # Resolve input
            raw_dir = directory or folder_name or folder or "~"
            
            # Validate
            dir_path = self._validate_path(raw_dir)
            if not dir_path:
                return {"error": True, "message": f"Access denied or invalid path: {raw_dir}"}
            
            if not dir_path.exists():
                # Try relative to home if not found
                retry_path = self._validate_path(f"~/{raw_dir}")
                if retry_path and retry_path.exists():
                    dir_path = retry_path
                else:
                    return {"error": True, "message": f"Directory not found: {raw_dir}"}

            if not dir_path.is_dir():
                return {"error": True, "message": f"Not a directory: {dir_path.name}"}
            
            # Execute List
            files = []
            scan_iter = dir_path.rglob(pattern or "*") if recursive else dir_path.glob(pattern or "*")
            
            for file_path in scan_iter:
                # Skip blacklisted
                if file_path.name in self.BLACKLIST_DIRS:
                    continue
                    
                # Get info for both files and directories
                files.append(self._get_file_info(file_path))
            
            # Format output
            file_names = [f["name"] for f in files]
            display_text = "\n".join(file_names[:10])
            if len(files) > 10:
                display_text += f"\n... and {len(files)-10} more"
            
            return {
                "success": True,
                "message": f"Found {len(files)} files in {dir_path.name}",
                "data": display_text,
                "directory": str(dir_path),
                "files": files,
                "count": len(files)
            }
            
        except Exception as e:
            return {"error": True, "message": str(e)}

    async def create_folder(self, directory: str) -> Dict[str, Any]:
        """Create a new folder (Sandboxed)"""
        try:
            dir_path = self._validate_path(directory)
            if not dir_path:
                # Try relative to home
                dir_path = self._validate_path(f"~/{directory}")
                if not dir_path:
                    return {"error": True, "message": "Access denied or invalid path"}
            
            if dir_path.exists():
                return {"error": True, "message": "Directory already exists"}
            
            dir_path.mkdir(parents=True, exist_ok=False)
            logger.info(f"Created folder: {dir_path}")
            return {"status": "created", "directory": str(dir_path)}
            
        except Exception as e:
            return {"error": True, "message": str(e)}

    async def delete_folder(self, directory: str, confirmed: bool = False) -> Dict[str, Any]:
        """Delete a folder (Sandboxed + Confirmation)"""
        if not confirmed:
            return {
                "status": "confirmation_required",
                "message": f"Are you sure you want to delete '{directory}'?",
                "command": "delete_folder",
                "risk_level": "high"
            }
            
        try:
            dir_path = self._validate_path(directory)
            if not dir_path:
                return {"error": True, "message": "Access denied or invalid path"}
            
            if not dir_path.exists():
                return {"error": True, "message": "Directory not found"}
            
            # Extra Safety: Don't delete root of home or important subdirs
            if dir_path == self.home_dir or dir_path == self.home_dir / "Downloads" or dir_path == self.home_dir / "Documents":
                 return {"error": True, "message": "Safety Block: Cannot delete core system folders."}

            shutil.rmtree(dir_path)
            logger.warning(f"Deleted folder: {dir_path}")
            return {"status": "deleted", "directory": str(dir_path)}
            
        except Exception as e:
            return {"error": True, "message": str(e)}

    async def search_files(self, directory: str, name_pattern: str, content_pattern: Optional[str] = None) -> Dict[str, Any]:
        """Search files (Sandboxed)"""
        try:
            dir_path = self._validate_path(directory)
            if not dir_path or not dir_path.exists():
                # Try relative
                dir_path = self._validate_path(f"~/{directory}")
                if not dir_path or not dir_path.exists():
                    return {"error": True, "message": "Directory not found or access denied"}
            
            matches = []
            for file_path in dir_path.rglob(name_pattern):
                if file_path.is_file():
                    # Skip blacklisted
                    if any(part in self.BLACKLIST_DIRS for part in file_path.parts):
                        continue
                        
                    file_info = self._get_file_info(file_path)
                    if content_pattern:
                        try:
                            # Limit read size for safety
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(100000) # Read first 100KB only
                                if content_pattern.lower() in content.lower():
                                    file_info["matched_content"] = True
                                    matches.append(file_info)
                        except:
                            pass
                    else:
                        matches.append(file_info)
            
            return {
                "directory": str(dir_path),
                "pattern": name_pattern,
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            return {"error": True, "message": str(e)}

    async def open_file(self, path: str) -> Dict[str, Any]:
        """Open a file or folder using system default app"""
        try:
            target_path = self._validate_path(path)
            if not target_path:
                return {"error": True, "message": "Access denied or invalid path"}
            
            if not target_path.exists():
                return {"error": True, "message": "File not found"}
                
            # Use macOS 'open' command
            import subprocess
            subprocess.run(['open', str(target_path)], check=True)
            
            return {"status": "opened", "path": str(target_path)}
            
        except Exception as e:
            return {"error": True, "message": str(e)}

    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file metadata"""
        try:
            stat = file_path.stat()
            is_dir = file_path.is_dir()
            return {
                "name": file_path.name,
                "path": str(file_path),
                "size": stat.st_size if not is_dir else 0,
                "size_human": self._format_size(stat.st_size) if not is_dir else "DIR",
                "modified": stat.st_mtime,
                "extension": file_path.suffix if not is_dir else "DIR",
                "type": "directory" if is_dir else "file"
            }
        except:
            return {"name": file_path.name, "error": "access_error"}
    
    @staticmethod
    def _format_size(size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
