import os
import shutil
import stat
from pathlib import Path

def create_app_bundle():
    desktop = Path(os.path.expanduser("~/Desktop"))
    old_app = desktop / "HVA.app"
    new_app = desktop / "HVA Premium.app"
    project_dir = Path("/Users/haitham/development/Haitham Voice Agent (HVA)")
    
    # Check if old app exists to steal icon
    icon_source = old_app / "Contents/Resources/applet.icns"
    if not icon_source.exists():
        print(f"⚠️  Could not find icon at {icon_source}")
        print("   Using generic icon.")
        icon_source = None
    
    # Create Directories
    contents = new_app / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources"
    
    if new_app.exists():
        shutil.rmtree(new_app)
        
    os.makedirs(macos, exist_ok=True)
    os.makedirs(resources, exist_ok=True)
    
    # Copy Icon
    if icon_source:
        shutil.copy(icon_source, resources / "applet.icns")
        icon_name = "applet.icns"
    else:
        icon_name = None
        
    # Create Info.plist
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>HVA</string>
    <key>CFBundleIconFile</key>
    <string>{icon_name if icon_name else ''}</string>
    <key>CFBundleIdentifier</key>
    <string>com.haitham.hva</string>
    <key>CFBundleName</key>
    <string>HVA Premium</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.7</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>"""
    
    with open(contents / "Info.plist", "w") as f:
        f.write(plist_content)
        
    # Create Launcher Script
    script_content = f"""#!/bin/bash
# HVA Launcher
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
cd "{project_dir}"

# Logging
LOG_FILE="/tmp/hva_launch.log"
echo "🚀 Launching HVA at $(date)" > "$LOG_FILE"

if [ -d ".venv" ]; then
    echo "Activating venv..." >> "$LOG_FILE"
    source .venv/bin/activate
else
    echo "⚠️ venv not found" >> "$LOG_FILE"
fi

echo "Running python..." >> "$LOG_FILE"
# Force arm64 execution to match installed libraries
arch -arm64 python3 -m haitham_voice_agent.hva_menubar >> "$LOG_FILE" 2>&1
"""

    launcher_path = macos / "HVA"
    with open(launcher_path, "w") as f:
        f.write(script_content)
        
    # Make executable
    st = os.stat(launcher_path)
    os.chmod(launcher_path, st.st_mode | stat.S_IEXEC)
    
    print(f"✅ Created '{new_app}' successfully!")
    if icon_source:
        print("   Icon copied from old app.")

if __name__ == "__main__":
    create_app_bundle()
