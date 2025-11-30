import asyncio
import sys
import shutil
from pathlib import Path
from unittest.mock import AsyncMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from haitham_voice_agent.memory.manager import get_memory_manager

async def test_memory_layer2():
    print("🧪 Testing Memory Layer 2 (Vector Store)...")
    
    manager = get_memory_manager()
    
    # Use a test directory
    test_memory_root = Path("test_hva_memory_layer2")
    if test_memory_root.exists():
        shutil.rmtree(test_memory_root)
    
    # Override paths
    manager.memory_root = test_memory_root
    manager.projects_dir = test_memory_root / "Projects"
    manager.inbox_dir = test_memory_root / "Inbox"
    manager.initialize_memory()
    
    # Override Vector Store path
    # We need to re-init vector store with test path
    import chromadb
    from haitham_voice_agent.memory.vector_store import VectorStore
    
    test_vector_path = test_memory_root / "VectorDB"
    test_vector_path.mkdir(parents=True, exist_ok=True)
    
    # Mock the singleton's internal vector store
    manager.vector_store.client = chromadb.PersistentClient(path=str(test_vector_path))
    manager.vector_store.collection = manager.vector_store.client.get_or_create_collection(name="hva_memory_test")
    
    # Mock LLM Router
    manager.llm_router.generate_with_gemini = AsyncMock(return_value='{"summary": "AI Memory", "key_points": "- RAG", "tags": ["AI"]}')
    
    # 1. Add Document (Save Thought)
    print("\n📝 Saving thought about 'Artificial Intelligence'...")
    await manager.save_thought("Artificial Intelligence is transforming how we organize information using vector databases.")
    
    # 2. Search (Semantic)
    print("\n🔍 Searching for 'AI database'...")
    results = await manager.search_memory("AI database")
    
    print("--- Search Results ---")
    found = False
    for r in results:
        print(f"- {r['content']} (Dist: {r['distance']:.4f})")
        if "Artificial Intelligence" in r['content']:
            found = True
            
    if found:
        print("✅ Semantic search successful")
    else:
        print("❌ Semantic search failed")

    # Cleanup
    # Note: ChromaDB holds file locks, so cleanup might fail on Windows, but usually OK on Mac/Linux if client is closed.
    # We won't force cleanup of vector db files to avoid errors, just the main dir if possible.
    try:
        shutil.rmtree(test_memory_root)
        print("\n🧹 Cleanup done")
    except Exception as e:
        print(f"\n⚠️ Cleanup warning: {e}")

if __name__ == "__main__":
    asyncio.run(test_memory_layer2())
