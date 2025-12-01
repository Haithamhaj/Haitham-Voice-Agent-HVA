import asyncio
import logging
import sys
from datetime import datetime
import uuid

# Add project root to path
sys.path.append("/Users/haitham/development/Haitham Voice Agent (HVA)")

from haitham_voice_agent.tools.memory.storage.sqlite_store import SQLiteStore
from haitham_voice_agent.tools.memory.models.memory import Memory, MemoryType, MemorySource, SensitivityLevel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_memory_v1_1():
    store = SQLiteStore()
    
    # Create a test memory with new fields
    memory_id = str(uuid.uuid4())
    memory = Memory(
        id=memory_id,
        timestamp=datetime.now(),
        source=MemorySource.MANUAL,
        project="Test Project",
        topic="Test Topic",
        type=MemoryType.NOTE,
        tags=["test"],
        ultra_brief="Test memory",
        executive_summary=[],
        detailed_summary="This is a test memory for v1.1",
        raw_content="Test content",
        status="on_hold",  # New field
        structured_data={"key": "value", "number": 123}  # New field
    )
    
    logger.info(f"Saving memory {memory_id} with status='on_hold' and structured_data...")
    success = await store.save_memory(memory)
    
    if not success:
        logger.error("Failed to save memory")
        return
        
    logger.info("Memory saved. Retrieving...")
    retrieved_memory = await store.get_memory(memory_id)
    
    if not retrieved_memory:
        logger.error("Failed to retrieve memory")
        return
        
    logger.info(f"Retrieved memory status: {retrieved_memory.status}")
    logger.info(f"Retrieved memory structured_data: {retrieved_memory.structured_data}")
    
    if retrieved_memory.status == "on_hold" and retrieved_memory.structured_data == {"key": "value", "number": 123}:
        logger.info("✅ Verification SUCCESS: New fields saved and retrieved correctly.")
    else:
        logger.error("❌ Verification FAILED: Fields do not match.")

if __name__ == "__main__":
    asyncio.run(test_memory_v1_1())
