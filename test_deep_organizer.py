import asyncio
import os
import shutil
from pathlib import Path
from haitham_voice_agent.tools.deep_organizer import get_deep_organizer

async def test_organizer():
    # Setup dummy dir
    base_dir = Path("test_organizer_data")
    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir()
    
    # Create test files
    (base_dir / "invoice.txt").write_text("Invoice for Google Cloud Services. Amount: $50. Date: Oct 2025.")
    (base_dir / "notes.txt").write_text("Meeting notes for Project Alpha. Discussed API design.")
    (base_dir / "random.txt").write_text("Just some random text that is too short.")
    
    print(f"Created test files in {base_dir}")
    
    # Run Scan
    organizer = get_deep_organizer()
    print("Scanning...")
    plan = await organizer.scan_and_plan(str(base_dir))
    
    print("\n--- Plan ---")
    print(f"Scanned: {plan['scanned']}")
    print(f"Changes Proposed: {len(plan['changes'])}")
    
    for change in plan['changes']:
        print(f"\nOriginal: {change['original_path']}")
        print(f"Proposed: {change['proposed_path']}")
        print(f"Reason: {change['reason']}")
        
    # Cleanup
    shutil.rmtree(base_dir)

if __name__ == "__main__":
    asyncio.run(test_organizer())
