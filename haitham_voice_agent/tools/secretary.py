import logging
import datetime
import psutil
import platform
from typing import Dict, Any, List
from pathlib import Path

from haitham_voice_agent.tools.tasks.task_manager import task_manager
from haitham_voice_agent.tools.system_tools import SystemTools

logger = logging.getLogger(__name__)

from haitham_voice_agent.memory.manager import get_memory_manager

class Secretary:
    """
    Executive Secretary Module
    Handles Morning Briefing, Work Modes, and Context Management.
    """
    
    def __init__(self):
        self.system_tools = SystemTools()
        self.memory = get_memory_manager()
        
    async def get_morning_briefing(self) -> Dict[str, Any]:
        """
        Generate a comprehensive morning briefing.
        """
        logger.info("Generating morning briefing...")
        
        # 1. Date & Time
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %d %B %Y")
        time_str = now.strftime("%H:%M")
        
        # 2. Weather (Mock for now, or integrate real API later)
        # In a real app, we'd call a weather API here.
        weather = {
            "condition": "Sunny",
            "temp": "25°C",
            "desc": "Perfect weather for productivity."
        }
        
        # 3. Tasks & Memory Context
        tasks = task_manager.list_tasks(status="open")
        high_priority = [t for t in tasks if "urgent" in t.title.lower() or "important" in t.title.lower()]
        
        # Retrieve recent context from memory
        recent_memories = await self.memory.search("important context for today", limit=3)
        memory_context = "\n".join([f"- {m.content}" for m in recent_memories]) if recent_memories else "No recent important notes."
        
        # 4. System Status
        battery = psutil.sensors_battery()
        battery_percent = battery.percent if battery else 100
        
        # 5. Calendar (Mock)
        # Future: Integrate with Google Calendar via Gmail API or local Calendar
        events = [
            {"time": "10:00 AM", "title": "Team Standup"},
            {"time": "02:00 PM", "title": "Project Review"}
        ]
        
        # --- Smart Feedback Agent (v1.1) ---
        feedback_question = ""
        
        # 1. Context Check (Vibe Check)
        # Assuming we can infer mode or day. For now, check if busy.
        is_busy_day = len(events) > 4
        is_weekend = now.weekday() >= 5 # 5=Sat, 6=Sun
        
        if not is_busy_day and not is_weekend:
            # 2. Fetch Candidates
            stale_projects = await self.memory.sqlite_store.get_stale_items(days=3)
            
            if stale_projects:
                # Pick top 1
                project = stale_projects[0]
                
                # 3. Generate Question (Smart Escalation)
                if project.nag_count == 0:
                    feedback_question = f"\n💡 **Follow-up:** By the way, no updates on *{project.project}* recently. Everything okay?"
                elif project.nag_count in [1, 2]:
                    feedback_question = f"\n🚀 **Action:** *{project.project}* is still active but silent. Do you need to break it down into tasks?"
                else:
                    feedback_question = f"\n🤔 **Strategy:** *{project.project}* seems stuck. Should we move it to 'On Hold' to clear your mind?"
                
                # 4. Update State
                project.nag_count += 1
                await self.memory.sqlite_store.save_memory(project)

        # Format Report
        report = f"""
🌅 **Morning Briefing**
📅 {date_str} | 🕒 {time_str}

🌤️ **Weather**
{weather['condition']}, {weather['temp']}
_{weather['desc']}_

📝 **Tasks**
You have {len(tasks)} pending tasks.
"""
        if high_priority:
            report += f"⚠️ **{len(high_priority)} High Priority:**\n"
            for t in high_priority:
                report += f"- {t.title}\n"
        
        report += f"""
🧠 **Memory Context**
{memory_context}
"""
        
        report += f"""
📅 **Schedule**
"""
        for evt in events:
            report += f"- **{evt['time']}**: {evt['title']}\n"
            
        report += f"""
🔋 **System**
Battery: {battery_percent}%
"""

        if feedback_question:
            report += f"{feedback_question}\n"

        return {
            "text": report,
            "data": {
                "weather": weather,
                "tasks_count": len(tasks),
                "events_count": len(events),
                "battery": battery_percent,
                "feedback_question": feedback_question
            }
        }

    async def set_work_mode(self, mode: str) -> str:
        """
        Set the active work mode (context).
        """
        mode = mode.lower()
        logger.info(f"Setting work mode: {mode}")
        
        if "work" in mode or "code" in mode:
            # Open coding apps
            await self.system_tools.open_app("Visual Studio Code")
            await self.system_tools.open_app("iTerm")
            # Set volume moderate
            await self.system_tools.set_volume(40)
            return "🚀 Work Mode Activated.\n- Opened VS Code & Terminal\n- Volume set to 40%"
            
        elif "meeting" in mode:
            # Open notes, mute music (if we could), set volume up
            await self.system_tools.open_app("Notes")
            await self.system_tools.set_volume(80) # Ensure we hear others
            return "👥 Meeting Mode Activated.\n- Opened Notes\n- Volume set to 80%"
            
        elif "chill" in mode or "relax" in mode:
            # Open music
            await self.system_tools.open_app("Spotify")
            await self.system_tools.set_volume(60)
            return "☕ Chill Mode Activated.\n- Opened Spotify\n- Enjoy your break!"
            
        else:
            return f"Unknown mode: {mode}. Try 'Work', 'Meeting', or 'Chill'."

# Singleton
_secretary = None

def get_secretary():
    global _secretary
    if _secretary is None:
        _secretary = Secretary()
    return _secretary
