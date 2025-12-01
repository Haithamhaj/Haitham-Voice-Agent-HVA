import asyncio
import datetime
from haitham_voice_agent.tools.calendar import CalendarTools
from haitham_voice_agent.config import Config

async def test_calendar_timezone():
    Config.init_gemini_mapping()
    cal = CalendarTools()
    
    print("--- Testing Smart Date Parsing ---")
    
    # Test 1: Simple Local Time
    dt1 = await cal._smart_parse_date("5:00 PM tomorrow")
    print(f"Simple: {dt1} (tz={dt1.tzinfo if dt1 else 'None'})")
    
    # Test 2: Cairo Time (Should trigger LLM)
    dt2 = await cal._smart_parse_date("Meeting at 5:00 PM Cairo time tomorrow")
    print(f"Cairo:  {dt2} (tz={dt2.tzinfo if dt2 else 'None'})")
    
    if dt2:
        # Check if it correctly offset (Cairo is usually UTC+2 or +3)
        # System is UTC+3 (Riyadh)
        # If Cairo is UTC+2, then 5:00 PM Cairo = 6:00 PM Riyadh
        # The ISO string should reflect the offset.
        print(f"ISO: {dt2.isoformat()}")

if __name__ == "__main__":
    asyncio.run(test_calendar_timezone())
