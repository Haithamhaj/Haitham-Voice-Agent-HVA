from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from haitham_voice_agent.dispatcher import get_dispatcher
from haitham_voice_agent.intent_router import route_command
from haitham_voice_agent.llm_router import get_router as get_llm_router
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
            else:
                # Fallback to LLM if mapping not explicit
                logger.info("Intent matched but no direct mapping, falling back to LLM")
                step = None
                
            if step:
                result = await dispatcher.dispatch(step)
                return {"response": str(result.get("message") or result)}

        # 2. LLM Planner (Slow Path)
        logger.info("Generating execution plan via LLM...")
        plan = await llm_router.generate_execution_plan(text)
        
        # 3. Execute Plan
        results = await dispatcher.execute_plan(plan)
        
        # Format response
        if not results:
             # Fallback to direct chat if no plan steps
             logger.info("No plan steps, falling back to direct chat")
             response_text = await llm_router.generate_with_gpt(text)
             return {"response": response_text}
             
        last_result = results[-1]
        
        # Check for "Tool not found" error
        if last_result.get("error") and "Tool not found" in last_result.get("message", ""):
             logger.info("Tool not found, falling back to direct chat")
             response_text = await llm_router.generate_with_gpt(text)
             return {"response": response_text, "type": "text"}

        # Return full result for rich rendering
        return {
            "response": str(last_result.get("message") or "تم التنفيذ."),
            "type": "action_result",
            "data": last_result
        }

    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        # Return error as response so user sees it in chat
        return {"response": f"حدث خطأ: {str(e)}"}
