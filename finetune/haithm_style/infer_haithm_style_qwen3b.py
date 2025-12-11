#!/usr/bin/env python3
"""
Haithm Style V1 Inference Comparison
====================================

Purpose:
    Qualitatively compare the base Qwen 2.5 3B model against the V1 Haithm Style LoRA adapter.
    
Usage:
    python finetune/haithm_style/infer_haithm_style_qwen3b.py --prompt "Your prompt here"

"""

import argparse
import sys
import sys
# import torch
# import time
# from transformers import AutoModelForCausalLM, AutoTokenizer
# from peft import PeftModel

# Configuration
BASE_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
ADAPTER_PATH = "models/hva_haithm_style_lora_hs-20251211-v1-text-only"

def generate_response(model, tokenizer, prompt, args, label):
    device = model.device
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    print(f"\n[{label}] Generating...", end="", flush=True)
    start_time = time.time()
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    end_time = time.time()
    elapsed = end_time - start_time
    print(f" Done ({elapsed:.2f}s)")
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Strip the prompt from the response if model echoes it (Qwen usually continues)
    # But strictly speaking, decode includes prompt.
    # We want to show just the new text or the whole thing?
    # Usually "response" is clearer if we strip prompt, but for chat models
    # the prompt formatting might be complex. Qwen Instruct expects Apply Chat Template?
    # For raw completion, we just print what it says. 
    # Let's print the full response but maybe separate prompt visibly.
    
    # Actually, for cleaner output, let's remove the prompt part if it matches exact input
    # BUT, tokenization might differ. 
    # Let's just print the raw decoded text.
    
    print(f"\n[{label}] Response:")
    print("-" * 40)
    print(response.strip())
    print("-" * 40)

def main():
    parser = argparse.ArgumentParser(description="Haithm Style Inference Checker")
    parser.add_argument("--prompt", type=str, help="Text prompt to generate from")
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.9)
    
    args = parser.parse_args()
    
    # Get prompt
    prompt = args.prompt
    if not prompt:
        print("Enter prompt (Ctrl+D to finish):")
        prompt = sys.stdin.read().strip()
        
    if not prompt:
        print("No prompt provided. Exiting.")
        return

    print("=" * 40)
    print(f"PROMPT:\n{prompt}")
    print("=" * 40)

    # Core Inference
    from infer_haithm_style_core import compare_base_vs_haithm_v1
    
    print(f"Running Comparison on device (auto-detect)...")
    result = compare_base_vs_haithm_v1(
        prompt, 
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p
    )
    
    print(f"Device: {result['device']}")
    
    print(f"\n[BASE] Response ({result['base_runtime_sec']:.2f}s):")
    print("-" * 40)
    print(result['base_response'].strip())
    print("-" * 40)

    print(f"\n[HAITHM-V1] Response ({result['haithm_v1_runtime_sec']:.2f}s):")
    print("-" * 40)
    print(result['haithm_v1_response'].strip())
    print("-" * 40)
    
    print("\nComparison Complete.")

if __name__ == "__main__":
    main()
