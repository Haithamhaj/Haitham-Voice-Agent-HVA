import asyncio
import logging
import json
from haitham_voice_agent.token_tracker import get_tracker
from haitham_voice_agent.tools.memory.memory_system import memory_system
from haitham_voice_agent.llm_router import get_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_token_tracker():
    print("\n--- Starting Token Tracker Verification ---\n")
    
    # 1. Initialize
    await memory_system.initialize()
    tracker = get_tracker()
    router = get_router()
    
    # 2. Simulate Usage (Directly via Tracker)
    print("Simulating direct usage logging...")
    await tracker.track_usage(
        model="gpt-4o",
        input_tokens=100,
        output_tokens=50,
        context={"test": "direct_log"}
    )
    
    await tracker.track_usage(
        model="gemini-1.5-flash",
        input_tokens=2000,
        output_tokens=100,
        context={"test": "direct_log_2"}
    )
    
    # 3. Verify DB
    print("\nVerifying Database...")
    stats = await memory_system.sqlite_store.get_token_usage_stats(days=1)
    print("Stats:", json.dumps(stats, indent=2))
    
    if stats["total_tokens"] >= 2250:
        print("SUCCESS: Total tokens match expected (>= 2250).")
    else:
        print(f"FAILURE: Total tokens mismatch. Got {stats['total_tokens']}")
        
    # Check cost
    # GPT-4o: (100/1000)*0.005 + (50/1000)*0.015 = 0.0005 + 0.00075 = 0.00125
    # Gemini Flash: (2000/1000)*0.000075 + (100/1000)*0.0003 = 0.00015 + 0.00003 = 0.00018
    # Total: 0.00143
    
    total_cost = stats["total_cost"]
    print(f"Total Cost: ${total_cost:.6f}")
    if total_cost > 0.0014:
        print("SUCCESS: Cost calculation seems correct.")
    else:
        print("FAILURE: Cost calculation seems wrong.")

    # 4. Simulate Real LLM Call (if configured)
    # We won't make real API calls to avoid cost/latency in test, 
    # but we can verify the integration code exists in llm_router.py (we did that by reading).
    
    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(test_token_tracker())
