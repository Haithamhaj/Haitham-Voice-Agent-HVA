
import argparse
import sys
import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Configuration
BASE_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
# V2.5 Path
ADAPTER_PATH = "models/hva_haithm_style_lora_v2"

def main():
    parser = argparse.ArgumentParser(description="Haithm Style V2.5 Inference Check")
    parser.add_argument("--prompt", type=str, help="Text prompt to generate from")
    parser.add_argument("--device", type=str, default="auto", help="Device to run on (cuda, mps, cpu, auto)")
    
    args = parser.parse_args()
    
    prompt = args.prompt
    if not prompt:
        print("Enter prompt (Ctrl+D to finish):")
        prompt = sys.stdin.read().strip()
        
    if not prompt:
        print("No prompt provided. Exiting.")
        return

    # Device Detection
    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    else:
        device = args.device
        
    print(f"🔹 Loading Model on {device}...")
    
    # Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME, trust_remote_code=True)
    
    # Load Base Model
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
        device_map=device,
        trust_remote_code=True
    )
    
    # Load V2.5 Adapter
    print(f"🔸 Loading V2.5 Adapter from: {ADAPTER_PATH}")
    try:
        model = PeftModel.from_pretrained(model, ADAPTER_PATH)
        print("✅ Adapter Loaded Successfully!")
    except Exception as e:
        print(f"❌ Error loading adapter: {e}")
        return

    # Inference
    print(f"\n💬 Generating Response for: '{prompt}'")
    print("-" * 50)
    
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    start_time = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    end_time = time.time()
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    print(response.strip())
    print("-" * 50)
    print(f"⏱️ Time: {end_time - start_time:.2f}s")

if __name__ == "__main__":
    main()
