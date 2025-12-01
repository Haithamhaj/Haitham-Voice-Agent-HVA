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

    async def list_events(self, limit: int = 10, days: int = 7) -> Dict[str, Any]:
        """List upcoming events"""
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Calendar not authorized. Please say 'Authorize Calendar'."}
            
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=limit,
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
                "events": formatted_events
            }
            
        except Exception as e:
            logger.error(f"List events failed: {e}")
            return {"error": True, "message": str(e)}

    async def create_event(self, summary: str, start_time: str, duration_minutes: int = 60) -> Dict[str, Any]:
        """Create a new event"""
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Calendar not authorized."}
            
            # Parse start time (expecting ISO format or simple natural language handled by LLM)
            # For simplicity, let's assume LLM gives ISO or we parse it.
            # If LLM gives "tomorrow at 5pm", we rely on LLM to convert to ISO in params.
            
            try:
                start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except:
                # Fallback: try to parse loosely or return error
                return {"error": True, "message": "Invalid date format. Please use ISO format."}
                
            end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)
            
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'UTC', # Should ideally be user's timezone
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            
            return {
                "success": True,
                "message": f"Event created: {event.get('htmlLink')}",
                "event_id": event.get('id')
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
        res = await cal.list_events()
        print(res)
    
    asyncio.run(test())
