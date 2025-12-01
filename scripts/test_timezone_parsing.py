import dateparser
import datetime
import pytz

def test_parsing(date_string):
    print(f"--- Parsing: '{date_string}' ---")
    
    # Test 1: Default
    dt = dateparser.parse(date_string)
    print(f"Default: {dt} (tzinfo={dt.tzinfo if dt else 'None'})")
    
    # Test 2: With settings
    settings = {
        'RETURN_AS_TIMEZONE_AWARE': True,
        'PREFER_DATES_FROM': 'future'
    }
    dt_aware = dateparser.parse(date_string, settings=settings)
    print(f"Aware:   {dt_aware} (tzinfo={dt_aware.tzinfo if dt_aware else 'None'})")

    if dt_aware:
        # Convert to UTC
        dt_utc = dt_aware.astimezone(pytz.UTC)
        print(f"UTC:     {dt_utc}")
        
        # Convert to Riyadh (UTC+3)
        dt_riyadh = dt_aware.astimezone(pytz.timezone('Asia/Riyadh'))
        print(f"Riyadh:  {dt_riyadh}")

print("System Timezone:", datetime.datetime.now().astimezone().tzinfo)

test_parsing("5:00 PM")
test_parsing("5:00 PM Cairo time")
test_parsing("5:00 PM Egypt time")
test_parsing("17:00 in Cairo")
