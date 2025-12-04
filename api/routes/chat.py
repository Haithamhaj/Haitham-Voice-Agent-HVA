from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from haitham_voice_agent.dispatcher import get_dispatcher
from haitham_voice_agent.intent_router import route_command
from haitham_voice_agent.llm_router import get_router as get_llm_router
from haitham_voice_agent.ollama_orchestrator import get_orchestrator
import logging

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str

@router.post("/")
async def chat(request: ChatRequest):
    """Process text chat message"""
    try:
        text = request.message
        logger.info(f"Chat request: {text}")
        
        dispatcher = get_dispatcher()
        llm_router = get_llm_router()
        ollama = get_orchestrator()
        
        # 0. Check Ollama Orchestrator (Local Intelligence)
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
                 step = {"tool": "files", "action": "open_folder", "params": {"path": ollama_result["parameters"].get("path")}}
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
            
            if step:
                try:
                    result = await dispatcher.dispatch(step)
                except Exception as e:
                    # Handle "Action not found" or other dispatch errors gracefully
                    logger.warning(f"Dispatch failed for {step}: {e}")
                    # Fallback to GPT if local dispatch fails (e.g. for complex tasks)
                    return {"response": "عذراً، لم أتمكن من تنفيذ هذا الأمر محلياً. سأحاول بطريقة أخرى.", "model": "Qwen 2.5 (Local)"}
                
                # Localize response if input is Arabic
                response_text = str(result.get("message") or result)
                is_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
                
                if is_arabic and result.get("success"):
                    if ollama_result["intent"] == "show_files":
                        count = result.get("count", 0)
                        dir_name = result.get("directory", "المجلد")
                        response_text = f"تم العثور على {count} ملف في {dir_name}"
                    elif ollama_result["intent"] == "open_folder":
                        response_text = f"تم فتح المجلد: {result.get('path', '')}"
                
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
        return {
            "response": str(last_result.get("message") or last_result.get("content") or "تم التنفيذ."),
            "type": "action_result",
            "data": last_result,
            "model": last_result.get("model", "GPT-5-mini") # Default to GPT if not specified
        }

    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        # Return error as response so user sees it in chat
        return {"response": f"حدث خطأ: {str(e)}"}
