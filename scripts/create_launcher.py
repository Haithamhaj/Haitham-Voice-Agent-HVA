import os
import stat
from pathlib import Path

def create_launcher():
    # Define paths
    project_dir = Path("/Users/haitham/development/Haitham Voice Agent (HVA)")
    desktop_dir = Path(os.path.expanduser("~/Desktop"))
    launcher_path = desktop_dir / "Start HVA.command"
    
    # Define script content
    script_content = f"""#!/bin/bash
# HVA Launcher
echo "🚀 Starting Haitham Voice Agent..."
cd "{project_dir}"

# Check if venv exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "⚠️  Virtual environment not found! Trying global python..."
fi

# Run the Menu Bar App
arch -arm64 python3 -m haitham_voice_agent.hva_menubar

# Keep terminal open if it crashes immediately
read -p "Press enter to close..."
"""

    # Write file
    try:
        with open(launcher_path, "w") as f:
            f.write(script_content)
        
        # Make executable (chmod +x)
        st = os.stat(launcher_path)
        os.chmod(launcher_path, st.st_mode | stat.S_IEXEC)
        
        print(f"✅ Launcher created successfully at: {launcher_path}")
        print("👉 You can now double-click 'Start HVA.command' on your Desktop.")
        
    except Exception as e:
        print(f"❌ Failed to create launcher: {e}")

if __name__ == "__main__":
    create_launcher()
