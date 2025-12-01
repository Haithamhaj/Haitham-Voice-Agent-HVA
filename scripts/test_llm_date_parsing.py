import asyncio
from haitham_voice_agent.llm_router import LLMRouter
from haitham_voice_agent.config import Config
import datetime

async def test_llm_parsing():
    router = LLMRouter()
    
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    user_query = "meeting at 5:00 PM Cairo time tomorrow"
    
    prompt = f"""
    You are a smart date parser.
    Current Date/Time: {today}
    User Input: "{user_query}"
    
    Task: Convert the user's date/time into ISO 8601 format with the correct timezone offset.
    If the user specifies a city (e.g. Cairo), use that city's current timezone.
    
    Return ONLY the ISO string (e.g. 2025-12-02T17:00:00+02:00). No JSON, no markdown.
    """
    
    print(f"--- Prompting LLM ---")
    print(f"Query: {user_query}")
    
    # Use generic generation (defaults to GPT-4o or Gemini Pro)
    response = await router.generate_execution_plan(prompt) # This returns a dict usually, wait.
    # generate_execution_plan expects a plan.
    # I should use generate_with_gemini or similar, or just use the router's internal model directly if exposed.
    # Actually, LLMRouter doesn't have a simple "generate text" method exposed publicly easily except via specific methods.
    # Let's use `model_router.py` directly or `choose_model`.
    
    # Let's use the `generate_with_gemini` method if available or `generate_plan` logic.
    # Actually, `LLMRouter` has `generate_with_gemini`.
    
    response = await router.generate_with_gemini(prompt)
    print(f"Response: {response}")

if __name__ == "__main__":
    Config.init_gemini_mapping()
    asyncio.run(test_llm_parsing())
