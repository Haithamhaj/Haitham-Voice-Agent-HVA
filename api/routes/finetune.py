import os
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from haitham_voice_agent.config import Config
from haitham_voice_agent.llm_router import get_router, LLMType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/finetune", tags=["finetune"])

# Pydantic Models
class ComparisonRequest(BaseModel):
    prompt: str

class ChatRequest(BaseModel):
    model_provider: str  # "gpt" or "gemini"
    messages: List[Dict[str, str]]

# Endpoints

@router.get("/status")
async def get_finetune_status():
    """
    Check existence of dataset and fine-tuned model.
    """
    dataset_path = Config.HVA_HOME.parent / "data/dataset_hva_qwen_routing.jsonl" # Assuming relative to project root, adjusting based on HVA_HOME needing care. 
    # Actually Config.FINETUNE_DATASET_PATH is relative to where process runs?
    # Let's use the project root logic from api/main.py but we don't have it here directly.
    # Config.HVA_HOME might be ~/.hva. 
    # Let's assume the user runs from project root.
    
    # Re-reading Config:
    # FINETUNE_DATASET_PATH: str = "data/dataset_hva_qwen_routing.jsonl"
    
    project_root = Path.cwd()
    dataset_full_path = project_root / Config.FINETUNE_DATASET_PATH
    model_full_path = project_root / Config.FINETUNE_MODEL_PATH
    
    return {
        "dataset_exists": dataset_full_path.exists(),
        "dataset_path": str(Config.FINETUNE_DATASET_PATH) if dataset_full_path.exists() else None,
        "finetuned_model_exists": model_full_path.exists(),
        "finetuned_model_path": str(Config.FINETUNE_MODEL_PATH) if model_full_path.exists() else None,
        "base_model": Config.FINETUNE_BASE_MODEL,
        "finetuned_model_name": Config.FINETUNE_TRAINED_MODEL
    }

@router.get("/dataset/preview")
async def get_dataset_preview(limit: int = 20):
    """
    Preview the first N lines of the dataset.
    """
    project_root = Path.cwd()
    dataset_full_path = project_root / Config.FINETUNE_DATASET_PATH
    
    if not dataset_full_path.exists():
        return []
        
    preview = []
    try:
        with open(dataset_full_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= limit:
                    break
                try:
                    data = json.loads(line)
                    # Filter for display
                    preview.append({
                        "instruction": data.get("instruction", "")[:100] + "...",
                        "input": data.get("input", "")[:100] + "...",
                        "output": data.get("output", "")[:100] + "..."
                    })
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        logger.error(f"Error reading dataset: {e}")
        raise HTTPException(status_code=500, detail="Error reading dataset file")
        
    return preview

@router.post("/compare")
async def compare_models(request: ComparisonRequest):
    """
    Compare Base vs Finetuned model response.
    """
    router = get_router()
    prompt = request.prompt
    
    try:
        # Base Model Call
        import time
        start_base = time.time()
        base_resp = await router.generate_with_local(
            prompt=prompt,
            model=Config.FINETUNE_BASE_MODEL,
        )
        latency_base = int((time.time() - start_base) * 1000)
        
        # Finetuned Model Call
        # Only call if user has it configured/available, otherwise simulate or error?
        # For now we attempt it. If Ollama doesn't have it, it will fail.
        # We wrap in try block to handle "model not found" gracefully?
        
        finetuned_resp_content = ""
        latency_ft = 0
        ft_available = False
        
        try:
            start_ft = time.time()
            ft_resp = await router.generate_with_local(
                prompt=prompt,
                model=Config.FINETUNE_TRAINED_MODEL,
            )
            latency_ft = int((time.time() - start_ft) * 1000)
            finetuned_resp_content = ft_resp["content"]
            ft_available = True
        except Exception as e:
            logger.warning(f"Finetuned model call failed: {e}")
            finetuned_resp_content = f"Model {Config.FINETUNE_TRAINED_MODEL} not available or failed: {str(e)}"
            
        return {
            "prompt": prompt,
            "base": {
                "model": Config.FINETUNE_BASE_MODEL,
                "response": base_resp["content"],
                "latency_ms": latency_base
            },
            "finetuned": {
                "model": Config.FINETUNE_TRAINED_MODEL,
                "response": finetuned_resp_content,
                "latency_ms": latency_ft,
                "available": ft_available
            }
        }
        
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tutor-chat")
async def tutor_chat(request: ChatRequest):
    """
    Educational chat with pure AI context about fine-tuning.
    """
    llm_router = get_router()
    
    # 1. Build System Prompt with Context
    # We could fetch real status here to inject into prompt
    status = await get_finetune_status()
    
    system_prompt = f"""
You are the Finetuning Tutor for the HVA Fine-Tuning Lab.

You have three responsibilities:
1) Explain the content and sections of the 'HVA Fine-Tuning Lab' page in simple, structured language.
2) Answer questions about fine-tuning, QLoRA, datasets, evaluation, and how these concepts apply to HVA.
3) Guide the user step-by-step on how to read and interpret the data shown on this page (status, dataset preview, model comparison).

CURRENT LAB STATUS:
- Dataset File: {'EXISTS' if status['dataset_exists'] else 'MISSING'} ({status['dataset_path']})
- Finetuned Model: {'EXISTS' if status['finetuned_model_exists'] else 'MISSING'} ({status['finetuned_model_path']})
- Base Model: {status['base_model']}
- Target Model: {status['finetuned_model_name']}

Important constraints:
- Do NOT trigger any actions on the system. You are read-only and purely educational.
- Stay focused on fine-tuning, Qwen/QLoRA, and the current HVA experiment. If the user asks about unrelated topics, gently redirect back to the fine-tuning context.
- When explaining technical ideas, use short steps and concrete examples.
"""

    # 2. Extract last user message to prompt
    # The request.messages is a full history list: [{"role": "...", "content": "..."}]
    # generic generate_with_gpt/gemini mostly takes a single prompt string + system prompt.
    # But for chat history effectively, we might need to concatenate or rely on the specific method.
    # LLMRouter.generate_with_gpt accepts simple prompt.
    # LLMRouter.generate_with_gemini accepts simple prompt.
    # We will construct a "chat transcript" or just pass the last message?
    # Better to pass last message + history as text context if the router doesn't support full history.
    # Looking at llm_router.py, generate_with_gpt takes `messages` constructed internally from prompt.
    # It does NOT expose sending a full `messages` list.
    # So we must collapse specific history into the prompt or update router (out of scope to refactor router heavily).
    # We will append history to the prompt text.
    
    last_user_msg = request.messages[-1]["content"] if request.messages else "Hello"
    
    # Basic history formatting
    history_text = ""
    if len(request.messages) > 1:
        history_text = "Chat History:\n"
        for msg in request.messages[:-1]:
            history_text += f"{msg['role'].upper()}: {msg['content']}\n"
        history_text += "\n(End of History)\n"
    
    full_prompt = f"{history_text}\nUser's Question: {last_user_msg}"
    
    response = {"content": "", "model": ""}
    
    if request.model_provider.lower() == "gemini":
        response = await llm_router.generate_with_gemini(
            prompt=full_prompt,
            system_instruction=system_prompt,
            temperature=0.7,
            logical_model="logical.gemini.flash" # Fast & Good for tutoring
        )
    else:
        # Default to GPT
        response = await llm_router.generate_with_gpt(
            prompt=full_prompt,
            system_instruction=system_prompt,
            temperature=0.7,
            logical_model="logical.mini" # GPT-4o-mini is good for chat
        )
        
    return {
        "messages": [
            {"role": "assistant", "content": response["content"]}
        ]
    }
@router.post("/style-compare")
async def style_compare(request: Dict[str, Any]):
    """
    Compare Base vs Haithm Style V1 using core inference logic.
    """
    # Import inside handler to avoid loading heavy models on app startup
    from finetune.haithm_style.infer_haithm_style_core import compare_base_vs_haithm_v1
    
    prompt = request.get("prompt", "")
    max_new_tokens = request.get("max_new_tokens", 256)
    temperature = request.get("temperature", 0.7)
    top_p = request.get("top_p", 0.9)
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    try:
        # Run in threadpool since it's blocking CPU work
        import asyncio
        import functools
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            functools.partial(
                compare_base_vs_haithm_v1,
                prompt=prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p
            )
        )
        return result
        
    except Exception as e:
        logger.error(f"Style comparison failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
