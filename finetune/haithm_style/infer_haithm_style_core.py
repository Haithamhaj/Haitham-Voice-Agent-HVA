import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Configuration
BASE_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
ADAPTER_PATH = "models/hva_haithm_style_lora_hs-20251211-v1-text-only"

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
    
    # Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME, trust_remote_code=True)
    
    # Load Base Model
    # Note: On CPU uses float32 to avoid some complex Half issues if backend doesn't support it, 
    # but Qwen usually fine with float16 on MPS.
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
        device_map=device,
        trust_remote_code=True
    )
    
    # --- Base Generation ---
    start_base = time.time()
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs_base = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    base_runtime = time.time() - start_base
    base_response = tokenizer.decode(outputs_base[0], skip_special_tokens=True)
    
    # --- Adapter Generation ---
    # Load Adapter
    # We use load_adapter and set_adapter to switch context
    try:
        model.load_adapter(ADAPTER_PATH, adapter_name="haithm_v1")
        model.set_adapter("haithm_v1")
        adapter_available = True
    except Exception as e:
        print(f"Warning: Could not load adapter from {ADAPTER_PATH}: {e}")
        adapter_available = False
        
    start_adapter = time.time()
    if adapter_available:
        with torch.no_grad():
            outputs_adapter = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        haithm_response = tokenizer.decode(outputs_adapter[0], skip_special_tokens=True)
    else:
        haithm_response = "[Error: Adapter not found or failed to load]"
        
    adapter_runtime = time.time() - start_adapter
    
    return {
        "prompt": prompt,
        "base_response": base_response,
        "haithm_v1_response": haithm_response,
        "base_runtime_sec": base_runtime,
        "haithm_v1_runtime_sec": adapter_runtime,
        "device": device,
        "model_info": {
            "base": BASE_MODEL_NAME,
            "adapter": ADAPTER_PATH,
            "adapter_available": adapter_available
        }
    }
