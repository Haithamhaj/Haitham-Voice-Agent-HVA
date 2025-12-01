import asyncio
import os
from haitham_voice_agent.tools.system_tools import SystemTools

async def main():
    tools = SystemTools()
    
    print("--- Testing show_files('Downloads') ---")
    # Ensure Downloads exists or use current dir
    path = "Downloads" if os.path.exists(os.path.expanduser("~/Downloads")) else "."
    
    result = await tools.show_files(path)
    
    if result["success"]:
        print("✅ Success!")
        print(f"Message: {result['message']}")
        print("Data:")
        print(result.get("data", "No data"))
    else:
        print("❌ Failed!")
        print(f"Message: {result['message']}")

if __name__ == "__main__":
    asyncio.run(main())
