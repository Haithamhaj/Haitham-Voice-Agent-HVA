import os
import sys
import asyncio
import aiohttp
import importlib
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from haitham_voice_agent.config import Config

async def check_ollama():
    print("\n🔍 Checking Ollama Connectivity...")
    url = f"{Config.OLLAMA_BASE_URL}/api/tags"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    models = [m['name'] for m in data['models']]
                    print(f"✅ Ollama is UP. Available models: {models}")
                    if Config.OLLAMA_MODEL in models:
                        print(f"✅ Model '{Config.OLLAMA_MODEL}' found.")
                        return True
                    else:
                        print(f"⚠️ Model '{Config.OLLAMA_MODEL}' NOT found in list.")
                        return False
                else:
                    print(f"❌ Ollama returned status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Ollama Connection Failed: {e}")
        return False

def check_env_vars():
    print("\n🔍 Checking Environment Variables...")
    required = ["OPENAI_API_KEY", "GEMINI_API_KEY"]
    all_good = True
    for var in required:
        val = os.getenv(var) or getattr(Config, var, None)
        if val:
            print(f"✅ {var} is set.")
        else:
            print(f"❌ {var} is MISSING.")
            all_good = False
    return all_good

def check_imports():
    print("\n🔍 Checking Critical Imports...")
    modules = [
        "haitham_voice_agent.main",
        "haitham_voice_agent.hva_menubar",
        "haitham_voice_agent.ollama_orchestrator",
        "haitham_voice_agent.llm_router",
        "haitham_voice_agent.gui_process"
    ]
    all_good = True
    for mod in modules:
        try:
            importlib.import_module(mod)
            print(f"✅ Import successful: {mod}")
        except Exception as e:
            print(f"❌ Import FAILED: {mod} -> {e}")
            all_good = False
    return all_good

async def main():
    print("🏥 HVA System Health Check")
    print("==========================")
    
    env_ok = check_env_vars()
    imports_ok = check_imports()
    ollama_ok = await check_ollama()
    
    print("\n==========================")
    if env_ok and imports_ok and ollama_ok:
        print("✅ SYSTEM STATUS: HEALTHY")
        print("You can launch the app safely.")
    else:
        print("❌ SYSTEM STATUS: UNHEALTHY")
        print("Please fix the errors above before launching.")

if __name__ == "__main__":
    asyncio.run(main())
