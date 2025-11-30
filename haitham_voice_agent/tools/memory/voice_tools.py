import logging
from typing import Optional, Dict, Any

from haitham_voice_agent.tools.memory.memory_system import MemorySystem
from haitham_voice_agent.tools.memory.models.memory import MemorySource

logger = logging.getLogger(__name__)

class VoiceMemoryTools:
    """
    High-level voice tools for Memory interaction.
    """
    
    def __init__(self):
        self.memory_system = MemorySystem()
        self._initialized = False
        
    async def ensure_initialized(self):
        if not self._initialized:
            await self.memory_system.initialize()
            self._initialized = True
            
    async def process_voice_note(self, audio_text: str) -> Dict[str, Any]:
        """
        Process a raw voice note and save it as a memory AND a local Markdown file.
        
        Args:
            audio_text: The transcribed text from STT
            
        Returns:
            Dict with result details
        """
        try:
            await self.ensure_initialized()
            
            logger.info(f"Processing voice note: {audio_text[:50]}...")
            
            # Save to memory (this handles classification and summarization)
            memory = await self.memory_system.add_memory(
                content=audio_text,
                source=MemorySource.VOICE,
                context="Voice Note"
            )
            
            if memory:
                # --- NEW: Save to Local Workspace as Markdown ---
                from haitham_voice_agent.tools.workspace_manager import workspace_manager
                from datetime import datetime
                
                # Determine project (fallback to 'inbox' if None or 'unknown')
                project_id = memory.project if memory.project and memory.project.lower() != "unknown" else "inbox"
                
                # Ensure project structure
                workspace_manager.ensure_project_structure(project_id)
                
                # Generate filename
                date_str = datetime.now().strftime("%Y-%m-%d")
                # Create a slug from the ultra_brief or first few words
                slug = memory.ultra_brief.replace(" ", "_")[:30] if memory.ultra_brief else "voice_note"
                slug = workspace_manager._sanitize_filename(slug)
                filename = f"{date_str}_{slug}.md"
                
                file_path = workspace_manager.project_notes_dir(project_id) / filename
                
                # Content
                md_content = f"""# {memory.ultra_brief or 'Voice Note'}
Date: {date_str}
Project: {project_id}
Source: Voice

## Content
{audio_text}

## Summary
{memory.ultra_brief}

## Decisions
{self._format_list(memory.decisions)}

## Next Actions
{self._format_list(memory.action_items)}
"""
                # Write file
                file_path.write_text(md_content, encoding="utf-8")
                logger.info(f"Saved Markdown note to: {file_path}")
                
                return {
                    "success": True,
                    "message": f"Saved to {project_id}",
                    "memory_id": memory.id,
                    "summary": memory.ultra_brief,
                    "file_path": str(file_path)
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save memory"
                }
                
        except Exception as e:
            logger.error(f"Voice memory processing failed: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    def _format_list(self, items: Optional[list]) -> str:
        if not items:
            return "- None"
        return "\n".join([f"- {item}" for item in items])

    async def search_memory_voice(self, query_text: str, language: str = "en") -> str:
        """
        Search memories via voice and return a spoken response.
        
        Args:
            query_text: The search query
            language: "ar" or "en"
            
        Returns:
            str: The response text to be spoken
        """
        try:
            await self.ensure_initialized()
            
            results = await self.memory_system.search_memories(query_text, limit=3)
            
            if not results:
                return "لم أجد أي ملاحظات مرتبطة." if language == "ar" else "I couldn't find any relevant memories."
            
            # Format response
            if language == "ar":
                response = f"وجدت {len(results)} نتائج. "
                top = results[0]
                response += f"الأهم هي من مشروع {top.project}: {top.ultra_brief}. "
                if len(results) > 1:
                    topics = [r.topic for r in results[1:]]
                    # Simple join for Arabic
                    response += "وجدت أيضاً ملاحظات عن: " + "، ".join(topics)
            else:
                response = f"I found {len(results)} relevant items. "
                top = results[0]
                response += f"The most relevant is from {top.project}: {top.ultra_brief}. "
                if len(results) > 1:
                    response += "I also found related notes about " + \
                               ", ".join([r.topic for r in results[1:]]) + "."
                           
            return response
            
        except Exception as e:
            logger.error(f"Voice search failed: {e}")
            return "واجهت مشكلة في البحث." if language == "ar" else "I encountered an error while searching your memories."
