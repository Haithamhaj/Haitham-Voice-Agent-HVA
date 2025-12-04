import asyncio
import os
import shutil
from pathlib import Path
from haitham_voice_agent.tools.deep_organizer import get_deep_organizer

async def test_organizer():
    print("--- Starting DeepOrganizer Verification ---")
    
    # 1. Setup Test Environment
    test_dir = Path("test_organizer_data")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # Create dummy files
    (test_dir / "invoice_2024.txt").write_text("Invoice for Web Design Service. Amount: $500.")
    (test_dir / "meeting_notes.txt").write_text("Notes from the team meeting. Discussed project timeline.")
    (test_dir / "random_script.py").write_text("print('hello world')")
    
    print(f"Created test directory at {test_dir.absolute()}")
    
    # 2. Initialize Organizer
    organizer = get_deep_organizer()
    print("DeepOrganizer initialized.")
    
    # 3. Run Scan and Plan
    print(f"Scanning {test_dir}...")
    try:
        plan = await organizer.scan_and_plan(str(test_dir))
        
        print("\n--- Plan Generated ---")
        print(f"Scanned files: {plan.get('scanned')}")
        print(f"Proposed moves: {len(plan.get('changes', []))}")
        
        for change in plan.get('changes', []):
            print(f"  - {change['original_path']} -> {change['category']}/{change['new_filename']}")
            
        if "error" in plan:
            print(f"ERROR in plan: {plan['error']}")
        else:
            print("SUCCESS: Plan generated without errors.")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    # shutil.rmtree(test_dir)

if __name__ == "__main__":
    asyncio.run(test_organizer())
