"""
Calendar Tools

Google Calendar integration for HVA.
Handles events, availability, and scheduling.
"""

import os
import logging
import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from haitham_voice_agent.config import Config
from haitham_voice_agent.tools.gmail.auth.credentials_store import get_credential_store

logger = logging.getLogger(__name__)

class CalendarTools:
    """Google Calendar operations"""
    
    def __init__(self):
        self.service = None
        self.credential_store = get_credential_store()
        self.client_secret_path = Config.CREDENTIALS_DIR / "client_secret.json"
        
        logger.info("CalendarTools initialized")

    def _get_credentials(self) -> Optional[Credentials]:
        """Get valid OAuth credentials for Calendar"""
        try:
            # Try to retrieve existing credentials
            cred_data = self.credential_store.retrieve_credential("calendar_oauth")
            
            if cred_data:
                creds = Credentials(
                    token=cred_data.get("token"),
                    refresh_token=cred_data.get("refresh_token"),
                    token_uri=cred_data.get("token_uri"),
                    client_id=cred_data.get("client_id"),
                    client_secret=cred_data.get("client_secret"),
                    scopes=cred_data.get("scopes")
                )
                
                if creds.expired and creds.refresh_token:
                    logger.info("Calendar token expired, refreshing...")
                    creds.refresh(Request())
                    self._save_credentials(creds)
                
                return creds
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get calendar credentials: {e}")
            return None

    def _save_credentials(self, creds: Credentials) -> bool:
        """Save credentials to store"""
        try:
            cred_data = {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes
            }
            return self.credential_store.store_credential("calendar_oauth", cred_data)
        except Exception as e:
            logger.error(f"Failed to save calendar credentials: {e}")
            return False

    def authorize(self) -> Dict[str, Any]:
        """Initiate OAuth flow"""
        try:
            if not self.client_secret_path.exists():
                return {
                    "error": True,
                    "message": f"client_secret.json not found at {self.client_secret_path}",
                    "suggestion": "Download OAuth credentials from Google Cloud Console"
                }
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.client_secret_path),
                scopes=Config.CALENDAR_SCOPES
            )
            
            creds = flow.run_local_server(port=0, open_browser=True)
            self._save_credentials(creds)
            
            return {"success": True, "message": "Calendar authorized successfully"}
            
        except Exception as e:
            logger.error(f"Authorization failed: {e}")
            return {"error": True, "message": str(e)}

    def _ensure_service(self) -> bool:
        """Ensure API service is ready"""
        if self.service:
            return True
            
        creds = self._get_credentials()
        if not creds:
            return False
            
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            return True
        except Exception as e:
            logger.error(f"Failed to build calendar service: {e}")
            return False

    async def _smart_parse_date(self, date_str: str) -> Optional[datetime.datetime]:
        """Use Gemini to parse natural language date into ISO format"""
        # 1. Check if it's already a datetime object
        if isinstance(date_str, datetime.datetime):
             return date_str
             
        # 2. Check if it's already an ISO string
        try:
            return datetime.datetime.fromisoformat(date_str)
        except ValueError:
            pass
            
        # 3. Try dateparser
        import dateparser
        dt = dateparser.parse(date_str, settings={'PREFER_DATES_FROM': 'future'})
        
        suspicious_keywords = ["time", "in ", "gmt", "utc", "est", "pst", "cairo", "egypt", "saudi", "london", "dubai"]
        is_complex = any(k in date_str.lower() for k in suspicious_keywords)
        
        if dt and not is_complex:
            return dt
            
        # 4. Fallback to LLM (Gemini) for complex parsing
        try:
            from haitham_voice_agent.llm_router import get_router
            router = get_router()
            
            now_str = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
            
            prompt = f"""
            Task: Parse the date/time from the user string into ISO 8601 format with correct timezone offset.
            
            Current System Time: {now_str}
            User Input: "{date_str}"
            
            Rules:
            1. If the user specifies a city/timezone (e.g. "Cairo time"), use that timezone's offset.
            2. If no timezone specified, assume system timezone.
            3. Return ONLY the ISO string (e.g. 2025-12-01T17:00:00+03:00).
            4. If invalid, return "None".
            """
            
            iso_str = await router.generate_with_gemini(prompt, temperature=0.0)
            iso_str = iso_str.strip().replace('"', '').replace("'", "")
            
            if iso_str.lower() == "none":
                return dt # Fallback to whatever dateparser found (or None)
                
            # Parse ISO string
            return datetime.datetime.fromisoformat(iso_str)
            
        except Exception as e:
            logger.error(f"Smart date parsing failed: {e}")
            return dt # Fallback

    async def list_events(self, day_str: str = "today", max_results: int = 10) -> Dict[str, Any]:
        """List upcoming events with natural language date parsing"""
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Calendar not authorized. Please say 'Authorize Calendar'."}
            
            # Parse date range
            base_date = await self._smart_parse_date(day_str)
            
            if not base_date:
                base_date = datetime.datetime.now().astimezone()
            
            # Determine range
            # If "today", range is now -> end of day
            # If "tomorrow", range is 00:00 -> 23:59 tomorrow
            # If specific date, range is 00:00 -> 23:59 that day
            
            now = datetime.datetime.now()
            
            if day_str.lower() in ["today", "اليوم"]:
                time_min = now
                time_max = now.replace(hour=23, minute=59, second=59)
            elif day_str.lower() in ["tomorrow", "بكرة", "غدا"]:
                tomorrow = now + datetime.timedelta(days=1)
                time_min = tomorrow.replace(hour=0, minute=0, second=0)
                time_max = tomorrow.replace(hour=23, minute=59, second=59)
            elif day_str.lower() in ["upcoming", "week", "الاسبوع", "القادم"]:
                # Show next 7 days
                time_min = now
                time_max = now + datetime.timedelta(days=7)
            else:
                # Use parsed date
                time_min = base_date.replace(hour=0, minute=0, second=0)
                time_max = base_date.replace(hour=23, minute=59, second=59)
                
                # If parsed date is in the past (e.g. "Monday" referring to next week but parsed as last week),
                # dateparser usually handles "next monday".
                # If it's today but earlier, clamp min to now if we only want upcoming?
                # The user might want to see past events of the day. Let's keep it as is.

            # Convert to ISO format with Z (UTC) or offset
            # Google API expects RFC3339.
            # We should be careful with timezones. dateparser returns naive or aware.
            # Let's assume system local time for now.
            
            # Convert to ISO format
            # Ensure we have timezone aware objects
            if time_min.tzinfo is None:
                time_min = time_min.astimezone()
            if time_max.tzinfo is None:
                time_max = time_max.astimezone()
                
            time_min_iso = time_min.isoformat()
            time_max_iso = time_max.isoformat()
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min_iso,
                timeMax=time_max_iso,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    "summary": event.get('summary', 'No Title'),
                    "start": start,
                    "link": event.get('htmlLink')
                })
                
            return {
                "success": True,
                "count": len(events),
                "events": formatted_events,
                "period": f"{time_min.strftime('%Y-%m-%d %H:%M')} to {time_max.strftime('%H:%M')}"
            }
            
        except Exception as e:
            logger.error(f"List events failed: {e}")
            return {"error": True, "message": str(e)}

    async def check_availability(self, day_str: str = "today", **kwargs) -> Dict[str, Any]:
        """Check availability for a given day (kwargs like 'time' are ignored for now)"""
        # Reuse list_events logic to get events
        res = await self.list_events(day_str=day_str, max_results=50)
        if res.get("error"):
            return res
            
        events = res.get("events", [])
        count = res.get("count", 0)
        
        if count == 0:
            return {
                "success": True,
                "status": "free",
                "message": f"You are completely free on {day_str}!"
            }
        
        # Simple busy analysis
        # Ideally we calculate free slots, but for now just returning the count and list is good.
        # Let's return a summary string.
        
        summary = f"You have {count} events on {day_str}."
        if count > 5:
            summary += " It's a busy day!"
        elif count < 3:
            summary += " It's a relatively light day."
            
        return {
            "success": True,
            "status": "busy" if count > 0 else "free",
            "message": summary,
            "events": events
        }

    async def create_event(self, summary: str, start_time: str, duration_minutes: int = 60, **kwargs) -> Dict[str, Any]:
        """Create a new event with natural language parsing"""
        # Handle param aliases
        if "duration" in kwargs:
             try:
                 duration_minutes = int(kwargs["duration"])
             except:
                 pass
                 
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Calendar not authorized."}
            
            # Smart Parse start time
            start_dt = await self._smart_parse_date(start_time)
            
            if not start_dt:
                return {"error": True, "message": f"Could not parse date: {start_time}"}
                
            # Check availability (warn if conflict)
            # We check a small window around the start time
            time_min = start_dt
            time_max = start_dt + datetime.timedelta(minutes=duration_minutes)

            # Ensure timezones are handled correctly
            # If naive, assume local system time and convert to aware
            if time_min.tzinfo is None:
                time_min = time_min.astimezone()
            if time_max.tzinfo is None:
                time_max = time_max.astimezone()
            
            time_min_iso = time_min.isoformat()
            time_max_iso = time_max.isoformat()
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min_iso,
                timeMax=time_max_iso,
                singleEvents=True
            ).execute()
            
            conflicts = events_result.get('items', [])
            conflict_warning = ""
            if conflicts:
                conflict_titles = [e.get('summary', 'Event') for e in conflicts]
                conflict_warning = f"Warning: This overlaps with {', '.join(conflict_titles)}."
                # We proceed anyway but return warning
            
            end_dt = time_max
            
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': str(start_dt.tzinfo) if start_dt.tzinfo else 'UTC',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': str(end_dt.tzinfo) if end_dt.tzinfo else 'UTC',
                },
            }
            
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            
            msg = f"Event created: {summary} at {start_dt.strftime('%Y-%m-%d %H:%M')}."
            if conflict_warning:
                msg += f" {conflict_warning}"
            
            return {
                "success": True,
                "message": msg,
                "event_id": event.get('id'),
                "link": event.get('htmlLink'),
                "warning": conflict_warning
            }
            
        except Exception as e:
            logger.error(f"Create event failed: {e}")
            return {"error": True, "message": str(e)}

if __name__ == "__main__":
    # Test
    import asyncio
    async def test():
        cal = CalendarTools()
        # print(cal.authorize()) # Uncomment to auth manually
        print("--- Today ---")
        print(await cal.list_events("today"))
        print("--- Availability Tomorrow ---")
        print(await cal.check_availability("tomorrow"))
    
    asyncio.run(test())
