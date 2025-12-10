import asyncio
import logging
import datetime
from typing import List, Dict, Any, Optional
from haitham_voice_agent.dispatcher import get_dispatcher

logger = logging.getLogger(__name__)

class SystemGuardian:
    """
    The Guardian: A proactive background system for HVA.
    Monitors tasks, calendar, and system state to provide intelligent reminders and context.
    """
    
    def __init__(self):
        self.running = False
        self.check_interval = 60 # Seconds
        self.last_check = datetime.datetime.now()
        self.reminded_events = set() # Track IDs to avoid spam
        
    async def start_monitoring(self):
        """Start the main Guardian loop"""
        if self.running:
            return
            
        self.running = True
        logger.info("🛡️ Guardian System Activated")
        
        while self.running:
            try:
                await self._check_schedule()
                # await self._check_system_health() # Future
            except Exception as e:
                logger.error(f"Guardian Loop Error: {e}")
                
            await asyncio.sleep(self.check_interval)
            
    async def stop(self):
        self.running = False
        logger.info("🛡️ Guardian System Stopped")

    async def _check_schedule(self):
        """Check for upcoming tasks and calendar events"""
        dispatcher = get_dispatcher()
        calendar = dispatcher.tools.get("calendar")
        tasks = dispatcher.tools.get("tasks")
        
        if not calendar:
            return

        now = datetime.datetime.now().astimezone()
        
        # 1. Check Calendar (Next 30 mins)
        try:
            # We use list_events with "upcoming" but filter manually for short term
            result = await calendar.list_events(day_str="today")
            if result.get("success"):
                for event in result.get("events", []):
                    event_id = event.get("id")
                    if event_id in self.reminded_events:
                        continue
                        
                    start_str = event.get("start")
                    # Handle ISO string or dict
                    start_dt = None
                    if isinstance(start_str, str):
                        try:
                            start_dt = datetime.datetime.fromisoformat(start_str)
                        except: pass
                    elif isinstance(start_str, dict):
                         # Google dict (dateTime or date)
                         pass # Usually already parsed by list_events to ISO string if possible?
                         # Wait, list_events returns cleaned dicts. Let's check format.
                    
                    if not start_dt:
                        continue
                        
                    # Calculate time diff
                    # Ensure start_dt is timezone aware
                    if start_dt.tzinfo is None:
                        start_dt = start_dt.astimezone()
                        
                    diff = (start_dt - now).total_seconds() / 60
                    
                    # Notify if within 15 mins
                    if 0 < diff <= 15:
                        await self._announce(f"تذكير: لديك موعد '{event.get('summary')}' بعد {int(diff)} دقيقة.")
                        self.reminded_events.add(event_id)
                        
        except Exception as e:
            logger.warning(f"Guardian Schedule Check Failed: {e}")

    async def _announce(self, message: str):
        """Announce via TTS and Frontend Toast"""
        logger.info(f"🛡️ Guardian Announce: {message}")
        
        dispatcher = get_dispatcher()
        
        # 1. Frontend Notification (via WebSocket)
        from api.connection_manager import manager
        await manager.broadcast({
            "type": "notification",
            "message": message,
            "level": "info"
        })
        
        # 2. Voice (Optional - check config or context)
        # For now, we assume active mode if user is near (not implemented yet), so we just speak
        # But we don't want to interrupt.
        # Let's use the 'speak' tool if available, but maybe with a 'notification' priority?
        # For this MVP, we will just log and push to WS. 
        # Voice announcement logic needs a dedicated "interrupt" mode which we don't have safe yet.
        
