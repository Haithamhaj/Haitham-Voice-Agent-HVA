
import asyncio
from haitham_voice_agent.ollama_orchestrator import get_orchestrator

async def test_nlu():
    print("----------------------------------------------------------------")
    print("              NLU ROBUSTNESS TEST (Qwen Local)                  ")
    print("----------------------------------------------------------------")
    
    ollama = get_orchestrator()
    
    # Test 1: Task with "date" and "meeting" keyword
    # Fails if it returns "meeting_mode"
    t1 = "اليوم الساعة 6 في عندي اجتماع مع الشب اللي بدرس طب"
    print(f"\n[1] Check Task: '{t1}'")
    res1 = await ollama.classify_request(t1)
    print(f" -> Result: {res1['type']} / Intent: {res1.get('intent', 'N/A')}")
    
    # Test 2: Complaint (Direct Response vs Rephrase)
    # Fails if it just rephrases the input
    t2 = "ليش فعلت مود الاجتماع انا عطيتك تهمة عشان تسجلها"
    print(f"\n[2] Check Complaint: '{t2}'")
    res2 = await ollama.classify_request(t2)
    print(f" -> Result: {res2['type']}")
    if res2['type'] == 'direct_response':
         print(f" -> Response: {res2.get('response')}")

if __name__ == "__main__":
    asyncio.run(test_nlu())
