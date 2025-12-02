import sys
import os
import subprocess
import time
import signal
from pathlib import Path

def main():
    project_root = Path(__file__).parent
    processes = []
    
    def cleanup(signum=None, frame=None):
        print("\n🛑 Shutting down HVA...")
        for p in processes:
            if p.poll() is None:
                p.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # 1. Start API Server
    print("🚀 Starting HVA API Server...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "api.main"],
        cwd=project_root,
        env={**os.environ, "PYTHONPATH": str(project_root)}
    )
    processes.append(api_process)
    
    # Wait for API to be ready
    print("⏳ Waiting for API...")
    time.sleep(3)
    
    # 2. Start Electron App
    print("🖥️ Starting HVA Desktop...")
    desktop_dir = project_root / "desktop"
    
    # Check if we are in dev mode or prod
    # For now, we assume dev mode or manual build
    # In a real scenario, we might check for the built .app or use 'npm run electron'
    
    if (desktop_dir / "node_modules").exists():
        # Use npm run electron:dev for development if arguments say so, else just electron
        # For simplicity in this phase, let's use the electron script which waits for vite
        # But wait, 'electron' script in package.json waits for port 5173.
        # If we want to run the FULL app, we need to start vite server too if it's not running.
        # The 'electron:dev' script does both.
        
        cmd = ["npm", "run", "electron:dev"]
        
        electron_process = subprocess.Popen(
            cmd,
            cwd=desktop_dir,
            shell=True
        )
        processes.append(electron_process)
    else:
        print("⚠️ Desktop dependencies not found. Run: cd desktop && npm install")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            for p in processes:
                if p.poll() is not None:
                    # If API dies, we should probably exit
                    if p == api_process:
                        print("⚠️ API Server stopped unexpectedly")
                        cleanup()
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
