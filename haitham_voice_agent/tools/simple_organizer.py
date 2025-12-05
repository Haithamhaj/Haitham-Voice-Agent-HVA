import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleOrganizer:
    """
    Simple, rule-based file organizer.
    Organizes files by extension into predefined categories.
    Zero cost, no LLM usage.
    """
    
    CATEGORIES = {
        "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".heic"},
        "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages", ".md"},
        "Spreadsheets": {".xls", ".xlsx", ".csv", ".numbers", ".ods"},
        "Presentations": {".ppt", ".pptx", ".key", ".odp"},
        "Audio": {".mp3", ".wav", ".aac", ".m4a", ".flac", ".ogg"},
        "Video": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"},
        "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
        "Code": {".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".json", ".xml", ".yaml", ".sql"},
        "Executables": {".exe", ".msi", ".dmg", ".pkg", ".app"}
    }
    
    def __init__(self):
        pass
        
    async def scan_and_plan(self, directory: str, instruction: str = None) -> Dict[str, Any]:
        """
        Scan directory and generate a simple reorganization plan.
        """
        root_path = Path(directory)
        if not root_path.exists():
            return {"error": f"Directory not found: {directory}"}
            
        logger.info(f"Starting Simple Scan of {directory}...")
        
        plan = {
            "root": str(root_path),
            "timestamp": datetime.now().isoformat(),
            "changes": [],
            "ignored": 0,
            "scanned": 0,
            "mode": "simple"
        }
        
        for root, dirs, files in os.walk(root_path):
            # Skip hidden dirs
            if Path(root).name.startswith("."):
                continue
                
            for file in files:
                if file.startswith("."):
                    continue
                    
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                
                # Check for Date Sorting Instruction
                if instruction and ("date" in instruction.lower() or "تاريخ" in instruction):
                    # Sort by Date: Year/Month
                    mtime = file_path.stat().st_mtime
                    dt = datetime.fromtimestamp(mtime)
                    category = f"{dt.year}/{dt.strftime('%m-%B')}"
                    reason = f"Sorted by Date: {dt.strftime('%Y-%m-%d')}"
                else:
                    # Default: Sort by Extension
                    # Find category
                    category = "Others"
                    for cat, extensions in self.CATEGORIES.items():
                        if ext in extensions:
                            category = cat
                            break
                    reason = f"File extension {ext} maps to {category}"
                
                # Proposed path
                proposed_path = root_path / category / file
                
                # Skip if already in correct place
                if proposed_path.resolve() == file_path.resolve():
                    continue
                    
                plan["scanned"] += 1
                plan["changes"].append({
                    "original_path": str(file_path),
                    "proposed_path": str(proposed_path),
                    "new_filename": file, # No renaming in simple mode
                    "category": category,
                    "reason": reason,
                    "usage": {"cost": 0.0, "tokens": 0} # Explicit zero cost
                })
                
        return plan

    async def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the simple plan"""
        # Reuse DeepOrganizer's execution logic or implement simple move
        # For simplicity and consistency, we can reuse the same structure
        # But since DeepOrganizer has complex indexing, let's keep it simple here or import it?
        # Better to have a shared executor or just implement move here.
        
        report = {
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        changes = plan.get("changes", [])
        operations_log = []
        
        for change in changes:
            try:
                src = Path(change["original_path"])
                dst = Path(change["proposed_path"])
                
                if not src.exists():
                    report["failed"] += 1
                    continue
                    
                dst.parent.mkdir(parents=True, exist_ok=True)
                
                if dst.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dst = dst.parent / f"{dst.stem}_{timestamp}{dst.suffix}"
                    
                shutil.move(str(src), str(dst))
                report["success"] += 1
                
                operations_log.append({
                    "src": str(src),
                    "dst": str(dst),
                    "reason": change.get("reason"),
                    "category": change.get("category")
                })
                
            except Exception as e:
                report["failed"] += 1
                report["errors"].append(str(e))
                
        # Create Checkpoint (Zero Cost)
        if operations_log:
            try:
                from haitham_voice_agent.tools.checkpoint_manager import get_checkpoint_manager
                cm = get_checkpoint_manager()
                await cm.create_checkpoint(
                    action_type="simple_organize",
                    description=f"Simple Organization of {len(operations_log)} files",
                    operations=operations_log,
                    meta={
                        "model": "Rule-Based (Free)",
                        "cost": 0.0,
                        "tokens": 0
                    }
                )
            except Exception:
                pass
                
        return report

# Singleton
_simple_organizer = None

def get_simple_organizer():
    global _simple_organizer
    if _simple_organizer is None:
        _simple_organizer = SimpleOrganizer()
    return _simple_organizer
