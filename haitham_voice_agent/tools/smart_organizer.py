import os
import shutil
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class SmartOrganizer:
    """
    Smart File Organizer
    Handles organizing Downloads and cleaning Desktop.
    """
    
    # File Categories
    CATEGORIES = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".heic", ".webp"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Audio": [".mp3", ".wav", ".m4a", ".flac"],
        "Video": [".mp4", ".mov", ".avi", ".mkv"],
        "Code": [".py", ".js", ".html", ".css", ".json", ".xml", ".java", ".cpp"],
        "Installers": [".dmg", ".pkg", ".app"] # .app is a directory but treated as file on macOS
    }
    
    def __init__(self):
        self.home = Path.home()
        self.downloads = self.home / "Downloads"
        self.desktop = self.home / "Desktop"
        
    def organize_downloads(self) -> Dict[str, Any]:
        """
        Organize files in Downloads folder into categories.
        Returns a summary report.
        """
        logger.info("Starting Downloads organization...")
        
        report = {
            "total_moved": 0,
            "categories": {},
            "errors": []
        }
        
        if not self.downloads.exists():
            return {"error": "Downloads folder not found"}
            
        # Create category folders
        for cat in self.CATEGORIES.keys():
            (self.downloads / cat).mkdir(exist_ok=True)
            
        # Scan and move
        for item in self.downloads.iterdir():
            if item.is_file() and not item.name.startswith("."):
                # Skip if it's already in a category folder (though iterdir is shallow)
                # iterdir is shallow, so we are fine.
                
                category = self._get_category(item)
                if category:
                    try:
                        dest_dir = self.downloads / category
                        dest_path = dest_dir / item.name
                        
                        # Handle duplicates
                        if dest_path.exists():
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            dest_path = dest_dir / f"{item.stem}_{timestamp}{item.suffix}"
                            
                        shutil.move(str(item), str(dest_path))
                        
                        # Update report
                        report["total_moved"] += 1
                        report["categories"][category] = report["categories"].get(category, 0) + 1
                        
                    except Exception as e:
                        logger.error(f"Failed to move {item.name}: {e}")
                        report["errors"].append(f"{item.name}: {str(e)}")
        
        # Cleanup empty category folders? No, keep them for structure.
        
        return report

    def clean_desktop(self) -> Dict[str, Any]:
        """
        Clean Desktop by moving Screenshots and clutter to a folder.
        """
        logger.info("Starting Desktop cleanup...")
        
        report = {
            "total_moved": 0,
            "screenshots_moved": 0,
            "misc_moved": 0,
            "dest_folder": ""
        }
        
        # Create cleanup folder with date
        date_str = datetime.now().strftime("%Y-%m-%d")
        cleanup_dir = self.desktop / f"Desktop Cleanup {date_str}"
        screenshots_dir = self.home / "Pictures" / "Screenshots"
        
        # Ensure directories exist
        # We only create cleanup_dir if we actually move stuff (except screenshots)
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        for item in self.desktop.iterdir():
            if item.name.startswith(".") or item.name == "Desktop Cleanup":
                continue
                
            # Handle Screenshots
            if item.is_file() and "Screenshot" in item.name and item.suffix == ".png":
                try:
                    dest = screenshots_dir / item.name
                    if dest.exists():
                        timestamp = datetime.now().strftime("%H%M%S")
                        dest = screenshots_dir / f"{item.stem}_{timestamp}{item.suffix}"
                    
                    shutil.move(str(item), str(dest))
                    report["total_moved"] += 1
                    report["screenshots_moved"] += 1
                except Exception as e:
                    logger.error(f"Failed to move screenshot {item.name}: {e}")
            
            # Handle other loose files (not folders, not aliases ideally)
            # For safety, let's only move Screenshots for now, OR move everything else to cleanup folder
            # User request was "Clean Desktop". Usually implies moving loose files.
            elif item.is_file():
                # Lazy create cleanup dir
                if not cleanup_dir.exists():
                    cleanup_dir.mkdir(exist_ok=True)
                    
                try:
                    dest = cleanup_dir / item.name
                    if dest.exists():
                        timestamp = datetime.now().strftime("%H%M%S")
                        dest = cleanup_dir / f"{item.stem}_{timestamp}{item.suffix}"
                        
                    shutil.move(str(item), str(dest))
                    report["total_moved"] += 1
                    report["misc_moved"] += 1
                except Exception as e:
                    logger.error(f"Failed to move {item.name}: {e}")
        
        if report["misc_moved"] > 0:
            report["dest_folder"] = str(cleanup_dir)
            
        return report

    def _get_category(self, file_path: Path) -> str:
        """Determine category based on file extension"""
        suffix = file_path.suffix.lower()
        for cat, extensions in self.CATEGORIES.items():
            if suffix in extensions:
                return cat
        return None

# Singleton
_organizer = None

def get_organizer():
    global _organizer
    if _organizer is None:
        _organizer = SmartOrganizer()
    return _organizer
