import asyncio
import logging
import sys
import time
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.append("/Users/haitham/development/Haitham Voice Agent (HVA)")

from haitham_voice_agent.tools.reminders import RemindersTool
from haitham_voice_agent.tools.reminders_watcher import RemindersWatcher
import haitham_voice_agent.tools.reminders_watcher

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_reminders_sync():
    print("Starting Reminders Sync Test...")
    
    # 1. Setup Tool
    tool = RemindersTool()
    list_name = "HVA_Test_Inbox" # Use a test list to avoid messing with real data
    
    # Ensure list exists
    logger.info(f"Creating test list: {list_name}")
    tool.ensure_list_exists(list_name)
    
    # 2. Add Dummy Task
    task_title = f"Test Task {int(time.time())}"
    logger.info(f"Adding task: {task_title}")
    tool.add_task(task_title, list_name)
    
    # Verify task exists
    tasks = tool.fetch_inbox_tasks(list_name)
    assert task_title in tasks, "Task was not added to Reminders"
    logger.info("✅ Task added successfully.")
    
    # 3. Mock Memory Manager
    mock_memory_manager = MagicMock()
    mock_memory_manager.save_thought = AsyncMock(return_value={"success": True})
    
    # Patch get_memory_manager in reminders_watcher module
    haitham_voice_agent.tools.reminders_watcher.get_memory_manager = lambda: mock_memory_manager
    
    # 4. Run Watcher Logic (Real Thread)
    logger.info("Running watcher logic...")
    watcher = RemindersWatcher(interval=1, list_name=list_name)
    watcher.start()
    
    # Give it time to process
    time.sleep(5)
    
    watcher.stop()
    watcher.join()
    
    # 5. Verify Results
    
    # Check if memory saved
    mock_memory_manager.save_thought.assert_called()
    call_args = mock_memory_manager.save_thought.call_args
    assert f"Imported from iPhone: {task_title}" in call_args.kwargs['content']
    logger.info("✅ Task saved to memory.")
    
    # Wait for Reminders to update
    time.sleep(2)
    
    # Check if task marked complete
    remaining_tasks = tool.fetch_inbox_tasks(list_name)
    assert task_title not in remaining_tasks, "Task was not marked complete"
    logger.info("✅ Task marked complete.")
    
    print("🎉 Reminders Sync Test Passed!")

if __name__ == "__main__":
    asyncio.run(test_reminders_sync())
