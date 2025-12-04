import asyncio
import os
import shutil
from pathlib import Path
from haitham_voice_agent.tools.deep_organizer import get_deep_organizer
from haitham_voice_agent.tools.checkpoint_manager import get_checkpoint_manager

async def test_rollback():
    # Setup dummy dir
    base_dir = Path("test_rollback_data")
    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir()
    
    # Create test files
    (base_dir / "invoice.txt").write_text("Invoice for Google Cloud Services. Amount: $50. Date: Oct 2025.")
    
    print(f"Created test file in {base_dir}")
    
    # Initialize DB (ensure table exists)
    from haitham_voice_agent.tools.memory.memory_system import memory_system
    await memory_system.initialize()
    
    # 1. Run Scan & Plan
    organizer = get_deep_organizer()
    print("Scanning...")
    plan = await organizer.scan_and_plan(str(base_dir))
    
    if not plan['changes']:
        print("No changes proposed. Test failed.")
        return

    # 2. Execute Plan (Creates Checkpoint)
    print("Executing Plan...")
    report = await organizer.execute_plan(plan)
    
    checkpoint_id = report.get("checkpoint_id")
    if not checkpoint_id:
        print("No checkpoint created. Test failed.")
        return
        
    print(f"Checkpoint created: {checkpoint_id}")
    
    # Verify file moved
    new_path = Path(plan['changes'][0]['proposed_path'])
    if new_path.exists():
        print(f"File moved to: {new_path}")
    else:
        print("File move failed.")
        return
        
    # 3. Rollback
    print("Rolling back...")
    cm = get_checkpoint_manager()
    rollback_report = await cm.rollback_checkpoint(checkpoint_id)
    
    print(f"Rollback Report: {rollback_report}")
    
    # Verify file returned
    original_path = Path(plan['changes'][0]['original_path'])
    if original_path.exists():
        print(f"SUCCESS: File returned to {original_path}")
    else:
        print(f"FAILURE: File not found at {original_path}")
        
    # Cleanup
    shutil.rmtree(base_dir)

if __name__ == "__main__":
    asyncio.run(test_rollback())
