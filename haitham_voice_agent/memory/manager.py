import os
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import asyncio

from haitham_voice_agent.llm_router import LLMRouter
from haitham_voice_agent.config import Config
from haitham_voice_agent.memory.vector_store import get_vector_store
from haitham_voice_agent.memory.graph_store import get_graph_store

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Structured Local Memory Manager (Layer 1)
    Handles Projects, Concepts, and Auto-Summarization.
    """
    
    def __init__(self):
        self.memory_root = Path.home() / "HVA_Memory"
        self.projects_dir = self.memory_root / "Projects"
        self.concepts_dir = self.memory_root / "Concepts"
        self.archives_dir = self.memory_root / "Archives"
        self.inbox_dir = self.memory_root / "Inbox"
        
        self.llm_router = LLMRouter()
        self.vector_store = get_vector_store()
        self.graph_store = get_graph_store()
        
        # Ensure structure exists
        self.initialize_memory()
            
    def initialize_memory(self):
        """Create basic directory structure"""
        for d in [self.projects_dir, self.concepts_dir, self.archives_dir, self.inbox_dir]:
            d.mkdir(parents=True, exist_ok=True)
            
    def create_project(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new project with standard structure.
        """
        safe_name = name.replace(" ", "_").replace("/", "-")
        project_path = self.projects_dir / safe_name
        
        if project_path.exists():
            return {"success": False, "message": f"Project '{name}' already exists."}
            
        try:
            # Create directories
            project_path.mkdir()
            (project_path / "context").mkdir()
            
            # Create Templates
            self._create_file(project_path / "overview.md", f"# {name}\n\n## Description\n{description}\n\n## Goals\n- [ ] Define goals\n")
            self._create_file(project_path / "decisions.md", f"# Decision Log for {name}\n\n| Date | Decision | Context |\n|---|---|---|\n")
            self._create_file(project_path / "tasks.md", f"# Tasks for {name}\n\n- [ ] Initial setup\n")
            
            # Index Project Description
            if description:
                self.vector_store.add_document(
                    text=f"Project: {name}\nDescription: {description}",
                    metadata={"type": "project", "name": name, "path": str(project_path)}
                )
                
            # Add to Graph
            self.graph_store.add_node(name, "Project", {"path": str(project_path)})
            
            return {"success": True, "message": f"Created project '{name}' at {project_path}", "path": str(project_path)}
            
        except Exception as e:
            logger.error(f"Failed to create project {name}: {e}")
            return {"success": False, "message": f"Error creating project: {str(e)}"}

    async def save_thought(self, content: str, project_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Save a thought/note, optionally linked to a project.
        Triggers auto-summarization.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Auto-Summarize
        summary_data = await self.auto_summarize(content)
        
        # 2. Format Note
        note_content = f"""
# Note - {timestamp}

## Content
{content}

## Summary
{summary_data.get('summary', 'No summary')}

## Key Points
{summary_data.get('key_points', '-')}

## Tags
{', '.join(summary_data.get('tags', []))}
"""
        
        # 3. Determine Location
        if project_name:
            # Find project (fuzzy match or exact)
            target_dir = self._find_project_dir(project_name)
            if not target_dir:
                return {"success": False, "message": f"Project '{project_name}' not found."}
            
            save_path = target_dir / "context" / f"note_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            meta_type = "project_note"
            meta_project = project_name
        else:
            save_path = self.inbox_dir / f"thought_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            meta_type = "thought"
            meta_project = "inbox"
            
        # 4. Save File
        self._create_file(save_path, note_content)
        
        # 5. Index in Vector Store
        self.vector_store.add_document(
            text=content,
            metadata={
                "type": meta_type,
                "project": meta_project,
                "path": str(save_path),
                "summary": summary_data.get('summary', '')
            }
        )
        
        # 6. Add to Graph
        note_id = save_path.name
        self.graph_store.add_node(note_id, "Note", {"path": str(save_path), "summary": summary_data.get('summary', '')})
        
        if project_name:
            self.graph_store.add_edge(note_id, project_name, "PART_OF")
            
        # Link tags as concepts
        for tag in summary_data.get('tags', []):
            tag_id = tag.lower().replace(" ", "_")
            self.graph_store.add_node(tag_id, "Concept")
            self.graph_store.add_edge(note_id, tag_id, "MENTIONS")
            if project_name:
                self.graph_store.add_edge(project_name, tag_id, "RELATED_TO")
        
        return {
            "success": True, 
            "message": f"Saved note to {save_path.name}",
            "summary": summary_data.get('summary')
        }

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
            # Use Gemini or GPT based on router config (defaulting to generic generate)
            # We assume generate returns a string, we might need to parse JSON if we want strict structure.
            # For simplicity, we'll ask for JSON and try to parse, or fallback to text.
            
            response = await self.llm_router.generate_with_gemini(prompt) # Prefer Gemini for analysis
            
            # Simple parsing (robustness needed in production)
            import json
            import re
            
            # Extract JSON block
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                # Fallback if no JSON found
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
        Search memory using vector store.
        """
        return self.vector_store.search(query)

    def _create_file(self, path: Path, content: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _find_project_dir(self, name: str) -> Optional[Path]:
        """Find project directory by name (case-insensitive)"""
        target = name.lower().replace(" ", "_")
        for p in self.projects_dir.iterdir():
            if p.is_dir() and p.name.lower() == target:
                return p
        return None

# Singleton
_memory_manager = None

def get_memory_manager():
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
