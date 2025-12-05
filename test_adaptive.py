import asyncio
import logging
from pathlib import Path
from haitham_voice_agent.intelligence.adaptive_sync import AdaptiveSync

logging.basicConfig(level=logging.INFO)

async def test_sync():
    print("🚀 Testing Adaptive Sync...")
    sync = AdaptiveSync()
    
    # Test with a specific folder (e.g., Documents)
    docs_path = str(Path.home() / "Documents")
    
    # Enable indexing of new files to populate DB
    stats = await sync.sync_knowledge_base(scan_roots=[docs_path], index_new=True)
    print(f"✅ Sync Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_sync())
