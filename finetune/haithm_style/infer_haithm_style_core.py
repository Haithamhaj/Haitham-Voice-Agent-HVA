import torch
import time
import threading
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

from haitham_voice_agent.config import Config

# Configuration
BASE_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
# Fallback to config path, or default if not set (though Config should have it)
ADAPTER_PATH = str(Config.HAITHM_STYLE_MODEL_PATH)

# GLOBAL CACHE
_CACHED_MODEL = None
_CACHED_TOKENIZER = None
_INFERENCE_LOCK = threading.Lock()

def get_model_and_tokenizer(adapter_path=ADAPTER_PATH):
    global _CACHED_MODEL, _CACHED_TOKENIZER
    
    if _CACHED_MODEL is not None and _CACHED_TOKENIZER is not None:
        return _CACHED_MODEL, _CACHED_TOKENIZER
        
    print("Loading model into cache...")
    # Device Detection
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
        device_map=device,
        trust_remote_code=True
    )
    
    try:
        model.load_adapter(adapter_path, adapter_name="haithm_v2")
        model.set_adapter("haithm_v2")
    except Exception as e:
        print(f"Warning: Adapter load failed: {e}")
        
    _CACHED_MODEL = model
    _CACHED_TOKENIZER = tokenizer
    return model, tokenizer

def compare_base_vs_haithm_v1(prompt: str,
                              max_new_tokens: int = 256,
                              temperature: float = 0.7,
                              top_p: float = 0.9) -> dict:
    """
    Returns a dict with:
    {
      "prompt": prompt,
      "base_response": "...",
      "haithm_v1_response": "...",
      "base_runtime_sec": float,
      "haithm_v1_runtime_sec": float,
      "device": "mps" | "cpu" | "cuda",
      "model_info": { ... }
    }
    """
    # Device Detection
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    
    try:
        model, tokenizer = get_model_and_tokenizer()
    except Exception as e:
        return {"error": str(e), "base_response": "", "haithm_v1_response": str(e)}

    # Same logic as chat_with_model but returning both
    # For now, let's keep it simple or redirect to chat_with_model called twice?
    # Actually, we can reuse logic or just implement quickly.
    
    messages = [{"role": "user", "content": prompt}]
    
    # Base
    res_base = chat_with_model(messages, mode="base", max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p)
    if "error" in res_base: return res_base
    
    # Adapter
    res_v2 = chat_with_model(messages, mode="haithm_v2", max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p)
    if "error" in res_v2: return res_v2
    
    return {
        "prompt": prompt,
        "base_response": res_base["content"],
        "haithm_v1_response": res_v2["content"], # legacy name v1 for frontend
        "base_runtime_sec": res_base["metadata"]["duration"],
        "haithm_v1_runtime_sec": res_v2["metadata"]["duration"],
        "device": device,
        "model_info": {
            "base": BASE_MODEL_NAME,
            "adapter": ADAPTER_PATH,
            "adapter_available": True
        }
    }

def chat_with_model(messages: list,
                    mode: str = "haithm_v2", # "base" or "haithm_v2"
                    max_new_tokens: int = 512,
                    temperature: float = 0.7,
                    top_p: float = 0.9) -> dict:
    """
    Stateful-like chat inference.
    messages: [{"role": "user", "content": "..."}, ...]
    """
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    
    try:
        model, tokenizer = get_model_and_tokenizer()
    except Exception as e:
         return {"error": f"Model load failed: {e}"}

    # Format Prompt (Applied to both for fair Instruct comparison)
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    model_inputs = tokenizer([text], return_tensors="pt").to(device)
    
    # ACQUIRE LOCK to prevent adapter switching race conditions
    with _INFERENCE_LOCK:
        start_time = time.time()
        generated_ids_full = None
    
        if mode == "base":
            # Base Model Context
            # disable_adapters is not a context manager in this version, it's a method
            model.disable_adapters()
            try:
                with torch.no_grad():
                    generated_ids_full = model.generate(
                        model_inputs.input_ids,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        do_sample=True,
                        pad_token_id=tokenizer.eos_token_id
                    )
            finally:
                # Re-enable for safety (though next call will set adapter)
                model.enable_adapters()
        else:
            # Adapter Context
            try:
                model.set_adapter("haithm_v2")
            except:
                 # Try loading if not set
                 try:
                     model.load_adapter(ADAPTER_PATH, adapter_name="haithm_v2")
                     model.set_adapter("haithm_v2")
                 except Exception as e:
                     return {"error": f"Adapter set failed: {e}"}
    
            with torch.no_grad():
                generated_ids_full = model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
        
        # Trim input
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids_full)
        ]
        
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        duration = time.time() - start_time
    
    return {
        "role": "assistant",
        "content": response,
        "metadata": {
            "duration": duration,
            "model": mode
        }
    }

