import sys
import os
import asyncio

# Ensure project root is in path
sys.path.append(os.getcwd())

from finetune.haithm_style.infer_haithm_style_core import chat_with_model

def test_inference():
    print("--- Testing Base Mode ---")
    try:
        res = chat_with_model(
            messages=[{"role": "user", "content": "مرحبا"}],
            mode="base"
        )
        print("Base Result:", res)
    except Exception as e:
        print("Base Mode Crash:", e)
        import traceback
        traceback.print_exc()

    print("\n--- Testing Haithm V2 Mode ---")
    try:
        res = chat_with_model(
            messages=[{"role": "user", "content": "مرحبا"}],
            mode="haithm_v2"
        )
        print("V2 Result:", res)
    except Exception as e:
        print("V2 Mode Crash:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_inference()
