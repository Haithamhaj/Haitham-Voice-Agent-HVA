from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from haitham_voice_agent.dispatcher import get_dispatcher
from haitham_voice_agent.intent_router import route_command
from haitham_voice_agent.llm_router import get_router as get_llm_router
from haitham_voice_agent.ollama_orchestrator import get_orchestrator
import logging

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    message: str
    command: Optional[str] = None
    params: Optional[Dict[str, Any]] = None

@router.post("/")
async def chat(request: ChatRequest):
    """Process text chat message or direct command"""
    try:
        text = request.message
        command = request.command
        params = request.params
        
        logger.info(f"Chat request: {text} (Command: {command})")
        
        dispatcher = get_dispatcher()
        llm_router = get_llm_router()
        ollama = get_orchestrator()
        
        # 0. Direct Command Execution (e.g. from Confirmation Buttons)
        if command:
            logger.info(f"Executing direct command: {command}")
            # Parse tool.action
            try:
                tool_name, action_name = command.split(".")
                step = {
                    "tool": tool_name,
                    "action": action_name,
                    "params": params or {}
                }
                result = await dispatcher.dispatch(step)
                
                # Handle result
                return {
                    "response": str(result.get("message") or result),
                    "type": "action_result",
                    "data": result,
                    "model": "System (Direct)"
                }
            except Exception as e:
                logger.error(f"Direct command failed: {e}")
                return {"response": f"فشل تنفيذ الأمر: {str(e)}", "model": "System"}

        # 1. Check Ollama Orchestrator (Local Intelligence)
        # This handles greetings, simple Q&A, and local commands FAST without cloud cost.
        ollama_result = await ollama.classify_request(text)
        
        if ollama_result["type"] == "direct_response":
            logger.info("Ollama handled request directly")
            return {"response": ollama_result["response"], "model": "Qwen 2.5 (Local)"}
            
        elif ollama_result["type"] == "execute_command":
            logger.info(f"Ollama triggered local command: {ollama_result['intent']}")
            # Dispatch local command
            step = {
                "tool": "system", # Assuming system tool handles these, or we map them
                "action": ollama_result["intent"],
                "params": ollama_result.get("parameters", {})
            }
            # We might need to map intents to actual tool calls if they differ
            # For now, let's assume dispatcher can handle or we map manually
            if ollama_result["intent"] == "open_folder":
                 # Use open_file for folders too, as it uses system 'open' command
                 step = {"tool": "files", "action": "open_file", "params": {"path": ollama_result["parameters"].get("path")}}
            elif ollama_result["intent"] == "open_app":
                 step = {"tool": "system", "action": "open_app", "params": {"app_name": ollama_result["parameters"].get("app")}}
            elif ollama_result["intent"] == "show_files":
                 step = {
                     "tool": "files", 
                     "action": "list_files", 
                     "params": {
                         "directory": ollama_result["parameters"].get("path"),
                         "sort_by": ollama_result["parameters"].get("sort_by", "name")
                     }
                 }
            elif ollama_result["intent"] == "organize_documents":
                 step = {
                     "tool": "files",
                     "action": "organize_documents",
                     "params": {
                         "path": ollama_result["parameters"].get("path"),
                         "mode": ollama_result["parameters"].get("mode"),
                         "instruction": ollama_result["parameters"].get("instruction")
                     }
                 }
            elif ollama_result["intent"] == "system_check":
                 # Default to health check
                 action = ollama_result["parameters"].get("action", "health")
                 tool_action = "check_health"
                 if "clean" in action or "cache" in action:
                     tool_action = "clean_cache"
                 elif "slow" in action or "hog" in action:
                     tool_action = "find_hogs"
                     
                 step = {
                     "tool": "system_sentry",
                     "action": tool_action,
                     "params": {}
                 }
            elif ollama_result["intent"] == "search_files":
                 # Use memory_system directly (same as /memory/search) for consistent, rich results
                 from haitham_voice_agent.tools.memory.memory_system import memory_system
                 await memory_system.initialize()
                 
                 # Use the full text as the query to match Memory View behavior (which handles natural language well)
                 query = text
                 
                 # Search Memories & Files (now includes transliteration in memory_system)
                 memories = await memory_system.search_memories(query=query, limit=20)
                 files = await memory_system.search_files(query=query, limit=50)
                 
                 # Format results for frontend (Rich Cards)
                 formatted_results = []
                 
                 # Add Memories
                 for mem in memories:
                     formatted_results.append({
                         "id": mem.id,
                         "content": mem.ultra_brief or mem.raw_content[:200],
                         "text": mem.raw_content,
                         "type": mem.type.value if hasattr(mem.type, "value") else str(mem.type),
                         "project": mem.project,
                         "timestamp": mem.timestamp.isoformat() if hasattr(mem.timestamp, "isoformat") else str(mem.timestamp),
                         "metadata": {
                             "type": mem.type.value if hasattr(mem.type, "value") else str(mem.type),
                             "project": mem.project,
                             "source": "memory"
                         }
                     })
                     
                 # Add Files
                 for f in files:
                     formatted_results.append({
                         "id": f.get("path"),
                         "content": f.get("description") or f.get("path"),
                         "text": f.get("description", ""),
                         "type": "file",
                         "project": f.get("project_id", "Unknown"),
                         "timestamp": f.get("last_modified", ""),
                         "score": f.get("score", 0),
                         "metadata": {
                             "type": "file",
                             "project": f.get("project_id"),
                             "path": f.get("path"),
                             "source": "file_index"
                         }
                     })
                 
                 # Construct natural language summary
                 summary = ""
                 if not memories and not files:
                     summary = "لم أجد أي نتائج مطابقة."
                 else:
                     summary = f"وجدت {len(memories)} ملاحظات و {len(files)} ملفات."
                     if files:
                         top_files = [f.get('path', '').split('/')[-1] for f in files[:3]]
                         file_list_str = "، ".join([f"'{f}'" for f in top_files])
                         summary += f" أبرزها: {file_list_str}."
                 
                 # Return rich response
                 return {
                     "response": summary,
                     "type": "search_results", # Frontend should render this as cards
                     "data": formatted_results,
                     "model": "Memory Search"
                 }
            elif ollama_result["intent"] == "confirm_action":
                 # User said "Ok" / "Yes". Check if we have a pending plan.
                 # For now, we assume the pending plan is the last organization plan.
                 # Ideally, we should store state in a session manager.
                 # We will trigger the execution of the LAST generated plan.
                 step = {
                     "tool": "files",
                     "action": "execute_organization",
                     "params": {
                         "confirm": True # Flag to indicate confirmation
                     }
                 }
            
            if step:
                try:
                    result = await dispatcher.dispatch(step)
                except Exception as e:
                    # Handle "Action not found" or other dispatch errors gracefully
                    logger.warning(f"Dispatch failed for {step}: {e}")
                    # Fallback to GPT if local dispatch fails (e.g. for complex tasks)
                    return {"response": "عذراً، لم أتمكن من تنفيذ هذا الأمر محلياً. سأحاول بطريقة أخرى.", "model": "Qwen 2.5 (Local)"}
                
                # Localize response if input is Arabic
                # Handle both string results (from voice search) and dict results
                if isinstance(result, str):
                    # Voice search returns a string directly - return it immediately
                    return {
                        "response": result,
                        "type": "search_result",
                        "model": "Memory Search"
                    }
                    
                response_text = str(result.get("message") or result)
                is_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
                
                if result.get("success") is not None and isinstance(result.get("success"), int):
                     # This is an execution report
                     success_count = result.get("success", 0)
                     failed_count = result.get("failed", 0)
                     checkpoint_failed = result.get("checkpoint_failed", False)
                     
                     if is_arabic:
                         if failed_count == 0:
                             response_text = f"✅ تم تنفيذ العملية بنجاح على {success_count} ملف."
                         else:
                             response_text = f"⚠️ تم نقل {success_count} ملف، ولكن فشل نقل {failed_count} ملف."
                         
                         # CRITICAL: Warn if checkpoint failed
                         if checkpoint_failed:
                             response_text += f"\n\n🚨 تحذير: فشل تسجيل العملية! لا يمكن التراجع عن هذه التغييرات."
                     else:
                         if failed_count == 0:
                             response_text = f"✅ Successfully processed {success_count} files."
                         else:
                             response_text = f"⚠️ Processed {success_count} files, but {failed_count} failed."
                         
                         # CRITICAL: Warn if checkpoint failed
                         if checkpoint_failed:
                             response_text += f"\n\n🚨 Warning: Failed to log operation! Cannot undo these changes."

                elif is_arabic and result.get("success"):
                    if ollama_result["intent"] == "show_files":
                        count = result.get("count", 0)
                        dir_name = result.get("directory", "المجلد")
                        response_text = f"تم العثور على {count} ملف في {dir_name}"
                    elif ollama_result["intent"] == "open_folder":
                        response_text = f"تم فتح المجلد: {result.get('path', '')}"
                
                # Special handling for Organization Plan (Deep/Simple Organizer)
                if result.get("type") == "organization_plan" or result.get("status") == "plan_ready":
                    # Force type for frontend rendering
                    result["type"] = "organization_plan"
                    
                    plan = result.get("plan", {})
                    changes = plan.get("changes", [])
                    count = len(changes)
                    
                    if count == 0:
                        response_text = "لم يتم العثور على ملفات تحتاج إلى تنظيم."
                    else:
                        response_text = f"🔍 تم تحليل {plan.get('scanned', 0)} ملف.\n"
                        response_text += f"✨ تم اقتراح تغييرات لـ {count} ملف:\n\n"
                        for change in changes[:3]: # Show first 3 examples
                            old_name = change['original_path'].split('/')[-1]
                            new_name = change['new_filename']
                            cat = change['category']
                            response_text += f"📄 {old_name} ➡️ {cat}/{new_name}\n"
                        
                        if count > 3:
                            response_text += f"\n...و {count - 3} ملفات أخرى."
                            
                        response_text += "\n\nهل تريد تنفيذ هذه التغييرات؟"
                    
                    return {
                        "response": response_text,
                        "type": "organization_plan", # Force type for frontend
                        "data": result,
                        "model": "System"
                    }

                return {
                    "response": response_text,
                    "data": result, # Pass full result for frontend rendering
                    "model": "Qwen 2.5 (Local)"
                }
                
        elif ollama_result["type"] == "needs_clarification":
            return {"response": ollama_result["question"], "model": "Qwen 2.5 (Local)"}
            
        # If type is "delegate" or unknown, proceed to existing logic (Intent Router -> LLM)
        logger.info(f"Ollama delegated request: {ollama_result.get('reason')}")

        # 1. Check Intent Router (Fast Path)
        intent_result = route_command(text)
        
        if intent_result["confidence"] > 0.8:
            logger.info(f"Intent matched: {intent_result['action']}")
            
            # Map intent action to Dispatcher plan
            # We need a mapping helper or just construct the step manually
            action = intent_result["action"]
            params = intent_result["params"]
            
            step = {}
            
            # Mapping logic
            if action == "save_memory_note":
                step = {"tool": "memory", "action": "save_note", "params": params}
            elif action == "fetch_latest_email":
                step = {"tool": "gmail", "action": "fetch_latest_email", "params": {}}
            elif action == "list_tasks":
                step = {"tool": "tasks", "action": "list_tasks", "params": {}}
            elif action == "create_task":
                 # Extract task content if possible, or pass raw text
                 step = {"tool": "tasks", "action": "add_task", "params": {"description": text}}
            elif action == "tasks.add_task": # Handle potential LLM hallucinated action name
                 step = {"tool": "tasks", "action": "add_task", "params": {"description": text}}
            elif action == "system.move_file" or action == "files.move_file":
                 # Map move_file hallucination to files tool
                 step = {"tool": "files", "action": "move_file", "params": params}
            else:
                # Fallback to LLM if mapping not explicit
                logger.info("Intent matched but no direct mapping, falling back to LLM")
                step = None
                
            if step:
                result = await dispatcher.dispatch(step)
                return {"response": str(result.get("message") or result), "model": "Intent Router (Rule-based)"}

        # 2. LLM Planner (Slow Path)
        logger.info("Generating execution plan via LLM...")
        plan = await llm_router.generate_execution_plan(text)
        
        # 3. Execute Plan
        results = await dispatcher.execute_plan(plan)
        
        # Format response
        if not results:
             # Fallback to direct chat if no plan steps
             logger.info("No plan steps, falling back to direct chat")
             response_data = await llm_router.generate_with_gpt(text)
             return {"response": response_data["content"], "model": response_data["model"]}
             
        last_result = results[-1]
        
        # Check for "Tool not found" error
        if last_result.get("error") and "Tool not found" in last_result.get("message", ""):
             logger.info("Tool not found, falling back to direct chat")
             response_data = await llm_router.generate_with_gpt(text)
             return {"response": response_data["content"], "type": "text", "model": response_data["model"]}

        # Return full result for rich rendering
        # Return full result for rich rendering
        response_text = str(last_result.get("message") or last_result.get("content") or "تم التنفيذ.")
        
        # Special handling for Organizer Report
        if "total_moved" in last_result and "categories" in last_result:
            count = last_result["total_moved"]
            cats = last_result["categories"]
            details = ", ".join([f"{k}: {v}" for k, v in cats.items()])
            response_text = f"تم نقل {count} ملفات إلى المستندات.\nالتفاصيل: {details}"
            
        # Special handling for Organization Plan (Deep/Simple Organizer)
        if last_result.get("type") == "organization_plan" or last_result.get("status") == "plan_ready":
            # Force type for frontend rendering
            last_result["type"] = "organization_plan"
            
            plan = last_result.get("plan", {})
            changes = plan.get("changes", [])
            count = len(changes)
            
            if count == 0:
                response_text = "لم يتم العثور على ملفات تحتاج إلى تنظيم."
            else:
                response_text = f"🔍 تم تحليل {plan.get('scanned', 0)} ملف.\n"
                response_text += f"✨ تم اقتراح تغييرات لـ {count} ملف:\n\n"
                for change in changes[:3]: # Show first 3 examples
                    old_name = change['original_path'].split('/')[-1]
                    new_name = change['new_filename']
                    cat = change['category']
                    response_text += f"📄 {old_name} ➡️ {cat}/{new_name}\n"
                
                if count > 3:
                    response_text += f"\n...و {count - 3} ملفات أخرى."
                    
                response_text += "\n\nهل تريد تنفيذ هذه التغييرات؟"
            
            return {
                "response": response_text,
                "type": "confirmation_required",
                "data": last_result,
                "model": "System"
            }

            return {
                "response": response_text,
                "type": "confirmation_required",
                "data": last_result,
                "model": "System"
            }
            
        # Special handling for Undo/Rollback
        if last_result.get("type") == "rollback_report" or ("success" in last_result and "failed" in last_result and isinstance(last_result["success"], int)):
            success = last_result.get("success", 0)
            failed = last_result.get("failed", 0)
            
            if failed == 0:
                response_text = f"✅ تم تنفيذ العملية بنجاح ({success} ملف)."
            else:
                response_text = f"⚠️ تم تنفيذ {success} عملية، وفشل {failed}."
            
            # Ensure type is set for frontend
            last_result["type"] = "rollback_report"
            
            return {
                "response": response_text,
                "type": "action_result",
                "data": last_result,
                "model": "System"
            }

        return {
            "response": response_text,
            "type": "action_result",
            "data": last_result,
            "model": last_result.get("model", "GPT-5 (Premium)") # Default to GPT if not specified
        }

    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        # Return error as response so user sees it in chat
        return {"response": f"حدث خطأ: {str(e)}"}
