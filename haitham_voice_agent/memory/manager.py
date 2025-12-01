import logging
import datetime
import uuid
from typing import Dict, Any, Optional, List

from haitham_voice_agent.llm_router import LLMRouter
from haitham_voice_agent.config import Config
from haitham_voice_agent.memory.vector_store import get_vector_store
from haitham_voice_agent.memory.graph_store import get_graph_store
from haitham_voice_agent.tools.memory.storage.sqlite_store import SQLiteStore
from haitham_voice_agent.tools.memory.models.memory import Memory, MemoryType, MemorySource, SensitivityLevel

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Unified Memory Manager (Wrapper around SQLite + Vector Store).
    Replaces file-based storage with SQLite.
    """
    
    def __init__(self):
        self.sqlite_store = SQLiteStore()
        self.vector_store = get_vector_store()
        self.graph_store = get_graph_store()
        self.llm_router = LLMRouter()
        
    async def initialize(self):
        """Explicit initialization if needed"""
        await self.sqlite_store.initialize()

    async def create_project(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new project definition in Memory.
        """
        try:
            # Create Memory Object for Project
            memory = Memory(
                id=str(uuid.uuid4()),
                timestamp=datetime.datetime.now(),
                source=MemorySource.MANUAL,
                project=name, # Self-referential
                topic="Project Definition",
                type=MemoryType.PROJECT,
                tags=["project", "definition"],
                ultra_brief=f"Project: {name}",
                executive_summary=[description],
                detailed_summary=description,
                raw_content=f"Project: {name}\nDescription: {description}",
                # Defaults
                decisions=[],
                action_items=[],
                open_questions=[],
                key_insights=[],
                people_mentioned=[],
                projects_mentioned=[],
                conversation_id=None,
                parent_memory_id=None,
                related_memory_ids=[],
                language="en",
                sentiment="neutral",
                importance=5,
                confidence=1.0,
                sensitivity=SensitivityLevel.PUBLIC,
                access_count=0,
                last_accessed=None,
                embedding=None,
                version=1,
                created_by="MemoryManager",
                updated_at=None
            )
            
            # Save to SQLite
            await self.sqlite_store.save_memory(memory)
            
            # Index in Vector Store
            self.vector_store.add_document(
                text=f"Project: {name}\nDescription: {description}",
                metadata={"type": "project", "name": name, "id": memory.id}
            )
            
            # Add to Graph
            self.graph_store.add_node(name, "Project", {"description": description})
            
            return {"success": True, "message": f"Created project '{name}'", "path": "sqlite://memory"}
            
        except Exception as e:
            logger.error(f"Failed to create project {name}: {e}")
            return {"success": False, "message": f"Error creating project: {str(e)}"}

    async def save_thought(self, content: str, project_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Save a thought/note to SQLite + Vector + Graph.
        """
        try:
            # 1. Auto-Summarize
            summary_data = await self.auto_summarize(content)
            
            # 2. Create Memory Object
            memory_id = str(uuid.uuid4())
            timestamp = datetime.datetime.now()
            
            memory = Memory(
                id=memory_id,
                timestamp=timestamp,
                source=MemorySource.MANUAL,
                project=project_name or "Inbox",
                topic=summary_data.get("summary", "Note"),
                type=MemoryType.NOTE,
                tags=summary_data.get("tags", []),
                ultra_brief=summary_data.get("summary", ""),
                executive_summary=[], 
                detailed_summary=summary_data.get("key_points", ""),
                raw_content=content,
                # Defaults
                decisions=[],
                action_items=[],
                open_questions=[],
                key_insights=[],
                people_mentioned=[],
                projects_mentioned=[],
                conversation_id=None,
                parent_memory_id=None,
                related_memory_ids=[],
                language="en",
                sentiment="neutral",
                importance=3,
                confidence=1.0,
                sensitivity=SensitivityLevel.PRIVATE,
                access_count=0,
                last_accessed=None,
                embedding=None,
                version=1,
                created_by="MemoryManager",
                updated_at=None
            )
            
            # 3. Transactional Save
            # Step A: Save to SQLite (Primary Source of Truth)
            await self.sqlite_store.save_memory(memory)
            
            try:
                # Step B: Index in Vector Store
                self.vector_store.add_document(
                    text=content,
                    metadata={
                        "type": "note",
                        "project": project_name or "Inbox",
                        "id": memory_id,
                        "summary": summary_data.get('summary', '')
                    }
                )
                
                # Step C: Add to Graph
                self.graph_store.add_node(memory_id, "Note", {"summary": summary_data.get('summary', '')})
                if project_name:
                    self.graph_store.add_edge(memory_id, project_name, "PART_OF")
                    
                for tag in summary_data.get('tags', []):
                    tag_id = tag.lower().replace(" ", "_")
                    self.graph_store.add_node(tag_id, "Concept")
                    self.graph_store.add_edge(memory_id, tag_id, "MENTIONS")
                    
            except Exception as vector_error:
                # ROLLBACK: If Vector/Graph fails, delete from SQLite to maintain consistency
                logger.error(f"Vector/Graph index failed: {vector_error}. Rolling back SQLite.")
                await self.sqlite_store.delete_memory(memory_id)
                raise vector_error

            return {
                "success": True, 
                "message": f"Saved note to memory",
                "summary": summary_data.get('summary')
            }
            
        except Exception as e:
            logger.error(f"Failed to save thought: {e}")
            return {"success": False, "message": str(e)}

    async def auto_summarize(self, content: str) -> Dict[str, Any]:
        """
        Use LLM to summarize content and extract tags.
        """
        prompt = f"""
Analyze the following text and provide a JSON output with:
1. "summary": A one-sentence executive summary.
2. "key_points": A markdown list of key points.
3. "tags": A list of 3-5 relevant tags.

Text:
{content}
"""
        try:
            response = await self.llm_router.generate_with_gemini(prompt)
            
            import json
            import re
            
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                return {
                    "summary": response[:100] + "...",
                    "key_points": response,
                    "tags": ["general"]
                }
                
        except Exception as e:
            logger.error(f"Auto-summarize failed: {e}")
            return {
                "summary": "Auto-summary failed",
                "key_points": "-",
                "tags": ["error"]
            }

    async def search_memory(self, query: str) -> List[Dict[str, Any]]:
        """
        Search using Vector Store and return formatted results.
        """
        results = self.vector_store.search(query)
        return results

    async def search(self, query: str, limit: int = 5) -> List[Any]:
        """
        Alias for search_memory to match Secretary usage.
        Returns objects with .content attribute if possible, or dicts.
        Secretary expects objects with .content attribute?
        Let's check Secretary usage: `m.content`.
        Vector store returns dicts.
        I should wrap the result in a simple object or ensure dict access works.
        Secretary code: `[f"- {m.content}" for m in recent_memories]`
        So it expects an object with .content.
        """
        results = self.vector_store.search(query, limit=limit)
        
        class MemoryResult:
            def __init__(self, text, meta):
                self.content = text
                self.metadata = meta
                
        return [MemoryResult(r['text'], r['metadata']) for r in results]

# Singleton
_memory_manager = None

def get_memory_manager():
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
