import json
import logging
from typing import Dict, Any

from haitham_voice_agent.llm_router import LLMRouter
from . import prompts

logger = logging.getLogger(__name__)

class Summarizer:
    """
    Multi-level summarizer using LLM
    """
    
    def __init__(self):
        self.router = LLMRouter()
        
    async def summarize(self, content: str) -> Dict[str, Any]:
        """
        Generate summaries using LLM
        """
        try:
            prompt = prompts.SUMMARIZE_MEMORY_PROMPT.format(
                content=content[:8000]  # Truncate if too long
            )
            
            # Use Gemini for heavy text processing/summarization
            # But we need JSON output, so GPT might be safer for structure, 
            # or Gemini with strict instructions. SRS says Gemini for summarization.
            # Let's try Gemini first, but handle parsing carefully.
            # Actually, for complex JSON structure, GPT-4o is more reliable.
            # The SRS says "Gemini (Analytical Tasks): Summarization".
            # I'll use Gemini but ensure I can parse the JSON.
            
            response = await self.router.generate_with_gemini(
                prompt=prompt,
                temperature=0.3,
                logical_model="logical.gemini.pro"
            )
            
            # Parse JSON
            if isinstance(response, str):
                clean_response = response.replace("```json", "").replace("```", "").strip()
                try:
                    return json.loads(clean_response)
                except json.JSONDecodeError:
                    # Fallback or retry? For now, simple fallback
                    logger.warning("Failed to parse Gemini JSON, falling back to simple summary")
                    return {
                        "ultra_brief": content[:50] + "...",
                        "executive_summary": ["Summary generation failed"],
                        "detailed_summary": content[:200] + "...",
                        "key_insights": [],
                        "decisions": [],
                        "action_items": [],
                        "open_questions": [],
                        "people_mentioned": [],
                        "projects_mentioned": []
                    }
            return response
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return {
                "ultra_brief": "Error generating summary",
                "executive_summary": [],
                "detailed_summary": "Error generating summary",
                "key_insights": [],
                "decisions": [],
                "action_items": [],
                "open_questions": [],
                "people_mentioned": [],
                "projects_mentioned": []
            }
