import asyncio
import logging
from haitham_voice_agent.tools.files import FileTools

# Setup logging
logging.basicConfig(level=logging.INFO)

async def test_sort():
    ft = FileTools()
    path = "/Users/haitham/Documents/Coaching"
    
    print(f"Testing Sort by Date on {path}...")
    
    # Test with English instruction
    print("\n--- Test 1: English 'Sort by date' ---")
    result = await ft.organize_documents(path=path, instruction="Sort by date")
    print(f"Result Message: {result.get('message')}")
    if "Simple Mode" in result.get('message', '') or "الوضع البسيط" in result.get('message', ''):
        print("SUCCESS: Switched to Simple Mode")
    else:
        print("FAILURE: Did not switch to Simple Mode")

    # Test with Arabic instruction
    print("\n--- Test 2: Arabic 'رتب حسب التاريخ' ---")
    result_ar = await ft.organize_documents(path=path, language="Arabic", instruction="رتب حسب التاريخ")
    print(f"Result Message: {result_ar.get('message')}")
    if "الوضع البسيط" in result_ar.get('message', ''):
        print("SUCCESS: Switched to Simple Mode")
    else:
        print("FAILURE: Did not switch to Simple Mode")

if __name__ == "__main__":
    asyncio.run(test_sort())
