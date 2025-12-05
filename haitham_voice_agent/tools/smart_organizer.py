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
    
    # File Categories (Fallback)
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
        self.documents = self.home / "Documents"
        self.llm_router = get_router()
        
    async def organize_old_downloads(self, hours: int = 72) -> Dict[str, Any]:
        """
        Move files older than 'hours' from Downloads to Documents,
        categorized by content using LLM.
        """
        logger.info(f"Starting Smart Cleanup for files older than {hours} hours...")
        
        report = {
            "total_moved": 0,
            "categories": {},
            "errors": []
        }
        
        if not self.downloads.exists():
            return {"error": "Downloads folder not found"}
            
        now = datetime.now()
        cutoff_seconds = hours * 3600
        
        # Scan files
        for item in self.downloads.iterdir():
            if item.name.startswith("."):
                continue
                
            # Check age
            try:
                stat = item.stat()
                # Use modification time
                age_seconds = now.timestamp() - stat.st_mtime
                
                if age_seconds > cutoff_seconds:
                    if item.is_file():
                        await self._process_file(item, report)
                    elif item.is_dir() and not item.name in self.CATEGORIES:
                         # Also move folders if they are old, but maybe treat differently?
                         # For now, let's focus on files as requested.
                         pass
                         
            except Exception as e:
                logger.error(f"Error checking file {item.name}: {e}")
                
        return report

    async def _process_file(self, item: Path, report: Dict[str, Any]):
        """Process a single file: Extract -> Categorize -> Move"""
        try:
            # 1. Extract Content
            text = content_extractor.extract_text(str(item))
            category = "Unsorted"
            
            # 2. Determine Category
            if text and len(text) > 50:
                # Use LLM to categorize with higher granularity
                prompt = f"""
                Analyze the following text from a file named "{item.name}" and categorize it into a folder structure "Category/Subcategory".
                
                CRITICAL INSTRUCTION:
                Base your classification PRIMARILY on the text content. Use the filename only as a secondary hint if the content is ambiguous.
                
                Rules:
                1. Distinguish between 'Personal' and 'Company/Work' if possible.
                2. Use standard categories: Financials, Legal, Projects, Health, Travel, Personal.
                3. Return ONLY the path "Category/Subcategory".
                
                Examples:
                - "Financials/Personal_Expenses" (for personal receipts)
                - "Financials/Company_Reports" (for business statements)
                - "Legal/Contracts"
                - "Projects/Mind_Q"
                
                Text snippet (First 5000 chars):
                {text[:5000]}
                """
                
                try:
                    # Use Gemini Flash for speed
                    result = await self.llm_router.generate_with_gemini(
                        prompt, 
                        logical_model="logical.gemini.flash",
                        temperature=0.3
                    )
                    # Clean up response
                    category_path = result["content"].strip().replace("\\", "/")
                    
                    # Validate format
                    if "/" not in category_path:
                        # If LLM returns just "Financials", maybe append "General" or keep as is?
                        # Let's trust the LLM or default to "General" if it's a known top-level
                        pass
                    
                    # Sanitize
                    category = category_path.replace(" ", "_")
                    
                except Exception as e:
                    logger.warning(f"LLM categorization failed for {item.name}: {e}")
                    category = self._get_category(item) or "Misc"
            else:
                # Fallback to extension-based
                category = self._get_category(item) or "Misc"
                
            # 3. Move File
            # Determine destination root based on category
            if category == "Installers":
                if item.suffix == ".app":
                    dest_root = self.home / "Applications"
                else:
                    dest_root = self.home / "Software"
            elif category == "Archives":
                dest_root = self.home / "Archives" # Keep archives separate too? Or Documents/Archives?
                # Let's keep Archives in Documents for now unless requested otherwise, 
                # but user specifically asked about the App.
                dest_root = self.documents / category
            else:
                dest_root = self.documents / category

            dest_root.mkdir(parents=True, exist_ok=True)
            
            # For Apps in Applications, we don't need a subfolder usually
            if category == "Installers" and item.suffix == ".app":
                dest_path = dest_root / item.name
            elif category == "Installers":
                 # For DMGs/PKGs in Software, maybe no subfolder needed either
                 dest_path = dest_root / item.name
            else:
                 # Standard behavior
                 dest_path = dest_root / item.name

            if dest_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_path = dest_root / f"{item.stem}_{timestamp}{item.suffix}"
                
            shutil.move(str(item), str(dest_path))
            logger.info(f"Moved {item.name} -> {dest_path}")
            
            report["total_moved"] += 1
            report["categories"][category] = report["categories"].get(category, 0) + 1
            
        except Exception as e:
            logger.error(f"Failed to process {item.name}: {e}")
            report["errors"].append(f"{item.name}: {str(e)}")

    def organize_downloads(self) -> Dict[str, Any]:
        """
        Legacy: Organize files in Downloads folder into categories (Extension based).
        Returns a summary report.
        """
        logger.info("Starting Downloads organization (Legacy)...")
        
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
                category = self._get_category(item)
                if category:
                    try:
                        dest_dir = self.downloads / category
                        dest_path = dest_dir / item.name
                        
                        if dest_path.exists():
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            dest_path = dest_dir / f"{item.stem}_{timestamp}{item.suffix}"
                            
                        shutil.move(str(item), str(dest_path))
                        
                        report["total_moved"] += 1
                        report["categories"][category] = report["categories"].get(category, 0) + 1
                        
                    except Exception as e:
                        logger.error(f"Failed to move {item.name}: {e}")
                        report["errors"].append(f"{item.name}: {str(e)}")
        
        return report

        return None

from haitham_voice_agent.intelligence.content_extractor import content_extractor
from haitham_voice_agent.llm_router import get_router

# Singleton
_organizer = None

def get_organizer():
    global _organizer
    if _organizer is None:
        _organizer = SmartOrganizer()
    return _organizer
