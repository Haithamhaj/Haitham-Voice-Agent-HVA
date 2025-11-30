import asyncio
import sys
import shutil
from pathlib import Path
from unittest.mock import AsyncMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from haitham_voice_agent.memory.manager import get_memory_manager

async def test_memory_layer1():
    print("🧪 Testing Memory Layer 1 (Structured)...")
    
    manager = get_memory_manager()
    
    # Use a test directory to avoid messing up real memory
    test_memory_root = Path("test_hva_memory")
    if test_memory_root.exists():
        shutil.rmtree(test_memory_root)
    
    # Override paths
    manager.memory_root = test_memory_root
    manager.projects_dir = test_memory_root / "Projects"
    manager.concepts_dir = test_memory_root / "Concepts"
    manager.archives_dir = test_memory_root / "Archives"
    manager.inbox_dir = test_memory_root / "Inbox"
    manager.initialize_memory()
    
    # Mock LLM Router
    manager.llm_router.generate_with_gemini = AsyncMock(return_value='{"summary": "Test Summary", "key_points": "- Point 1", "tags": ["test"]}')
    
    # 1. Test Create Project
    print("\n📂 Testing Create Project...")
    res = manager.create_project("Test Project", "A dummy project for testing.")
    print(f"Result: {res}")
    
    if res["success"] and (manager.projects_dir / "Test_Project" / "overview.md").exists():
        print("✅ Project created successfully")
    else:
        print("❌ Project creation failed")
        
    # 2. Test Save Thought (Inbox)
    print("\n📝 Testing Save Thought (Inbox)...")
    res = await manager.save_thought("This is a random thought.")
    print(f"Result: {res}")
    
    if res["success"] and list(manager.inbox_dir.glob("thought_*.md")):
        print("✅ Thought saved to Inbox")
        print(f"Summary: {res.get('summary')}")
    else:
        print("❌ Inbox save failed")

    # 3. Test Save Thought (Project)
    print("\n📝 Testing Save Thought (Project)...")
    res = await manager.save_thought("This is a project thought.", project_name="Test Project")
    print(f"Result: {res}")
    
    project_context = manager.projects_dir / "Test_Project" / "context"
    if res["success"] and list(project_context.glob("note_*.md")):
        print("✅ Thought saved to Project Context")
    else:
        print("❌ Project save failed")
        
    # Cleanup
    shutil.rmtree(test_memory_root)
    print("\n🧹 Cleanup done")

if __name__ == "__main__":
    asyncio.run(test_memory_layer1())
