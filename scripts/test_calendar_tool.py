import asyncio
import logging
import sys
import datetime
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append("/Users/haitham/development/Haitham Voice Agent (HVA)")

from haitham_voice_agent.tools.calendar import CalendarTools

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_calendar_logic():
    print("Starting Calendar Tool Logic Test...")
    
    # Mock Service
    mock_service = MagicMock()
    
    # Mock list events response
    now = datetime.datetime.now()
    event_time = now.replace(hour=14, minute=0)
    
    mock_events = {
        'items': [
            {
                'summary': 'Test Meeting',
                'start': {'dateTime': event_time.isoformat() + 'Z'},
                'htmlLink': 'http://google.com/calendar/event'
            }
        ]
    }
    
    mock_service.events().list().execute.return_value = mock_events
    mock_service.events().insert().execute.return_value = {'id': '123', 'htmlLink': 'link'}

    # Patch build to return mock service
    with patch('haitham_voice_agent.tools.calendar.build', return_value=mock_service):
        with patch.object(CalendarTools, '_get_credentials', return_value=True):
            
            tool = CalendarTools()
            
            # 1. Test list_events with "today"
            print("\nTesting list_events('today')...")
            res = await tool.list_events("today")
            print(res)
            assert res['success']
            assert res['count'] == 1
            assert res['events'][0]['summary'] == 'Test Meeting'
            
            # Verify date parsing logic (roughly)
            # The mock returns the same event regardless of input, but we check if it didn't crash
            
            # 2. Test check_availability
            print("\nTesting check_availability('today')...")
            res = await tool.check_availability("today")
            print(res)
            assert res['success']
            assert res['status'] == 'busy' # Because we mocked 1 event
            assert "You have 1 events" in res['message']
            
            # 3. Test create_event with natural language
            print("\nTesting create_event('Meeting', 'tomorrow at 5pm')...")
            res = await tool.create_event("Meeting", "tomorrow at 5pm")
            print(res)
            assert res['success']
            
            # Verify insert called
            mock_service.events().insert.assert_called()
            
            print("\n✅ Calendar Logic Test Passed!")

if __name__ == "__main__":
    asyncio.run(test_calendar_logic())
