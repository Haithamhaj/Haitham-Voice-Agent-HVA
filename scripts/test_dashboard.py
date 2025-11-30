import multiprocessing
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from haitham_voice_agent.gui_process import run_gui_process

def test_dashboard():
    print("🚀 Launching Dashboard GUI Test...")
    
    gui_queue = multiprocessing.Queue()
    cmd_queue = multiprocessing.Queue()
    
    # Start GUI process
    p = multiprocessing.Process(target=run_gui_process, args=(gui_queue, cmd_queue))
    p.start()
    
    try:
        # Simulate some interactions
        time.sleep(2)
        print("Sending 'show' command...")
        gui_queue.put(('show',))
        
        time.sleep(1)
        print("Sending user message...")
        gui_queue.put(('add_message', 'user', 'Hello Haitham!', False))
        
        time.sleep(1)
        print("Sending assistant response...")
        gui_queue.put(('add_message', 'assistant', 'Hello! How can I help you today?', False))
        
        time.sleep(1)
        print("Simulating listening...")
        gui_queue.put(('show_listening',))
        
        time.sleep(2)
        print("Simulating processing...")
        gui_queue.put(('show_processing',))
        
        print("\n✅ Test running. Close the window to exit.")
        p.join()
        
    except KeyboardInterrupt:
        print("\nStopping...")
        p.terminate()

if __name__ == "__main__":
    test_dashboard()
