import os
import shutil
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from haitham_voice_agent.intelligence.content_extractor import content_extractor
from haitham_voice_agent.llm_router import get_router

logger = logging.getLogger(__name__)

class DeepOrganizer:
    """
    Deep Documents Organizer
    Scans, analyzes content, renames, and reorganizes files.
    """
    
    # Safety: Ignore these directories
    IGNORE_DIRS = {
        ".git", ".svn", ".hg", ".idea", ".vscode", 
        "node_modules", "venv", "env", "__pycache__",
        "build", "dist", "target", "bin", "obj"
    }
    
    # Safety: Ignore these file extensions (code, system files)
    IGNORE_EXTS = {
        ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".c", ".h", 
        ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".toml", ".ini",
        ".sh", ".bat", ".ps1", ".lock", ".gitignore", ".dockerignore"
    }

    def __init__(self):
        self.llm_router = get_router()
        
    async def scan_and_plan(self, directory: str) -> Dict[str, Any]:
        """
        Scan directory and generate a reorganization plan.
        Does NOT modify files.
        """
        root_path = Path(directory)
        if not root_path.exists():
            return {"error": f"Directory not found: {directory}"}
            
        logger.info(f"Starting Deep Scan of {directory}...")
        
        plan = {
            "root": str(root_path),
            "timestamp": datetime.now().isoformat(),
            "changes": [],
            "ignored": 0,
            "scanned": 0
        }
        
        # Collect all valid files first
        files_to_process = []
        for root, dirs, files in os.walk(root_path):
            # Filter directories in-place
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS and not d.startswith(".")]
            
            for file in files:
                if file.startswith("."):
                    continue
                    
                file_path = Path(root) / file
                
                # Check extension safety
                if file_path.suffix.lower() in self.IGNORE_EXTS:
                    plan["ignored"] += 1
                    continue
                
                files_to_process.append((file_path, root_path))
                
        # Limit total files to prevent massive bills/timeouts
        MAX_FILES = 20
        if len(files_to_process) > MAX_FILES:
            logger.warning(f"Too many files ({len(files_to_process)}). Limiting to {MAX_FILES}.")
            files_to_process = files_to_process[:MAX_FILES]
            
        # Process in parallel with semaphore
        import asyncio
        semaphore = asyncio.Semaphore(5) # Max 5 concurrent GPT calls
        
        async def analyze_with_limit(fp, rp):
            async with semaphore:
                return await self._analyze_file(fp, rp)
        
        tasks = [analyze_with_limit(fp, rp) for fp, rp in files_to_process]
        results = await asyncio.gather(*tasks)
        
        for change in results:
            plan["scanned"] += 1
            if change:
                plan["changes"].append(change)
                
        return plan

    async def _analyze_file(self, file_path: Path, root_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze file content and propose new name/location"""
        try:
            # Broadcast: Scanning
            from api.connection_manager import manager
            await manager.broadcast({"type": "log", "message": f"🔍 Scanning: {file_path.name}..."})
            
            # Extract text
            text = content_extractor.extract_text(str(file_path))
            if not text or len(text) < 50:
                return None # Skip empty/unreadable files
                
            # Step 1: Summarize with Gemini (Cost efficient & fast)
            await manager.broadcast({"type": "log", "message": f"🧠 Gemini: Summarizing {file_path.name}..."})
            summary_result = await self.llm_router.summarize_with_gemini(text, summary_type="brief")
            summary = summary_result["content"]
            
            # Step 2: Plan with GPT (Reasoning)
            await manager.broadcast({"type": "log", "message": f"🤖 GPT: Planning organization for {file_path.name}..."})
            
            # LLM Prompt
            prompt = f"""
            Analyze the following document summary and propose a new filename and folder structure.
            
            Current File: {file_path.name}
            Summary: {summary}
            
            Rules:
            1. Rename: Generate a descriptive, concise filename in snake_case (e.g., "invoice_google_oct2025.pdf"). Keep the original extension.
            2. Reorganize: Suggest a Category/Subcategory path (e.g., "Financials/Invoices").
            3. Context: Distinguish between Personal, Work, Legal, Health, etc.
            
            Return JSON ONLY:
            {{
                "new_filename": "...",
                "category_path": "Category/Subcategory",
                "reason": "Brief explanation"
            }}
            """
            
            response = await self.llm_router.generate_with_gpt(
                prompt, 
                temperature=0.2,
                response_format="json_object"
            )
            
            result = json.loads(response["content"])
            
            new_filename = result.get("new_filename")
            category_path = result.get("category_path")
            
            # Validate
            if not new_filename or not category_path:
                return None
                
            # Ensure extension is preserved/correct
            if not new_filename.endswith(file_path.suffix.lower()):
                new_filename += file_path.suffix.lower()
                
            # Construct proposed path
            proposed_path = root_path / category_path / new_filename
            
            # Skip if no change
            if proposed_path.resolve() == file_path.resolve():
                return None
                
            return {
                "original_path": str(file_path),
                "proposed_path": str(proposed_path),
                "new_filename": new_filename,
                "category": category_path,
                "reason": result.get("reason")
            }
            
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path.name}: {e}")
            return None

    async def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the approved plan"""
        logger.info("Executing Deep Organizer Plan...")
        
        report = {
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        changes = plan.get("changes", [])
        if not changes:
            return report
            
        # Track operations for checkpoint
        operations_log = []
        total_cost = 0.0
        total_tokens = 0
            
        for change in changes:
            try:
                src = Path(change["original_path"])
                dst = Path(change["proposed_path"])
                
                # Accumulate usage from analysis
                if "usage" in change:
                    total_cost += change["usage"].get("cost", 0.0)
                    total_tokens += change["usage"].get("input_tokens", 0) + change["usage"].get("output_tokens", 0)
                
                if not src.exists():
                    report["failed"] += 1
                    report["errors"].append(f"Source not found: {src}")
                    continue
                    
                # Create parent dirs
                dst.parent.mkdir(parents=True, exist_ok=True)
                
                # Handle duplicates
                if dst.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dst = dst.parent / f"{dst.stem}_{timestamp}{dst.suffix}"
                    
                shutil.move(str(src), str(dst))
                report["success"] += 1
                
                # Log operation
                operations_log.append({
                    "src": str(src),
                    "dst": str(dst)
                })
                
                # --- Memory Indexing ---
                try:
                    from haitham_voice_agent.tools.memory.voice_tools import VoiceMemoryTools
                    memory_tools = VoiceMemoryTools()
                    await memory_tools.ensure_initialized()
                    
                    # Determine Project ID (from path or default)
                    # Heuristic: If path contains "Projects/X", use X. Else "Documents"
                    project_id = "documents"
                    parts = dst.parts
                    if "Projects" in parts:
                        try:
                            idx = parts.index("Projects")
                            if idx + 1 < len(parts):
                                project_id = parts[idx+1]
                        except:
                            pass
                    
                    await memory_tools.memory_system.index_file(
                        path=str(dst),
                        project_id=project_id,
                        description=f"Organized file: {dst.name}",
                        tags=["organized", change.get("category", "general")]
                    )
                except Exception as mem_err:
                    logger.warning(f"Failed to index organized file {dst}: {mem_err}")
                # -----------------------
                
            except Exception as e:
                logger.error(f"Failed to move {src}: {e}")
                report["failed"] += 1
                report["errors"].append(f"{src.name}: {str(e)}")
        
        # Create Checkpoint if changes were made
        if operations_log:
            try:
                from haitham_voice_agent.tools.checkpoint_manager import get_checkpoint_manager
                cm = get_checkpoint_manager()
                checkpoint_id = await cm.create_checkpoint(
                    action_type="deep_organize",
                    description=f"Deep Organization of {len(operations_log)} files",
                    operations=operations_log,
                    meta={
                        "model": "Hybrid (Gemini + GPT-4o)",
                        "cost": total_cost,
                        "tokens": total_tokens
                    }
                )
                report["checkpoint_id"] = checkpoint_id
                logger.info(f"Checkpoint saved: {checkpoint_id}")
            except Exception as e:
                logger.error(f"Failed to save checkpoint: {e}")
                report["errors"].append(f"Checkpoint failed: {str(e)}")
                
        return report

# Singleton
_deep_organizer = None

def get_deep_organizer():
    global _deep_organizer
    if _deep_organizer is None:
        _deep_organizer = DeepOrganizer()
    return _deep_organizer
