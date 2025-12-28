import logging
import json
from typing import List, Dict, Any

from haitham_voice_agent.intelligence.smart_summarizer import smart_summarizer
from haitham_voice_agent.tools.memory.storage.graph_store import GraphStore
from haitham_voice_agent.ollama_orchestrator import get_orchestrator
from haitham_voice_agent.llm_router import get_router

logger = logging.getLogger(__name__)

class KnowledgeGraphBuilder:
    """
    Extracts structural knowledge (Topics, Concepts) from content 
    and builds a local Knowledge Graph.
    """
    
    def __init__(self):
        self.graph_store = GraphStore()
        self.ollama = get_orchestrator()
        self.llm_router = get_router()
        self._initialized = False
        
    async def ensure_initialized(self):
        if not self._initialized:
            await self.graph_store.initialize()
            self._initialized = True

    async def build_document_tree(self, document_id: str, content: str, title: str = "Document"):
        """
        Analyze content and build a topic tree linked to the document.
        Steps:
        1. Extract Key Topics from content.
        2. Create Nodes for Topics.
        3. Create Edges (Document -> has_topic -> Topic).
        """
        await self.ensure_initialized()
        
        if not content:
            return
            
        logger.info(f"Building Knowledge Tree for: {title}")
        
        # 1. Extract Topics using LLM
        topics = await self._extract_topics(content)
        
        # 2. Create Document Node
        await self.graph_store.add_node(
            node_id=document_id,
            node_type="document",
            properties={"title": title}
        )
        
        # 3. Create Topic Nodes and Edges
        for topic in topics:
            topic_name = topic.get("name")
            description = topic.get("description", "")
            
            if not topic_name:
                continue
                
            # Normalize ID
            topic_id = f"topic:{topic_name.lower().replace(' ', '_')}"
            
            # Add Topic Node
            await self.graph_store.add_node(
                node_id=topic_id,
                node_type="topic",
                properties={"name": topic_name, "description": description}
            )
            
            # Add Edge (Document -> Topic)
            await self.graph_store.add_edge(
                source=document_id,
                target=topic_id,
                relation="has_topic",
                properties={"confidence": 1.0}
            )
            
            logger.info(f"Linked Topic: {topic_name} -> {title}")

    async def _extract_topics(self, content: str) -> List[Dict[str, str]]:
        """Ask LLM to extract top 5 topics as JSON"""
        
        prompt = f"""
        Analyze the following text and extract the top 5 key topics or concepts.
        Return ONLY a JSON list of objects with 'name' and 'description'.
        
        Text:
        {content[:4000]}
        
        Example Output:
        [
            {{"name": "Machine Learning", "description": "Study of algorithms..."}},
            {{"name": "Python", "description": "Programming language..."}}
        ]
        """
        
        try:
            # Try Local Qwen (JSON mode if possible, otherwise text parsing)
            # Using simple generation and text parsing for robustness
            response = await self.ollama.client.generate(
                model=self.ollama.model,
                prompt=prompt,
                options={"temperature": 0.1, "num_predict": 1000, "stop": ["```"]}
            )
            text_resp = response.get("response", "").strip()
            
            # Clean Markdown code blocks
            if "```json" in text_resp:
                text_resp = text_resp.split("```json")[1].split("```")[0].strip()
            elif "```" in text_resp:
                text_resp = text_resp.split("```")[1].split("```")[0].strip()
                
            return json.loads(text_resp)
            
        except Exception as e:
            logger.warning(f"Local topic extraction failed: {e}. Trying simple regex/fallback.")
            return []

# Singleton
knowledge_graph_builder = KnowledgeGraphBuilder()
