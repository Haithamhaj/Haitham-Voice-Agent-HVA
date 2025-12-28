import logging
import textwrap
from typing import Optional, List, Dict, Any

from haitham_voice_agent.ollama_orchestrator import get_orchestrator
from haitham_voice_agent.llm_router import get_router

logger = logging.getLogger(__name__)

class SmartSummarizer:
    """
    Summarizes content using a Local-First strategy with Recursive Logic.
    1. Try Local Qwen (via Ollama).
    2. Fallback to Cloud (Gemini/GPT) via LLMRouter.
    """
    
    def __init__(self):
        self.ollama = get_orchestrator()
        self.llm_router = get_router()
        self.chunk_size = 4000  # Characters approx
        self.overlap = 200
        
    async def summarize_content(self, text: str, max_length: int = 2000) -> str:
        """Legacy Entry point: Generate a concise summary (single pass or simple)"""
        if not text:
            return ""
            
        # If text is short enough, just summarize directly
        if len(text) < self.chunk_size * 1.5:
             return await self._generate_summary(text, prompt_type="short")
             
        # Otherwise, use recursive
        result = await self.recursive_summarize(text)
        return result.get("final_summary", "")

    async def recursive_summarize(self, text: str) -> Dict[str, Any]:
        """
        Recursively summarizes large text.
        Returns:
            {
                "final_summary": str,
                "chunk_summaries": List[str],
                "structure": "Recursive"
            }
        """
        if not text:
            return {"final_summary": "", "chunk_summaries": []}

        # 1. Chunk the text
        chunks = self._chunk_text(text)
        logger.info(f"Recursive Summarization: Splitting {len(text)} chars into {len(chunks)} chunks")
        
        # 2. Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            # Contextual prompt for chunks
            summary = await self._generate_summary(chunk, prompt_type="chunk", index=i, total=len(chunks))
            if summary:
                chunk_summaries.append(summary)
        
        # 3. Final Pass: Summarize the summaries
        if len(chunk_summaries) == 1:
            final_summary = chunk_summaries[0]
        else:
            combined_summaries = "\n\n".join([f"- Part {i+1}: {s}" for i, s in enumerate(chunk_summaries)])
            final_summary = await self._generate_summary(combined_summaries, prompt_type="final")
            
        return {
            "final_summary": final_summary,
            "chunk_summaries": chunk_summaries,
            "raw_chunks": len(chunks)
        }

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        return textwrap.wrap(
            text, 
            width=self.chunk_size, 
            break_long_words=False, 
            break_on_hyphens=False,
            replace_whitespace=False
        )
        
    async def _generate_summary(self, text: str, prompt_type: str = "short", index: int=0, total: int=0) -> str:
        """Internal helper to call LLM"""
        
        # Select Prompt
        if prompt_type == "chunk":
            prompt = f"Summarize this section ({index+1}/{total}) of a larger document. Focus on key facts and topics:\n\n{text[:6000]}"
        elif prompt_type == "final":
            prompt = f"Create a cohesive final summary from these section summaries. Focus on the main narrative and key takeaways:\n\n{text[:6000]}"
        else:
            prompt = f"Summarize the following content in 2-3 concise sentences:\n\n{text[:4000]}"

        # 1. Try Local Qwen
        try:
            response = await self.ollama.client.generate(
                model=self.ollama.model,
                prompt=prompt,
                options={"temperature": 0.3, "num_predict": 500}
            )
            summary = response.get("response", "").strip()
            if summary:
                return summary
        except Exception as e:
            logger.warning(f"Local summarization failed: {e}")
            
        # 2. Fallback to Cloud (Gemini Flash)
        try:
            result = await self.llm_router.generate_with_gemini(
                prompt, logical_model="logical.gemini.flash"
            )
            return result["content"]
        except Exception as e:
            logger.error(f"Cloud summarization failed: {e}")
            return "Summary unavailable."

# Singleton
smart_summarizer = SmartSummarizer()
