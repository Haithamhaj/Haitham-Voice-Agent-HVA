import time
import threading
import logging
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

class FileWatcher:
    """
    Monitors key folders for changes and triggers callbacks.
    Uses 'watchdog' if available, otherwise falls back to polling.
    """
    
    def __init__(self, folders: list[str], callback: Callable):
        self.folders = [Path(f).expanduser() for f in folders]
        self.callback = callback
        self.running = False
        self.thread = None
        self.use_polling = False
        
        try:
            import watchdog
            self.use_polling = False
        except ImportError:
            logger.warning("Watchdog library not found. Using polling for file watcher.")
            self.use_polling = True
            
    def start(self):
        """Start the watcher"""
        if self.running: return
        self.running = True
        
        if self.use_polling:
            self.thread = threading.Thread(target=self._poll_loop, daemon=True)
            self.thread.start()
        else:
            self._start_watchdog()
            
    def stop(self):
        """Stop the watcher"""
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
            
    def _poll_loop(self):
        """Simple polling loop (fallback)"""
        snapshots = {f: self._get_snapshot(f) for f in self.folders}
        
        while self.running:
            time.sleep(10) # Poll every 10 seconds
            
            for folder in self.folders:
                current = self._get_snapshot(folder)
                if current != snapshots[folder]:
                    logger.info(f"Change detected in {folder}")
                    snapshots[folder] = current
                    try:
                        self.callback()
                    except Exception as e:
                        logger.error(f"Watcher callback failed: {e}")
                        
    def _get_snapshot(self, folder: Path) -> float:
        """Get modification time of folder"""
        try:
            return folder.stat().st_mtime
        except:
            return 0.0

    def _start_watchdog(self):
        """Start watchdog observer"""
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class Handler(FileSystemEventHandler):
            def __init__(self, callback):
                self.callback = callback
                self.last_trigger = 0
                
            def on_any_event(self, event):
                if event.is_directory: return
                
                # Debounce (max 1 update per 5 seconds)
                now = time.time()
                if now - self.last_trigger > 5:
                    self.last_trigger = now
                    logger.info(f"Watchdog event: {event.src_path}")
                    self.callback()
                    
        self.observer = Observer()
        handler = Handler(self.callback)
        
        for folder in self.folders:
            if folder.exists():
                self.observer.schedule(handler, str(folder), recursive=False)
                
        self.observer.start()
