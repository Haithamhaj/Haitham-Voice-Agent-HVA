import threading
import time
import logging
import asyncio
from typing import Optional

from haitham_voice_agent.tools.reminders import RemindersTool
from haitham_voice_agent.memory.manager import get_memory_manager

logger = logging.getLogger(__name__)

class RemindersWatcher(threading.Thread):
    """
    Background thread that watches Apple Reminders for new tasks
    and syncs them to HVA Memory.
    """
    
    def __init__(self, interval: int = 60, list_name: str = "HVA_Inbox"):
        super().__init__()
        self.interval = interval
        self.list_name = list_name
        self.tool = RemindersTool()
        self.running = False
        self.daemon = True # Daemon thread exits when main program exits
        self.name = "RemindersWatcher"

    def run(self):
        """Main loop."""
        logger.info(f"RemindersWatcher started (List: {self.list_name}, Interval: {self.interval}s)")
        self.running = True
        
        # Ensure list exists on startup
        self.tool.ensure_list_exists(self.list_name)
        
        while self.running:
            try:
                self._check_for_tasks()
            except Exception as e:
                logger.error(f"Error in RemindersWatcher: {e}")
            
            # Sleep in small chunks to allow faster shutdown
            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)
                
        logger.info("RemindersWatcher stopped.")

    def stop(self):
        """Stop the watcher."""
        self.running = False

    def _check_for_tasks(self):
        """Fetch and process tasks."""
        tasks = self.tool.fetch_inbox_tasks(self.list_name)
        
        if not tasks:
            return

        logger.info(f"Found {len(tasks)} new tasks in Reminders.")
        
        # We need an event loop to call async memory methods
        # Since we are in a thread, we create a new loop or run_coroutine_threadsafe
        # But creating a loop is safer for this isolated thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        memory_manager = get_memory_manager()
        
        for task_text in tasks:
            try:
                logger.info(f"Processing task from iPhone: {task_text}")
                
                # 1. Save to Memory
                # We use run_until_complete since we are in a sync thread
                loop.run_until_complete(
                    memory_manager.save_thought(
                        content=f"Imported from iPhone: {task_text}",
                        project_name="Inbox"
                    )
                )
                
                # 2. Mark as complete in Reminders (so we don't process again)
                self.tool.mark_complete(task_text, self.list_name)
                
            except Exception as e:
                logger.error(f"Failed to process task '{task_text}': {e}")
        
        loop.close()
