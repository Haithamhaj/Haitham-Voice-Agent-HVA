import os
import logging
import subprocess
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SystemTools:
    """
    Tools for controlling macOS system functions.
    """
    
    def __init__(self):
        logger.info("SystemTools initialized")

    async def open_app(self, app_name: str) -> Dict[str, Any]:
        """
        Open an application by name.
        """
        try:
            # Sanitize app name slightly to prevent injection, though open -a is relatively safe with quotes
            app_name = app_name.replace('"', '')
            
            cmd = f'open -a "{app_name}"'
            ret = os.system(cmd)
            
            if ret == 0:
                return {"success": True, "message": f"Opened {app_name}"}
            else:
                return {"success": False, "message": f"Failed to open {app_name}. App might not be found."}
                
        except Exception as e:
            logger.error(f"Failed to open app: {e}")
            return {"success": False, "message": str(e)}

    async def set_volume(self, level: int) -> Dict[str, Any]:
        """
        Set system volume (0-100).
        """
        try:
            level = max(0, min(100, level))
            cmd = f"osascript -e 'set volume output volume {level}'"
            subprocess.run(cmd, shell=True, check=True)
            return {"success": True, "message": f"Volume set to {level}%"}
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return {"success": False, "message": str(e)}

    async def mute_volume(self) -> Dict[str, Any]:
        """Mute system volume."""
        try:
            cmd = "osascript -e 'set volume output muted true'"
            subprocess.run(cmd, shell=True, check=True)
            return {"success": True, "message": "Volume muted"}
        except Exception as e:
            logger.error(f"Failed to mute: {e}")
            return {"success": False, "message": str(e)}

    async def unmute_volume(self) -> Dict[str, Any]:
        """Unmute system volume."""
        try:
            cmd = "osascript -e 'set volume output muted false'"
            subprocess.run(cmd, shell=True, check=True)
            return {"success": True, "message": "Volume unmuted"}
        except Exception as e:
            logger.error(f"Failed to unmute: {e}")
            return {"success": False, "message": str(e)}

    async def sleep_display(self) -> Dict[str, Any]:
        """Put display to sleep."""
        try:
            cmd = "pmset displaysleepnow"
            subprocess.run(cmd, shell=True, check=True)
            return {"success": True, "message": "Display sleeping"}
        except Exception as e:
            logger.error(f"Failed to sleep display: {e}")
            return {"success": False, "message": str(e)}

    async def notify(self, title: str, message: str, sound: str = "Ping") -> Dict[str, Any]:
        """
        Send a macOS notification.
        """
        try:
            # Escape quotes
            title = title.replace('"', '\\"')
            message = message.replace('"', '\\"')
            
            cmd = f'osascript -e \'display notification "{message}" with title "{title}" sound name "{sound}"\''
            subprocess.run(cmd, shell=True, check=True)
            return {"success": True, "message": "Notification sent"}
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return {"success": False, "message": str(e)}

    async def show_files(self, path: str = ".") -> Dict[str, Any]:
        """
        List files in a directory, categorized by date.
        """
        try:
            # Resolve path
            if path.lower() in ["downloads", "download"]:
                path = os.path.expanduser("~/Downloads")
            elif path.lower() in ["desktop", "desk"]:
                path = os.path.expanduser("~/Desktop")
            elif path.lower() in ["documents", "docs"]:
                path = os.path.expanduser("~/Documents")
            else:
                path = os.path.expanduser(path)
                
            if not os.path.exists(path):
                return {"success": False, "message": f"Path not found: {path}"}
                
            files = []
            for f in os.listdir(path):
                full_path = os.path.join(path, f)
                if os.path.isfile(full_path) and not f.startswith('.'):
                    stat = os.stat(full_path)
                    files.append({
                        "name": f,
                        "mtime": stat.st_mtime,
                        "size": stat.st_size
                    })
            
            # Sort by mtime desc
            files.sort(key=lambda x: x["mtime"], reverse=True)
            
            # Categorize
            import datetime
            now = datetime.datetime.now()
            today = []
            yesterday = []
            older = []
            
            for f in files:
                mtime = datetime.datetime.fromtimestamp(f["mtime"])
                delta = now - mtime
                
                if delta.days == 0 and now.day == mtime.day:
                    today.append(f["name"])
                elif delta.days <= 1:
                    yesterday.append(f["name"])
                else:
                    older.append(f["name"])
            
            # Format output
            output = []
            if today:
                output.append("📅 Today:")
                output.extend([f"  • {f}" for f in today[:5]])
                if len(today) > 5: output.append(f"  ... and {len(today)-5} more")
                
            if yesterday:
                output.append("\n📅 Yesterday:")
                output.extend([f"  • {f}" for f in yesterday[:5]])
                if len(yesterday) > 5: output.append(f"  ... and {len(yesterday)-5} more")
                
            if older:
                output.append("\n📅 Older:")
                output.extend([f"  • {f}" for f in older[:5]])
                if len(older) > 5: output.append(f"  ... and {len(older)-5} more")
                
            if not output:
                return {"success": True, "message": "No files found.", "data": "Folder is empty."}
                
            result_str = "\n".join(output)
            return {"success": True, "message": f"Found {len(files)} files in {path}", "data": result_str}
            
        except Exception as e:
            logger.error(f"Failed to show files: {e}")
            return {"success": False, "message": str(e)}
