
import sys
import os
from pathlib import Path

# Simulate app environment
sys.path.append(os.getcwd())

print("1. Testing Imports...")
try:
    from haitham_voice_agent.config import Config
    print(f"   Config imported. Model Path: {Config.HAITHM_STYLE_MODEL_PATH}")
except Exception as e:
    print(f"   FAIL: Config import error: {e}")
    sys.exit(1)

print("2. Testing Core Inference Import...")
try:
    from finetune.haithm_style.infer_haithm_style_core import compare_base_vs_haithm_v1
    print("   Core Inference imported.")
except Exception as e:
    print(f"   FAIL: Core import error: {e}")
    # Inspecting the file might help
    print("   Dumping file content headers:")
    with open("finetune/haithm_style/infer_haithm_style_core.py", "r") as f:
        print(f.read()[:200])
    sys.exit(1)

print("3. Testing Inference Call (Dry Run)...")
try:
    # We won't actually run heavy inference if we can avoid it, or maybe just a tiny run?
    # This might load the model which is heavy. 
    # Let's just check if the function exists and arguments match.
    import inspect
    sig = inspect.signature(compare_base_vs_haithm_v1)
    print(f"   Function Signature: {sig}")
    
    # Check if adapter path exists
    adapter_path = Config.HAITHM_STYLE_MODEL_PATH
    if not adapter_path.exists():
        print(f"   WARNING: Adapter path {adapter_path} does not exist!")
    else:
        print(f"   Adapter path confirmed: {adapter_path}")

except Exception as e:
    print(f"   FAIL: Execution setup error: {e}")
    sys.exit(1)

print("✅ DIAGNOSTICS COMPLETE")
