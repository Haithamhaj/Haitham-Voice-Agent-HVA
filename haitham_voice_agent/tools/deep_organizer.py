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
        MAX_FILES = 100 # Increased limit due to batching efficiency
        if len(files_to_process) > MAX_FILES:
            logger.warning(f"Too many files ({len(files_to_process)}). Limiting to {MAX_FILES}.")
            files_to_process = files_to_process[:MAX_FILES]
            
        # Batch Processing
        BATCH_SIZE = 5
        batches = [files_to_process[i:i + BATCH_SIZE] for i in range(0, len(files_to_process), BATCH_SIZE)]
        
        results = []
        for batch in batches:
            batch_results = await self._analyze_batch(batch)
            results.extend(batch_results)
        
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
            # await manager.broadcast({"type": "log", "message": f"🔍 Scanning: {file_path.name}..."})
            await manager.broadcast({
                "type": "task_progress",
                "task": "Deep Organize",
                "status": "scanning",
                "file": file_path.name,
                "details": "Analyzing content..."
            })
            
            # --- OPTIMIZATION GUARD (Safety Layer) ---
            # DISABLED TEMPORARILY TO FORCE ARABIC RE-ANALYSIS
            # from haitham_voice_agent.intelligence.optimization_guard import get_optimization_guard
            # guard = get_optimization_guard()
            
            # guard_check = await guard.check_file(str(file_path), context="deep_organize")
            
            # Force process
            guard_check = {"should_process": True}
            
            if not guard_check["should_process"]:
                # Cache Hit! Return cached result with zero cost
                cached_result = guard_check.get("cached_result")
                if cached_result:
                    await manager.broadcast({
                        "type": "task_progress",
                        "task": "Deep Organize",
                        "status": "skipped",
                        "file": file_path.name,
                        "details": f"Cached (Saved ${guard_check.get('savings', 0):.4f})"
                    })
                    return cached_result
                else:
                    # Should not happen if check returns false, but safe fallback
                    return None

            # --- LOCAL FIRST (Gatekeeper) ---
            # Check for obvious patterns (Regex/Keywords)
            local_result = self._local_categorization(file_path, root_path)
            if local_result:
                await manager.broadcast({
                    "type": "task_progress",
                    "task": "Deep Organize",
                    "status": "local_rule",
                    "file": file_path.name,
                    "details": f"Local Rule: {local_result['category']}"
                })
                return local_result
            # --------------------------------

            # Extract text
            text = content_extractor.extract_text(str(file_path))
            if not text or len(text) < 50:
                return None # Skip empty/unreadable files
                
            # --- PHASE 1: ADAPTIVE LEARNING (High-Confidence Patterns) ---
            # Check if we have learned patterns for similar files
            try:
                from haitham_voice_agent.tools.memory.voice_tools import VoiceMemoryTools
                from haitham_voice_agent.tools.memory.storage.sqlite_store import SQLiteStore
                
                mem_tools = VoiceMemoryTools()
                await mem_tools.ensure_initialized()
                sqlite_store = SQLiteStore()
                await sqlite_store.initialize()
                
                # Search for similar files using vector search
                similar_files = await mem_tools.memory_system.search_file_index(text[:1000])
                
                # Check if any similar file has a learning event
                for match in similar_files:
                    match_path = Path(match['path'])
                    file_hash = match.get('file_hash')
                    
                    if not file_hash:
                        continue
                    
                    # Query learning events for this file hash
                    import aiosqlite
                    async with aiosqlite.connect(sqlite_store.db_path) as db:
                        db.row_factory = aiosqlite.Row
                        async with db.execute("""
                            SELECT * FROM learning_events 
                            WHERE file_hash = ? AND confidence >= 0.5
                            ORDER BY confidence DESC, times_applied DESC
                            LIMIT 1
                        """, (file_hash,)) as cursor:
                            learning_event = await cursor.fetchone()
                            
                            if learning_event:
                                event = dict(learning_event)
                                confidence = event['confidence']
                                new_category = event['new_category']
                                
                                # High confidence (>= 0.8): Apply automatically
                                if confidence >= 0.8:
                                    await manager.broadcast({
                                        "type": "task_progress",
                                        "task": "Deep Organize",
                                        "status": "learning_applied",
                                        "file": file_path.name,
                                        "details": f"Learned pattern: {new_category} (confidence: {confidence:.1f})"
                                    })
                                    
                                    return {
                                        "original_path": str(file_path),
                                        "proposed_path": str(root_path / new_category / file_path.name),
                                        "new_filename": file_path.name,
                                        "category": new_category,
                                        "reason": f"Learned from your manual move (confidence: {confidence:.1f}, applied {event['times_applied']} times)",
                                        "learning_event_id": event['id'],  # For feedback
                                        "usage": {
                                            "cost": 0.0,
                                            "input_tokens": 0,
                                            "output_tokens": 0
                                        }
                                    }
                                # Medium confidence (0.5-0.8): Will ask for confirmation in Phase 4
                                elif confidence >= 0.5:
                                    # Store for potential confirmation request
                                    # For now, fall through to mimicry/LLM
                                    pass
            except Exception as e:
                logger.warning(f"Learning event query failed: {e}")
            # -----------------------------------
                
            # --- PHASE 2: ADAPTIVE LEARNING (Mimicry) ---
            # Search for similar files to see where they live
            try:
                from haitham_voice_agent.tools.memory.voice_tools import VoiceMemoryTools
                mem_tools = VoiceMemoryTools()
                await mem_tools.ensure_initialized()
                
                # Search for similar files using vector search
                similar_files = await mem_tools.memory_system.search_file_index(text[:1000]) # Search by content snippet
                
                best_match = None
                for match in similar_files:
                    # Check if match is in a target category folder (not Downloads/Desktop)
                    match_path = Path(match['path'])
                    if "Documents" in match_path.parts or "Projects" in match_path.parts:
                        # Found a good example!
                        best_match = match_path
                        break
                        
                if best_match:
                    # We found a similar file in a good place. Let's mimic it!
                    # Extract category path relative to Documents or Projects
                    # Heuristic: If in Documents/Financials/2024, suggest Financials/2024
                    
                    mimic_category = None
                    parts = best_match.parts
                    if "Documents" in parts:
                        idx = parts.index("Documents")
                        if idx + 1 < len(parts) - 1: # Ensure there is a subfolder and filename
                            mimic_category = "/".join(parts[idx+1:-1])
                            
                    if mimic_category:
                        await manager.broadcast({
                            "type": "task_progress",
                            "task": "Deep Organize",
                            "status": "mimicking",
                            "file": file_path.name,
                            "details": f"Mimicking {best_match.name} -> {mimic_category}"
                        })
                        
                        # Return mimic result without LLM cost!
                        return {
                            "original_path": str(file_path),
                            "proposed_path": str(root_path / mimic_category / file_path.name),
                            "new_filename": file_path.name, # Keep name or ask LLM just to rename? Let's keep name for zero cost.
                            "category": mimic_category,
                            "reason": f"Adaptive Learning: Mimicked placement of similar file '{best_match.name}'",
                            "usage": {
                                "cost": 0.0,
                                "input_tokens": 0,
                                "output_tokens": 0
                            }
                        }
            except Exception as e:
                logger.warning(f"Adaptive Learning failed: {e}")
            # -----------------------------------

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
            4. Language: If the summary suggests Arabic content or the user request was in Arabic, provide the 'reason' field in Arabic.
            
            Return JSON ONLY:
            {{
                "new_filename": "...",
                "category": "Category/Subcategory",
                "reason": "Brief explanation of why this category was chosen (in Arabic if content is Arabic)"
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
                
            # Calculate total usage for this file
            file_usage = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
                "gemini_cost": 0.0,
                "gpt_cost": 0.0,
                "gemini_tokens": 0,
                "gpt_tokens": 0
            }
            
            if "usage" in summary_result:
                u = summary_result["usage"]
                file_usage["input_tokens"] += u.get("input_tokens", 0)
                file_usage["output_tokens"] += u.get("output_tokens", 0)
                file_usage["cost"] += u.get("cost", 0.0)
                file_usage["gemini_cost"] += u.get("cost", 0.0)
                file_usage["gemini_tokens"] += u.get("input_tokens", 0) + u.get("output_tokens", 0)
                
            if "usage" in response:
                u = response["usage"]
                file_usage["input_tokens"] += u.get("input_tokens", 0)
                file_usage["output_tokens"] += u.get("output_tokens", 0)
                file_usage["cost"] += u.get("cost", 0.0)
                file_usage["gpt_cost"] += u.get("cost", 0.0)
                file_usage["gpt_tokens"] += u.get("input_tokens", 0) + u.get("output_tokens", 0)

            final_result = {
                "original_path": str(file_path),
                "proposed_path": str(proposed_path),
                "new_filename": new_filename,
                "category": category_path,
                "reason": result.get("reason"),
                "usage": file_usage
            }
            
            # Save to Guard Cache
            file_hash = guard_check.get("file_hash")
            if file_hash:
                await guard.save_result(
                    file_hash=file_hash,
                    context="deep_organize",
                    result=final_result,
                    cost_saved=file_usage["cost"]
                )

            return final_result
            
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path.name}: {e}")
            return None

    async def _analyze_batch(self, files: List[tuple[Path, Path]]) -> List[Dict[str, Any]]:
        """Analyze a batch of files in one LLM call"""
        results = []
        batch_summary = []
        
        # 1. Prepare Batch
        for file_path, root_path in files:
            try:
                # Check Guard
                from haitham_voice_agent.intelligence.optimization_guard import get_optimization_guard
                guard = get_optimization_guard()
                guard_check = await guard.check_file(str(file_path), context="deep_organize")
                
                if not guard_check["should_process"]:
                    # Cache Hit
                    if guard_check.get("cached_result"):
                        results.append(guard_check["cached_result"])
                    continue
                    
                # Extract
                text = content_extractor.extract_text(str(file_path))
                if not text or len(text) < 50:
                    continue
                    
                # Summarize (Gemini Flash is cheap, do individual summaries for better context)
                # Or skip summary and send truncated text directly in batch?
                # Let's send truncated text (Smart Truncation) to save calls.
                truncated_text = text[:2000] + "\n...\n" + text[-500:] if len(text) > 2500 else text
                
                batch_summary.append({
                    "filename": file_path.name,
                    "content_snippet": truncated_text,
                    "original_path": str(file_path),
                    "root_path": str(root_path),
                    "file_hash": guard_check.get("file_hash")
                })
                
            except Exception as e:
                logger.warning(f"Batch prep failed for {file_path.name}: {e}")
                
        if not batch_summary:
            return results
            
        # 2. Batch Prompt
        prompt = """
        Analyze the following list of files and propose a new filename and folder structure for EACH.
        
        Rules:
        1. Rename: Snake_case, descriptive.
        2. Reorganize: Category/Subcategory.
        3. Context: Personal vs Work.
        
        Files:
        """
        
        for item in batch_summary:
            prompt += f"\n--- FILE: {item['filename']} ---\n{item['content_snippet']}\n"
            
        prompt += """
        
        Return JSON List:
        [
            {
                "original_filename": "...",
                "new_filename": "...",
                "category_path": "...",
                "reason": "..."
            }
        ]
        """
        
        # 3. Call LLM (GPT-4o or Gemini Pro)
        try:
            response = await self.llm_router.generate_with_gpt(
                prompt,
                temperature=0.2,
                response_format="json_object" # GPT-4o supports schema, but let's use object and expect list in key
            )
            
            # Parse
            import json
            content = json.loads(response["content"])
            # Handle if it returns dict with key "files" or just list
            items = content if isinstance(content, list) else content.get("files", content.get("results", []))
            
            # Map back to results
            for item in items:
                # Find matching source
                source = next((x for x in batch_summary if x["filename"] == item.get("original_filename")), None)
                if not source:
                    continue
                    
                new_filename = item.get("new_filename")
                category_path = item.get("category_path")
                
                if not new_filename or not category_path:
                    continue
                    
                if not new_filename.endswith(Path(source["original_filename"]).suffix.lower()):
                    new_filename += Path(source["original_filename"]).suffix.lower()
                    
                proposed_path = Path(source["root_path"]) / category_path / new_filename
                
                # Usage split (approximate)
                total_cost = response["usage"].get("cost", 0.0) / len(items)
                
                result_entry = {
                    "original_path": source["original_path"],
                    "proposed_path": str(proposed_path),
                    "new_filename": new_filename,
                    "category": category_path,
                    "reason": item.get("reason"),
                    "usage": {
                        "cost": total_cost,
                        "gpt_cost": total_cost
                    }
                }
                
                results.append(result_entry)
                
                # Save to Guard
                if source["file_hash"]:
                    await guard.save_result(
                        file_hash=source["file_hash"],
                        context="deep_organize",
                        result=result_entry,
                        cost_saved=0.0
                    )
                    
        except Exception as e:
            logger.error(f"Batch LLM call failed: {e}")
            
        return results

    def _local_categorization(self, file_path: Path, root_path: Path) -> Optional[Dict[str, Any]]:
        """
        Local First: Categorize based on filename keywords/regex.
        Zero cost, instant.
        """
        name = file_path.name.lower()
        category = None
        
        # Rules
        if "screenshot" in name or "screen shot" in name:
            category = "Images/Screenshots"
        elif "invoice" in name or "receipt" in name or "bill" in name:
            category = "Financials/Invoices"
        elif "contract" in name or "agreement" in name or "nda" in name:
            category = "Legal/Contracts"
        elif "resume" in name or "cv" in name:
            category = "Personal/Career"
        elif "statement" in name and ("bank" in name or "card" in name):
            category = "Financials/Statements"
            
        if category:
            return {
                "original_path": str(file_path),
                "proposed_path": str(root_path / category / file_path.name),
                "new_filename": file_path.name, # Keep original name for local rules
                "category": category,
                "reason": f"Local Rule: Filename contains keyword matching '{category}'",
                "usage": {
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0
                }
            }
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
        gemini_cost = 0.0
        gpt_cost = 0.0
        gemini_tokens = 0
        gpt_tokens = 0
            
        for change in changes:
            try:
                src = Path(change["original_path"])
                dst = Path(change["proposed_path"])
                
                # Accumulate usage from analysis
                if "usage" in change:
                    u = change["usage"]
                    total_cost += u.get("cost", 0.0)
                    total_tokens += u.get("input_tokens", 0) + u.get("output_tokens", 0)
                    gemini_cost += u.get("gemini_cost", 0.0)
                    gpt_cost += u.get("gpt_cost", 0.0)
                    gemini_tokens += u.get("gemini_tokens", 0)
                    gpt_tokens += u.get("gpt_tokens", 0)
                
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
                    "dst": str(dst),
                    "reason": change.get("reason"),
                    "category": change.get("category")
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
                    
                    # Calculate hash for the new file
                    import hashlib
                    hasher = hashlib.md5()
                    with open(dst, 'rb') as f:
                        buf = f.read(65536)
                        while len(buf) > 0:
                            hasher.update(buf)
                            buf = f.read(65536)
                    new_file_hash = hasher.hexdigest()

                    await memory_tools.memory_system.index_file(
                        path=str(dst),
                        project_id=project_id,
                        description=f"Organized file: {dst.name}",
                        tags=["organized", change.get("category", "general")],
                        file_hash=new_file_hash
                    )
                    
                    # If this was organized using a learned pattern, log auto-applied event
                    if change.get("learning_event_id"):
                        from haitham_voice_agent.tools.memory.storage.sqlite_store import SQLiteStore
                        sqlite_store = SQLiteStore()
                        await sqlite_store.initialize()
                        
                        # Log that we applied this learning event
                        await sqlite_store.log_learning_event(
                            file_hash=new_file_hash,
                            event_type="auto_applied",
                            old_path=str(src),
                            new_path=str(dst),
                            old_category="Downloads",  # Assuming from Downloads
                            new_category=change.get("category", "Unknown"),
                            description=f"Auto-applied learned pattern",
                            embedding_id=None
                        )
                        logger.info(f"Logged auto-applied event for {dst.name}")
                    
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
                        "tokens": total_tokens,
                        "gemini_cost": gemini_cost,
                        "gpt_cost": gpt_cost,
                        "gemini_tokens": gemini_tokens,
                        "gpt_tokens": gpt_tokens
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
