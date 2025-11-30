import asyncio
import sys
import shutil
from pathlib import Path
from unittest.mock import AsyncMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from haitham_voice_agent.memory.manager import get_memory_manager

async def test_memory_layer3():
    print("🧪 Testing Memory Layer 3 (Knowledge Graph)...")
    
    manager = get_memory_manager()
    
    # Use a test directory
    test_memory_root = Path("test_hva_memory_layer3")
    if test_memory_root.exists():
        shutil.rmtree(test_memory_root)
    
    # Override paths
    manager.memory_root = test_memory_root
    manager.projects_dir = test_memory_root / "Projects"
    manager.inbox_dir = test_memory_root / "Inbox"
    manager.initialize_memory()
    
    # Override Graph Store path
    manager.graph_store.memory_root = test_memory_root
    manager.graph_store.graph_path = test_memory_root / "knowledge_graph.json"
    manager.graph_store.load_graph() # Reset graph
    
    # Mock LLM Router
    manager.llm_router.generate_with_gemini = AsyncMock(return_value='{"summary": "Graph Theory", "key_points": "- Nodes\n- Edges", "tags": ["Math", "Network"]}')
    
    # 1. Create Project
    print("\n📂 Creating Project 'GraphProject'...")
    manager.create_project("GraphProject", "Testing graph connections")
    
    # 2. Save Thought Linked to Project
    print("\n📝 Saving thought linked to 'GraphProject'...")
    await manager.save_thought("Nodes and edges connect entities.", project_name="GraphProject")
    
    # 3. Verify Graph
    print("\n🕸️ Verifying Graph Connections...")
    graph = manager.graph_store
    
    # Check Project Node
    related_to_project = graph.get_related("GraphProject")
    print(f"Related to GraphProject: {len(related_to_project)}")
    
    has_note = False
    has_tag = False
    
    for r in related_to_project:
        print(f"- {r['direction']} {r['relation']} -> {r['type']} ({r['id']})")
        if r['type'] == "Note" and r['relation'] == "PART_OF":
            has_note = True
        if r['type'] == "Concept" and r['relation'] == "RELATED_TO":
            has_tag = True
            
    if has_note:
        print("✅ Project -> Note connection verified")
    else:
        print("❌ Project -> Note connection missing")
        
    if has_tag:
        print("✅ Project -> Concept connection verified")
    else:
        print("❌ Project -> Concept connection missing")

    # Cleanup
    try:
        shutil.rmtree(test_memory_root)
        print("\n🧹 Cleanup done")
    except Exception as e:
        print(f"\n⚠️ Cleanup warning: {e}")

if __name__ == "__main__":
    asyncio.run(test_memory_layer3())
