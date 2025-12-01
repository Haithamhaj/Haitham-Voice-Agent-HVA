"""
Notification Manager

Background service for proactive notifications.
Polls Calendar and Gmail to alert the user.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

from haitham_voice_agent.tools.system_tools import SystemTools
from haitham_voice_agent.tools.calendar import CalendarTools
from haitham_voice_agent.tools.gmail.connection_manager import ConnectionManager
from haitham_voice_agent.config import Config

logger = logging.getLogger(__name__)

class NotificationManager:
    """
    Manages background polling and notifications.
    """
    
    def __init__(self, system_tools: SystemTools):
        self.system_tools = system_tools
        self.calendar = CalendarTools()
        self.gmail = ConnectionManager()
        
        self.is_running = False
        self.poll_interval = 300  # 5 minutes
        
        # State tracking to avoid duplicate notifications
        self.notified_events = set()
        self.last_email_id = None
        
        logger.info("NotificationManager initialized")

    async def start(self):
        """Start the background polling loop"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("NotificationManager started")
        
        while self.is_running:
            try:
                await self.check_calendar()
                await self.check_gmail()
            except Exception as e:
                logger.error(f"Notification poll failed: {e}")
            
            # Wait for next poll
            await asyncio.sleep(self.poll_interval)

    def stop(self):
        """Stop the background loop"""
        self.is_running = False
        logger.info("NotificationManager stopped")

    async def check_calendar(self):
        """Check for upcoming events in the next 15 minutes"""
        try:
            # Get events for next 15 mins
            # Note: list_events usually gets next 7 days, we filter here
            res = await self.calendar.list_events(max_results=5)
            
            if res.get("error"):
                return
                
            events = res.get("events", [])
            now = datetime.utcnow()
            warning_window = timedelta(minutes=15)
            
            for event in events:
                # Parse start time
                start_str = event['start']
                # Handle 'date' (all day) vs 'dateTime'
                if 'T' in start_str:
                    start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00')).replace(tzinfo=None)
                    
                    # Check if within window
                    time_until = start_dt - now
                    
                    if timedelta(minutes=0) < time_until <= warning_window:
                        event_id = event['link'] # Use link as ID if ID not available in simplified view
                        
                        if event_id not in self.notified_events:
                            # Notify!
                            title = "📅 Upcoming Event"
                            msg = f"{event['summary']} in {int(time_until.seconds/60)} mins"
                            
                            await self.system_tools.notify(title, msg, sound="Glass")
                            
                            # Mark as notified
                            self.notified_events.add(event_id)
                            
        except Exception as e:
            logger.error(f"Calendar check failed: {e}")

    async def check_gmail(self):
        """Check for new important emails"""
        try:
            # Fetch latest 1 email
            res = await self.gmail.fetch_latest_email(limit=1)
            
            if res.get("error") or res.get("count", 0) == 0:
                return
                
            email = res['emails'][0]
            email_id = email['id']
            
            # Check if new
            if self.last_email_id and email_id != self.last_email_id:
                # Check if unread
                if email['is_unread']:
                    # Notify!
                    title = f"📧 New Email from {email['from']}"
                    msg = email['subject'][:50]
                    
                    await self.system_tools.notify(title, msg, sound="Tink")
            
            self.last_email_id = email_id
            
        except Exception as e:
            logger.error(f"Gmail check failed: {e}")
