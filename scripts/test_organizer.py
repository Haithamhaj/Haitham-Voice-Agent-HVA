import os
import shutil
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from haitham_voice_agent.tools.smart_organizer import SmartOrganizer

def test_organizer():
    print("🧪 Testing Smart Organizer...")
    
    # Setup dummy downloads
    dummy_downloads = Path("dummy_downloads")
    if dummy_downloads.exists():
        shutil.rmtree(dummy_downloads)
    dummy_downloads.mkdir()
    
    # Create dummy files
    files = [
        "image1.jpg", "doc1.pdf", "script.py", "archive.zip", "installer.dmg", "random.xyz"
    ]
    
    for f in files:
        (dummy_downloads / f).touch()
        
    print(f"📂 Created dummy files in {dummy_downloads}")
    
    # Initialize Organizer with dummy path
    organizer = SmartOrganizer()
    organizer.downloads = dummy_downloads # Override for test
    
    # Run Organization
    print("🔄 Running organize_downloads()...")
    report = organizer.organize_downloads()
    
    print("\n📊 Report:")
    print(report)
    
    # Verify
    print("\n🧐 Verification:")
    expected_structure = {
        "Images": ["image1.jpg"],
        "Documents": ["doc1.pdf"],
        "Code": ["script.py"],
        "Archives": ["archive.zip"],
        "Installers": ["installer.dmg"]
    }
    
    success = True
    for cat, items in expected_structure.items():
        cat_dir = dummy_downloads / cat
        if not cat_dir.exists():
            print(f"❌ Missing category folder: {cat}")
            success = False
            continue
            
        for item in items:
            if not (cat_dir / item).exists():
                print(f"❌ Missing file {item} in {cat}")
                success = False
            else:
                print(f"✅ Found {item} in {cat}")
                
    # Check random file remains
    if (dummy_downloads / "random.xyz").exists():
        print("✅ Uncategorized file remained in root")
    else:
        print("❌ Uncategorized file moved unexpectedly")
        success = False
        
    # Cleanup
    shutil.rmtree(dummy_downloads)
    print("\n🧹 Cleanup done")
    
    if success:
        print("\n✅ TEST PASSED")
    else:
        print("\n❌ TEST FAILED")

if __name__ == "__main__":
    test_organizer()
