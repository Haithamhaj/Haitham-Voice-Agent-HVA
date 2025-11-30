import subprocess
import json
import os
import platform
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class SystemProfiler:
    """
    Layer 1: System Profile
    Gather static system information (Hardware, Storage, Apps)
    """
    
    def __init__(self, storage_path: str = "~/HVA_Memory/system/system_profile.json"):
        self.storage_path = Path(storage_path).expanduser()
        self.profile = {}
        self.load_profile() # Load immediately on init
        
    def load_profile(self):
        """Load existing profile from disk"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.profile = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load system profile: {e}")
                self.profile = {}

    def run_profile(self) -> Dict[str, Any]:
        """Run smart system profile update"""
        logger.info("Running System Profile Update (Layer 1)...")
        
        # 1. Hardware: Keep existing if available (Static)
        if not self.profile.get("device"):
            self.profile["device"] = self._get_device_info()
            
        # 2. Apps: Check if re-scan is needed (Smart Update)
        if self._should_rescan_apps():
            logger.info("Changes detected in Applications. Re-scanning...")
            self.profile["apps"] = self._scan_applications()
            self.profile["apps_last_scan"] = self._get_timestamp()
        else:
            logger.info("No changes in Applications. Using cached list.")
             
        # 3. Storage: Always update (Volatile)
        self.profile["storage"] = self._get_storage_info()
        
        # 4. Key Folders: Update if missing
        if not self.profile.get("key_folders"):
            self.profile["key_folders"] = self._get_key_folders()
            
        self.profile["last_updated"] = self._get_timestamp()
        
        self._save_profile()
        return self.profile

    def _should_rescan_apps(self) -> bool:
        """Check if application folders have been modified since last scan"""
        last_scan = self.profile.get("apps_last_scan")
        if not last_scan:
            return True
            
        search_paths = ["/Applications", "/System/Applications", str(Path.home() / "Applications")]
        
        try:
            from datetime import datetime
            last_scan_dt = datetime.fromisoformat(last_scan)
            
            for path in search_paths:
                p = Path(path)
                if p.exists():
                    # Check folder modification time
                    mtime = datetime.fromtimestamp(p.stat().st_mtime)
                    if mtime > last_scan_dt:
                        return True
        except Exception as e:
            logger.warning(f"Error checking app timestamps: {e}")
            return True # Fallback to rescan
            
        return False
        
    def _get_device_info(self) -> Dict[str, str]:
        """Get hardware info using system_profiler"""
        info = {
            "name": platform.node(),
            "os": f"{platform.system()} {platform.release()}",
            "arch": platform.machine()
        }
        
        try:
            # Get Chip/RAM info on macOS
            cmd = ["system_profiler", "SPHardwareDataType", "-json"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            hw = data['SPHardwareDataType'][0]
            
            info["chip"] = hw.get('chip_type', 'Unknown')
            info["ram"] = hw.get('physical_memory', 'Unknown')
            info["model"] = hw.get('machine_model', 'Unknown')
            
        except Exception as e:
            logger.warning(f"Failed to get detailed hardware info: {e}")
            
        return info
        
    def _get_storage_info(self) -> Dict[str, str]:
        """Get storage info using df"""
        try:
            cmd = ["df", "-h", "/"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                # Filesystem Size Used Avail Capacity iused ifree %iused Mounted on
                return {
                    "total": parts[1],
                    "used": parts[2],
                    "free": parts[3],
                    "capacity": parts[4]
                }
        except Exception as e:
            logger.warning(f"Failed to get storage info: {e}")
            
        return {}
        
    def _scan_applications(self) -> List[Dict[str, str]]:
        """Scan installed applications"""
        apps = []
        # Added user applications path
        search_paths = ["/Applications", "/System/Applications", str(Path.home() / "Applications")]
        
        seen_names = set()
        
        for path in search_paths:
            p = Path(path)
            if not p.exists():
                continue
                
            try:
                for item in p.iterdir():
                    if item.suffix == ".app":
                        name = item.stem
                        if name not in seen_names:
                            apps.append({
                                "name": name,
                                "path": str(item)
                            })
                            seen_names.add(name)
            except Exception as e:
                logger.warning(f"Error scanning {path}: {e}")
                
        return sorted(apps, key=lambda x: x['name'])
        
    def _get_key_folders(self) -> Dict[str, str]:
        """Get paths to key folders"""
        home = Path.home()
        return {
            "home": str(home),
            "desktop": str(home / "Desktop"),
            "downloads": str(home / "Downloads"),
            "documents": str(home / "Documents"),
            "pictures": str(home / "Pictures"),
            "music": str(home / "Music"),
            "movies": str(home / "Movies")
        }
        
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
        
    def _save_profile(self):
        """Save profile to disk"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.profile, f, indent=2, ensure_ascii=False)
            logger.info(f"System profile saved to {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save system profile: {e}")

    def get_app_path(self, app_name: str) -> str:
        """Get path for an app by name (fuzzy match)"""
        if not self.profile:
            self.run_profile() # Ensure loaded
            
        app_name_lower = app_name.lower()
        
        # 1. Exact match
        for app in self.profile.get("apps", []):
            if app["name"].lower() == app_name_lower:
                return app["path"]
                
        # 2. Contains match
        for app in self.profile.get("apps", []):
            if app_name_lower in app["name"].lower():
                return app["path"]
                
        return None
