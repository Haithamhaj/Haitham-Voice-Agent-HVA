import sys
import os
import threading
import time

# Ensure project root is in path
sys.path.append(os.getcwd())

from finetune.haithm_style.infer_haithm_style_core import chat_with_model, get_model_and_tokenizer

def run_chat(mode):
    print(f"[{mode}] Starting request...")
    try:
        if mode == "base": 
             model, _ = get_model_and_tokenizer()
             print([m for m in dir(model) if "adapter" in m])
        res = chat_with_model(
            messages=[{"role": "user", "content": "hello"}],
            mode=mode,
            max_new_tokens=10 
        )
        print(f"[{mode}] Result: {res}")
    except Exception as e:
        print(f"[{mode}] FAILED: {e}")

def main():
    print("--- 1. Warmup Load ---")
    get_model_and_tokenizer()
    print("--- Warmup Done ---")

    print("\n--- 2. Parallel Test ---")
    t1 = threading.Thread(target=run_chat, args=("base",))
    t2 = threading.Thread(target=run_chat, args=("haithm_v2",))
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    main()
