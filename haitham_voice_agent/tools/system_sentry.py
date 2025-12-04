"""
System Sentry Tool
Monitors system health, identifies resource hogs, and performs safe cleanup.
"""

import os
import shutil
import logging
import psutil
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SystemSentry:
    """
    Guardian of System Health.
    Monitors CPU, RAM, Disk, and cleans up junk.
    """
    
    def __init__(self):
        logger.info("SystemSentry initialized")
        
    async def check_health(self) -> Dict[str, Any]:
        """
        Get comprehensive system health status.
        """
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory
            mem = psutil.virtual_memory()
            ram_percent = mem.percent
            ram_used_gb = round(mem.used / (1024**3), 2)
            ram_total_gb = round(mem.total / (1024**3), 2)
            
            # Disk
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free_gb = round(disk.free / (1024**3), 2)
            
            # Battery (if laptop)
            battery_info = "N/A"
            if hasattr(psutil, "sensors_battery"):
                battery = psutil.sensors_battery()
                if battery:
                    battery_info = f"{round(battery.percent)}% ({'Charging' if battery.power_plugged else 'On Battery'})"
            
            status = "Healthy"
            if cpu_percent > 80 or ram_percent > 85:
                status = "Strained"
            if disk_percent > 90:
                status = "Low Disk Space"
                
            return {
                "status": status,
                "cpu": {
                    "usage": f"{cpu_percent}%",
                    "cores": cpu_count
                },
                "memory": {
                    "usage": f"{ram_percent}%",
                    "details": f"{ram_used_gb}GB / {ram_total_gb}GB"
                },
                "disk": {
                    "usage": f"{disk_percent}%",
                    "free": f"{disk_free_gb}GB"
                },
                "battery": battery_info
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"error": True, "message": str(e)}

    async def find_hogs(self, limit: int = 5) -> Dict[str, Any]:
        """
        Find processes consuming the most resources.
        """
        try:
            # Get all processes
            procs = []
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    # Calculate CPU percent (can be > 100% on multi-core)
                    p.info['cpu_percent'] = p.cpu_percent() / psutil.cpu_count()
                    procs.append(p.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort by Memory (usually more relevant for "slowness" on Mac)
            # Or we could return two lists. Let's sort by a mix or just Memory for now.
            sorted_by_mem = sorted(procs, key=lambda p: p['memory_percent'] or 0, reverse=True)[:limit]
            sorted_by_cpu = sorted(procs, key=lambda p: p['cpu_percent'] or 0, reverse=True)[:limit]
            
            return {
                "memory_hogs": [
                    {"name": p['name'], "memory": f"{round(p['memory_percent'], 1)}%"} 
                    for p in sorted_by_mem
                ],
                "cpu_hogs": [
                    {"name": p['name'], "cpu": f"{round(p['cpu_percent'] * 100, 1)}%"} 
                    for p in sorted_by_cpu
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to find hogs: {e}")
            return {"error": True, "message": str(e)}

    async def clean_cache(self, confirmed: bool = False) -> Dict[str, Any]:
        """
        Clean user cache files (~/Library/Caches).
        REQUIRES CONFIRMATION.
        """
        if not confirmed:
            return {
                "status": "confirmation_required",
                "message": "Are you sure you want to clean the System Cache? This may log you out of some apps or reset preferences.",
                "command": "system_sentry.clean_cache",
                "risk_level": "medium"
            }
            
        try:
            cache_dir = Path.home() / "Library/Caches"
            if not cache_dir.exists():
                return {"error": True, "message": "Cache directory not found"}
            
            # Calculate size before
            total_size = sum(f.stat().st_size for f in cache_dir.glob('**/*') if f.is_file())
            size_mb = round(total_size / (1024*1024), 2)
            
            # Delete contents (not the dir itself)
            deleted_count = 0
            errors = 0
            
            for item in cache_dir.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                    deleted_count += 1
                except Exception:
                    errors += 1
            
            return {
                "status": "cleaned",
                "freed_space": f"{size_mb} MB",
                "items_removed": deleted_count,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
            return {"error": True, "message": str(e)}
