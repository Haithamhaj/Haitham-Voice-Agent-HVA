"""
File and Folder Tools

Safe file operations for HVA.
Implements operations from Master SRS Section 3.4.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import fnmatch

logger = logging.getLogger(__name__)


class FileTools:
    """File and folder operations"""
    
    def __init__(self):
        logger.info("FileTools initialized")
    
    async def list_files(
        self,
        directory: str = None,
        folder_name: str = None,
        pattern: Optional[str] = None,
        recursive: bool = False
    ) -> Dict[str, Any]:
        """
        List files in a directory
        
        Args:
            directory: Directory path
            folder_name: Alias for directory
            pattern: Optional glob pattern (e.g., "*.pdf")
            recursive: Search recursively
            
        Returns:
            dict: List of files with metadata
        """
        try:
            # Handle aliases
            actual_dir = directory or folder_name
            
            # Handle "None" string from LLM
            if actual_dir == "None":
                actual_dir = None
                
            # Default to home if not specified
            if not actual_dir:
                actual_dir = "~"
                
            dir_path = Path(actual_dir).expanduser()
            
            # Smart resolution: If path doesn't exist, try relative to home
            if not dir_path.exists():
                home_path = Path.home() / actual_dir
                if home_path.exists():
                    dir_path = home_path
                    logger.info(f"Resolved '{actual_dir}' to '{dir_path}'")
            
            if not dir_path.exists():
                return {
                    "error": True,
                    "message": f"Directory not found: {actual_dir}"
                }
            
            if not dir_path.is_dir():
                return {
                    "error": True,
                    "message": f"Not a directory: {directory}"
                }
            
            files = []
            
            if recursive:
                for file_path in dir_path.rglob(pattern or "*"):
                    if file_path.is_file():
                        files.append(self._get_file_info(file_path))
            else:
                for file_path in dir_path.glob(pattern or "*"):
                    if file_path.is_file():
                        files.append(self._get_file_info(file_path))
            
            logger.info(f"Listed {len(files)} files in {directory}")
            
            return {
                "directory": str(dir_path),
                "files": files,
                "count": len(files)
            }
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def search_files(
        self,
        directory: str,
        name_pattern: str,
        content_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for files by name and optionally content
        
        Args:
            directory: Directory to search
            name_pattern: Filename pattern (glob)
            content_pattern: Optional text to search in files
            
        Returns:
            dict: Matching files
        """
        try:
            dir_path = Path(directory).expanduser()
            matches = []
            
            # Search by name
            for file_path in dir_path.rglob(name_pattern):
                if file_path.is_file():
                    file_info = self._get_file_info(file_path)
                    
                    # Search content if pattern provided
                    if content_pattern:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if content_pattern.lower() in content.lower():
                                    file_info["matched_content"] = True
                                    matches.append(file_info)
                        except:
                            pass  # Skip files that can't be read
                    else:
                        matches.append(file_info)
            
            logger.info(f"Found {len(matches)} matching files")
            
            return {
                "directory": str(dir_path),
                "pattern": name_pattern,
                "matches": matches,
                "count": len(matches)
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def open_folder(self, directory: str) -> Dict[str, Any]:
        """
        Open folder in Finder (macOS)
        
        Args:
            directory: Directory path
            
        Returns:
            dict: Status
        """
        try:
            dir_path = Path(directory).expanduser()
            
            if not dir_path.exists():
                return {
                    "error": True,
                    "message": f"Directory not found: {directory}"
                }
            
            # Open in Finder
            os.system(f'open "{dir_path}"')
            
            logger.info(f"Opened folder: {directory}")
            
            return {
                "status": "opened",
                "directory": str(dir_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to open folder: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def create_folder(self, directory: str) -> Dict[str, Any]:
        """
        Create a new folder
        
        Args:
            directory: Directory path to create
            
        Returns:
            dict: Status
        """
        try:
            dir_path = Path(directory).expanduser()
            
            if dir_path.exists():
                return {
                    "error": True,
                    "message": f"Directory already exists: {directory}"
                }
            
            dir_path.mkdir(parents=True, exist_ok=False)
            
            logger.info(f"Created folder: {directory}")
            
            return {
                "status": "created",
                "directory": str(dir_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to create folder: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def delete_folder(self, directory: str, confirmed: bool = False) -> Dict[str, Any]:
        """
        Delete a folder (requires confirmation)
        
        Args:
            directory: Directory path to delete
            confirmed: Confirmation flag (must be True)
            
        Returns:
            dict: Status
        """
        if not confirmed:
            return {
                "error": True,
                "message": "Deletion requires explicit confirmation",
                "suggestion": "Set confirmed=True to proceed"
            }
        
        try:
            dir_path = Path(directory).expanduser()
            
            if not dir_path.exists():
                return {
                    "error": True,
                    "message": f"Directory not found: {directory}"
                }
            
            shutil.rmtree(dir_path)
            
            logger.warning(f"Deleted folder: {directory}")
            
            return {
                "status": "deleted",
                "directory": str(dir_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to delete folder: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """
        Move a file
        
        Args:
            source: Source file path
            destination: Destination path
            
        Returns:
            dict: Status
        """
        try:
            src_path = Path(source).expanduser()
            dst_path = Path(destination).expanduser()
            
            if not src_path.exists():
                return {
                    "error": True,
                    "message": f"Source file not found: {source}"
                }
            
            shutil.move(str(src_path), str(dst_path))
            
            logger.info(f"Moved file: {source} -> {destination}")
            
            return {
                "status": "moved",
                "source": str(src_path),
                "destination": str(dst_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to move file: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        """
        Copy a file
        
        Args:
            source: Source file path
            destination: Destination path
            
        Returns:
            dict: Status
        """
        try:
            src_path = Path(source).expanduser()
            dst_path = Path(destination).expanduser()
            
            if not src_path.exists():
                return {
                    "error": True,
                    "message": f"Source file not found: {source}"
                }
            
            shutil.copy2(str(src_path), str(dst_path))
            
            logger.info(f"Copied file: {source} -> {destination}")
            
            return {
                "status": "copied",
                "source": str(src_path),
                "destination": str(dst_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to copy file: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def rename_file(self, source: str, new_name: str) -> Dict[str, Any]:
        """
        Rename a file
        
        Args:
            source: Source file path
            new_name: New filename (not full path)
            
        Returns:
            dict: Status
        """
        try:
            src_path = Path(source).expanduser()
            
            if not src_path.exists():
                return {
                    "error": True,
                    "message": f"File not found: {source}"
                }
            
            dst_path = src_path.parent / new_name
            src_path.rename(dst_path)
            
            logger.info(f"Renamed file: {source} -> {new_name}")
            
            return {
                "status": "renamed",
                "old_name": src_path.name,
                "new_name": new_name,
                "path": str(dst_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to rename file: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def sort_files(
        self,
        directory: str,
        sort_by: str = "name",
        reverse: bool = False
    ) -> Dict[str, Any]:
        """
        Sort files in a directory
        
        Args:
            directory: Directory path
            sort_by: Sort criteria ("name", "size", "date")
            reverse: Reverse sort order
            
        Returns:
            dict: Sorted file list
        """
        try:
            # Get files
            result = await self.list_files(directory)
            
            if result.get("error"):
                return result
            
            files = result["files"]
            
            # Sort
            if sort_by == "size":
                files.sort(key=lambda x: x["size"], reverse=reverse)
            elif sort_by == "date":
                files.sort(key=lambda x: x["modified"], reverse=reverse)
            else:  # name
                files.sort(key=lambda x: x["name"], reverse=reverse)
            
            return {
                "directory": directory,
                "files": files,
                "count": len(files),
                "sorted_by": sort_by,
                "reverse": reverse
            }
            
        except Exception as e:
            logger.error(f"Failed to sort files: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file metadata"""
        stat = file_path.stat()
        
        return {
            "name": file_path.name,
            "path": str(file_path),
            "size": stat.st_size,
            "size_human": self._format_size(stat.st_size),
            "modified": stat.st_mtime,
            "extension": file_path.suffix
        }
    
    @staticmethod
    def _format_size(size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"


if __name__ == "__main__":
    # Test file tools
    import asyncio
    
    async def test():
        tools = FileTools()
        
        print("Testing FileTools...")
        
        # Test list files
        print("\nListing files in Downloads:")
        result = await tools.list_files("~/Downloads", pattern="*.pdf")
        print(f"Found {result.get('count', 0)} PDF files")
        
        # Test search
        print("\nSearching for Python files:")
        result = await tools.search_files("~/Downloads", "*.py")
        print(f"Found {result.get('count', 0)} Python files")
        
        print("\nFileTools test completed")
    
    asyncio.run(test())
