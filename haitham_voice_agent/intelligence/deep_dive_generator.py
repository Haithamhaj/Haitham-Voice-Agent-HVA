import logging
import json
from typing import Dict, Any, List

from haitham_voice_agent.ollama_orchestrator import get_orchestrator
from haitham_voice_agent.llm_router import get_router

logger = logging.getLogger(__name__)

class DeepDiveGenerator:
    """
    Generates a 'Deep Dive' podcast script (Host vs Guest) from content.
    Inspired by Open Notebook / Google NotebookLM.
    """
    
    def __init__(self):
        self.ollama = get_orchestrator()
        self.llm_router = get_router()
        # Default personalities
        self.host_name = "Sarah"
        self.guest_name = "Mike"
        
    async def generate_script(self, content: str, title: str = "Topic") -> Dict[str, Any]:
        """
        Generate a dialogue script.
        Returns:
            {
                "title": str,
                "script": List[Dict[str, str]], # [{"speaker": "Host", "text": "..."}]
                "raw_script": str
            }
        """
        if not content:
            return {"error": "No content provided"}
            
        logger.info(f"Generating Deep Dive Podcast for: {title}")
        
        # Truncate for context window if massive (TODO: use recursive summary if needed)
        # For script generation, key points are better than raw massive text.
        # But let's assume content passed is reasonable or already summarized.
        context = content[:15000] 
        
        prompt = f"""
        You are an expert podcast producer.
        Create a "Deep Dive" podcast script where two hosts ('{self.host_name}' and '{self.guest_name}') discuss the following content.
        
        Guidelines:
        - {self.host_name} (Host): Enthusiastic, introduces topics, asks questions, guides the flow.
        - {self.guest_name} (Guest/Expert): Analytical, explains details, provides analogies, adds depth.
        - Tone: Conversational, engaging, "edutainment". Use interjections like "Exactly!", "Right?", "Wow".
        - Structure: Intro -> Key Point 1 -> Key Point 2 -> Summary/Outro.
        - Format: JSON List of objects: [{{"speaker": "{self.host_name}", "text": "..."}}, ...]
        
        Content to discuss:
        {context}
        
        Generate the JSON script directly.
        """
        
        try:
            # Prefer Cloud (Gemini) for long context creative writing
            response = await self.llm_router.generate_with_gemini(
                prompt,
                logical_model="logical.gemini.flash" 
            )
            raw_text = response.get("content", "").strip()
            
            # Parse JSON
            script = self._parse_json_script(raw_text)
            
            return {
                "title": f"Deep Dive: {title}",
                "script": script,
                "raw_script": raw_text
            }
            
        except Exception as e:
            logger.error(f"Podcast generation failed: {e}")
            return {"error": str(e)}

    def _parse_json_script(self, text: str) -> List[Dict[str, str]]:
        """Extract and parse JSON from LLM response"""
        try:
            # Clean Markdown
            cleaned = text
            if "```json" in text:
                cleaned = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                cleaned = text.split("```")[1].split("```")[0]
                
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON script. Returning raw text fallback.")
            # Fallback: simple text parsing if LLM failed JSON format
            lines = text.split('\n')
            script = []
            for line in lines:
                if ':' in line:
                    parts = line.split(':', 1)
                    script.append({"speaker": parts[0].strip(), "text": parts[1].strip()})
            return script

# Singleton
deep_dive_generator = DeepDiveGenerator()
