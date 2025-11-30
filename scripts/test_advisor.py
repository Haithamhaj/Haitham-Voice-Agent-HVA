import asyncio
import sys
import time
import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from haitham_voice_agent.tools.advisor import get_advisor

def test_advisor():
    print("🧪 Testing Advisor Module...")
    
    advisor = get_advisor()
    
    # 1. Test Safety Validation
    print("\n🛡️ Testing Safety Validation...")
    
    # Case A: Safe deletion
    dummy_path = Path.home() / "Downloads" / "junk_test_folder"
    dummy_path.mkdir(exist_ok=True)
    
    res = advisor.validate_action("files", "delete_folder", {"path": str(dummy_path)})
    if res["safe"]:
        print("✅ Safe deletion allowed")
    else:
        print(f"❌ Safe deletion blocked: {res}")
    
    # Cleanup
    if dummy_path.exists():
        dummy_path.rmdir()
        
    # Case B: Unsafe deletion (Documents)
    res = advisor.validate_action("files", "delete_folder", {"path": "~/Documents"})
    if not res["safe"]:
        print(f"✅ Unsafe deletion blocked: {res['warning']}")
    else:
        print("❌ Unsafe deletion allowed!")

    # 2. Test Wellbeing
    print("\n🧘 Testing Wellbeing Check...")
    # Mock start time to be 2.05 hours ago (within 2.0-2.1 window)
    advisor.start_time = datetime.datetime.now() - datetime.timedelta(hours=2.05)
    alert = advisor.check_wellbeing()
    if alert and "Health Tip" in alert:
        print(f"✅ Wellbeing alert triggered: {alert}")
    else:
        print("❌ Wellbeing alert failed")
        
    # 3. Test Resource Check (Mock)
    print("\n🚀 Testing Resource Check...")
    # We can't easily mock psutil here without mocking the library, 
    # but we can check if it runs without error.
    # To force alert, we'd need to mock psutil.virtual_memory
    
    try:
        alert = advisor.check_resources()
        print(f"Resource check ran. Alert: {alert}")
        print("✅ Resource check executed")
    except Exception as e:
        print(f"❌ Resource check failed: {e}")

if __name__ == "__main__":
    test_advisor()
