import os
import sys
import importlib.util
from dotenv import load_dotenv

load_dotenv()

def check_env():
    print("--- Environment Check ---")
    
    nvidia_key = os.environ.get("NVIDIA_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    has_ne_mo = False
    if importlib.util.find_spec("nemo_data_designer") or importlib.util.find_spec("data_designer"):
        has_ne_mo = True
        
    print(f"NVIDIA_API_KEY Present: {bool(nvidia_key)}")
    print(f"OPENAI_API_KEY Present: {bool(openai_key)}")
    print(f"Data Designer Library Installed: {has_ne_mo}")
    
    if not nvidia_key and not openai_key:
        print("ERROR: No API keys found. Cannot proceed with real generation.")
        sys.exit(1)
        
    if nvidia_key:
        print("MODE: HOSTED (Preferred)")
    else:
        print("MODE: OSS (OpenAI Provider)")

if __name__ == "__main__":
    check_env()
