import asyncio
import logging
import sys
import aiosqlite
from datetime import datetime, timedelta
import uuid

# Add project root to path
sys.path.append("/Users/haitham/development/Haitham Voice Agent (HVA)")

from haitham_voice_agent.tools.memory.storage.sqlite_store import SQLiteStore
from haitham_voice_agent.tools.memory.models.memory import Memory, MemoryType, MemorySource, SensitivityLevel
from haitham_voice_agent.tools.secretary import Secretary

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_feedback_agent():
    store = SQLiteStore()
    
    # 0. Cleanup previous test runs
    # Delete any memories with project "Stale Project X"
    async with aiosqlite.connect(store.db_path) as db:
        await db.execute("DELETE FROM memories WHERE project = 'Stale Project X'")
        await db.commit()

    # 1. Create a "stale" project memory
    memory_id = str(uuid.uuid4())
    # Set updated_at to 5 days ago
    stale_date = datetime.now() - timedelta(days=5)
    
    memory = Memory(
        id=memory_id,
        timestamp=stale_date,
        source=MemorySource.MANUAL,
        project="Stale Project X",
        topic="Project Definition",
        type=MemoryType.PROJECT,
        tags=["test"],
        ultra_brief="Test stale project",
        executive_summary=[],
        detailed_summary="This is a stale project for testing feedback agent",
        raw_content="Test content",
        status="active",
        updated_at=stale_date,
        nag_count=0,
        importance=10 # Ensure it's picked first
    )
    
    logger.info(f"Creating stale project '{memory.project}' with nag_count=0...")
    await store.save_memory(memory)
    
    # 2. Initialize Secretary and get briefing
    secretary = Secretary()
    
    logger.info("Generating morning briefing (simulating normal day)...")
    # Note: Secretary uses the singleton memory manager which uses the singleton store.
    # We need to ensure they point to the same DB. They should as they use Config.
    
    briefing = await secretary.get_morning_briefing()
    
    # 3. Verify Feedback Question
    feedback = briefing.get("data", {}).get("feedback_question", "")
    logger.info(f"Feedback Question: {feedback}")
    
    if "Stale Project X" in feedback and "no updates" in feedback:
        logger.info("✅ Verification 1 SUCCESS: Feedback question generated correctly for nag_count=0.")
    else:
        logger.error(f"❌ Verification 1 FAILED: Feedback question missing or incorrect. Got: {feedback}")
        
    # 4. Verify nag_count incremented
    updated_memory = await store.get_memory(memory_id)
    if updated_memory.nag_count == 1:
        logger.info("✅ Verification 2 SUCCESS: nag_count incremented to 1.")
    else:
        logger.error(f"❌ Verification 2 FAILED: nag_count is {updated_memory.nag_count}, expected 1.")
        
    # Cleanup
    await store.delete_memory(memory_id)

if __name__ == "__main__":
    asyncio.run(test_feedback_agent())
