import logging
import subprocess
from typing import List, Optional

logger = logging.getLogger(__name__)

class RemindersTool:
    """
    Tool for interacting with Apple Reminders via AppleScript.
    Acts as a bridge for iPhone sync.
    """
    
    def __init__(self):
        pass

    def _run_applescript(self, script: str) -> Optional[str]:
        """Run an AppleScript command and return the output."""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"AppleScript error: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"Failed to run AppleScript: {e}")
            return None

    def ensure_list_exists(self, list_name: str = "HVA_Inbox") -> bool:
        """Ensure the specified Reminders list exists."""
        script = f'''
        tell application "Reminders"
            if not (exists list "{list_name}") then
                make new list with properties {{name:"{list_name}"}}
            end if
        end tell
        '''
        return self._run_applescript(script) is not None

    def fetch_inbox_tasks(self, list_name: str = "HVA_Inbox") -> List[str]:
        """
        Fetch all incomplete tasks from the specified list.
        Returns a list of task titles.
        """
        # First ensure list exists
        self.ensure_list_exists(list_name)
        
        script = f'''
        tell application "Reminders"
            set myList to list "{list_name}"
            set taskNames to name of (reminders of myList where completed is false)
            
            -- Join with delimiter to parse in Python
            set AppleScript's text item delimiters to "|||"
            return taskNames as string
        end tell
        '''
        
        output = self._run_applescript(script)
        if not output:
            return []
            
        # Split by delimiter
        tasks = [t.strip() for t in output.split("|||") if t.strip()]
        return tasks

    def mark_complete(self, task_name: str, list_name: str = "HVA_Inbox") -> bool:
        """Mark a specific task as completed."""
        # Escape quotes in task name
        safe_name = task_name.replace('"', '\\"')
        
        script = f'''
        tell application "Reminders"
            set myList to list "{list_name}"
            set myTask to (first reminder of myList where name is "{safe_name}" and completed is false)
            set completed of myTask to true
        end tell
        '''
        result = self._run_applescript(script)
        if result is None:
            logger.error(f"Failed to mark task '{task_name}' as complete.")
            return False
        return True

    def add_task(self, title: str, list_name: str = "HVA_Inbox") -> bool:
        """Add a task to the list (useful for testing/feedback)."""
        safe_title = title.replace('"', '\\"')
        script = f'''
        tell application "Reminders"
            if not (exists list "{list_name}") then
                make new list with properties {{name:"{list_name}"}}
            end if
            tell list "{list_name}"
                make new reminder with properties {{name:"{safe_title}"}}
            end tell
        end tell
        '''
        return self._run_applescript(script) is not None
