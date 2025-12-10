import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from .models.memory import Memory, MemoryType, MemorySource, SensitivityLevel
from .storage.sqlite_store import SQLiteStore
from .storage.vector_store import VectorStore
from .storage.graph_store import GraphStore
from .intelligence.classifier import SmartClassifier
from .intelligence.summarizer import Summarizer
from .utils.embeddings import EmbeddingGenerator
from haitham_voice_agent.intelligence.file_router import file_router
from haitham_voice_agent.intelligence.content_extractor import content_extractor
from haitham_voice_agent.intelligence.smart_summarizer import smart_summarizer

logger = logging.getLogger(__name__)

class MemorySystem:
    """
    Main entry point for the Advanced Memory System.
    Coordinates input processing, intelligence, storage, and retrieval.
    """
    
    def __init__(self):
        self.sqlite_store = SQLiteStore()
        self.vector_store = VectorStore()
        self.graph_store = GraphStore()
        self.classifier = SmartClassifier()
        self.summarizer = Summarizer()
        self.embedding_generator = EmbeddingGenerator()
        
    async def initialize(self):
        """Initialize storage systems"""
        await self.sqlite_store.initialize()
        await self.graph_store.initialize()

    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics from all memory stores"""
        try:
            # SQLite Stats
            sql_count = 0
            if hasattr(self.sqlite_store, "count_memories"):
                sql_count = await self.sqlite_store.count_memories()
            elif hasattr(self.sqlite_store, "get_stats"):
                s = await self.sqlite_store.get_stats()
                sql_count = s.get("count", 0)
                
            # Vector Stats
            vec_count = 0
            if hasattr(self.vector_store, "count"):
                vec_count = self.vector_store.count()
                
            # Graph Stats
            graph_count = 0
            if hasattr(self.graph_store, "count_nodes"):
                graph_count = await self.graph_store.count_nodes()
                
            return {
                "sql_records": sql_count,
                "vector_embeddings": vec_count,
                "graph_nodes": graph_count,
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e), "status": "error"}

    # ... (existing methods) ...

    async def suggest_file_project(self, path: str) -> Optional[Dict[str, Any]]:
        """Suggest a project for a new file"""
        result = await file_router.classify_file(path)
        if result.confidence > 0.4 and result.candidates:
            return {
                "path": result.path,
                "project_id": result.candidates[0].project_id,
                "confidence": result.confidence,
                "reason": result.candidates[0].reason,
                "predicted_type": result.predicted_type
            }
        return None



    async def ingest_file(self, path: str, project_id: str, description: str = None, tags: List[str] = None) -> bool:
        """
        Ingest a file into all 3 memory layers (SQLite, Vector, Graph)
        """
        try:
            # 0. Extract Content & Summarize (Smart Layer)
            extracted_text = content_extractor.extract_text(path)
            final_description = description
            
            if extracted_text:
                logger.info(f"Extracted {len(extracted_text)} chars from {path}")
                
                # Generate summary if no description provided
                if not final_description:
                    final_description = await smart_summarizer.summarize_content(extracted_text)
                    logger.info(f"Generated summary: {final_description}")
            
            # 1. SQLite & Vector (via index_file)
            # Pass extracted text for deep indexing
            index_success = await self.index_file(
                path, 
                project_id, 
                final_description or "", 
                tags or [],
                content=extracted_text
            )
            
            if not index_success:
                return False
                
            # 2. Graph Store
            # Create File Node
            await self.graph_store.add_node(path, "File", {"description": final_description})
            
            # ... (rest of graph logic) ...
            
            # Create Project Node (ensure exists)
            await self.graph_store.add_node(project_id, "Project", {})
            
            # Link Project -> File
            await self.graph_store.add_edge(project_id, path, "HAS_FILE", {"since": datetime.now().isoformat()})
            
            # Link File -> Concepts (Tags)
            if tags:
                for tag in tags:
                    tag_id = f"concept:{tag.lower()}"
                    await self.graph_store.add_node(tag_id, "Concept", {"name": tag})
                    await self.graph_store.add_edge(path, tag_id, "REFERS_TO", {})
            
            logger.info(f"Ingested file {path} into Project {project_id} (3-Layer)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ingest file {path}: {e}")
            return False

    async def index_file(self, path: str, project_id: str, description: str = "", tags: List[str] = None, content: str = None) -> bool:
        """
        Index a file in the memory system.
        Generates an embedding for the description/content to allow semantic search.
        """
        try:
            # Generate embedding
            # If we have full content, we should ideally chunk it.
            # For now, we'll embed the description + tags + (first 1000 chars of content)
            # to keep it simple and fast.
            # TODO: Implement full chunking for large files.
            
            content_snippet = content[:1000] if content else ""
            content_to_embed = f"{description} {' '.join(tags or [])} {content_snippet}"
            embedding = await self.embedding_generator.generate(content_to_embed)
            
            # ... (rest of indexing logic) ...
            
            # Create Project Node (ensure exists)
            await self.graph_store.add_node(project_id, "Project", {})
            
            # Link Project -> File
            await self.graph_store.add_edge(project_id, path, "HAS_FILE", {"since": datetime.now().isoformat()})
            
            # Link File -> Concepts (Tags)
            if tags:
                for tag in tags:
                    tag_id = f"concept:{tag.lower()}"
                    await self.graph_store.add_node(tag_id, "Concept", {"name": tag})
                    await self.graph_store.add_edge(path, tag_id, "REFERS_TO", {})
            
            logger.info(f"Ingested file {path} into Project {project_id} (3-Layer)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ingest file {path}: {e}")
            return False
        
    async def add_memory(
        self, 
        content: str, 
        source: Union[MemorySource, str] = MemorySource.MANUAL,
        context: Optional[str] = None
    ) -> Optional[Memory]:
        """
        Process and store a new memory
        """
        try:
            # 1. Generate Embedding
            embedding = await self.embedding_generator.generate(content)
            
            # 2. Classify
            classification = await self.classifier.classify(content, context)
            
            # 3. Summarize
            summary = await self.summarizer.summarize(content)
            
            # 4. Create Memory Object
            memory_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            # Handle source enum
            if isinstance(source, str):
                try:
                    source_enum = MemorySource(source.lower())
                except ValueError:
                    source_enum = MemorySource.MANUAL
            else:
                source_enum = source
            
            # Handle type enum
            try:
                type_enum = MemoryType(classification.get("type", "note").lower())
            except ValueError:
                type_enum = MemoryType.NOTE
                
            memory = Memory(
                id=memory_id,
                timestamp=timestamp,
                source=source_enum,
                project=classification.get("project", "General"),
                topic=classification.get("topic", "Unclassified"),
                type=type_enum,
                tags=classification.get("tags", []),
                ultra_brief=summary.get("ultra_brief", ""),
                executive_summary=summary.get("executive_summary", []),
                detailed_summary=summary.get("detailed_summary", ""),
                raw_content=content,
                decisions=summary.get("decisions", []),
                action_items=summary.get("action_items", []),
                open_questions=summary.get("open_questions", []),
                key_insights=summary.get("key_insights", []),
                people_mentioned=summary.get("people_mentioned", []),
                projects_mentioned=summary.get("projects_mentioned", []),
                language="en", # TODO: Detect language
                sentiment=classification.get("sentiment", "neutral"),
                importance=classification.get("importance", 3),
                confidence=classification.get("confidence", 1.0),
                sensitivity=SensitivityLevel.PRIVATE,
                embedding=embedding
            )
            
            # 5. Save to SQLite
            await self.sqlite_store.save_memory(memory)
            
            # 6. Save to Vector Store
            metadata = {
                "project": memory.project,
                "topic": memory.topic,
                "type": memory.type.value,
                "timestamp": memory.timestamp.isoformat()
            }
            self.vector_store.add_embedding(memory_id, embedding, metadata)
            
            logger.info(f"Memory stored: {memory_id} ({memory.project} - {memory.topic})")
            return memory
            
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return None

    async def search_memories(
        self, 
        query: str, 
        limit: int = 5,
        project: Optional[str] = None
    ) -> List[Memory]:
        """
        Semantic search for memories
        """
        try:
            # 1. Generate query embedding
            query_embedding = await self.embedding_generator.generate(query)
            
            # 2. Search Vector Store
            filter_criteria = {}
            if project:
                filter_criteria["project"] = project
                
            vector_results = self.vector_store.search(
                query_embedding, 
                limit=limit,
                filter_criteria=filter_criteria if filter_criteria else None
            )
            
            # 3. Retrieve full objects from SQLite
            memories = []
            for result in vector_results:
                memory_id = result["id"]
                memory = await self.sqlite_store.get_memory(memory_id)
                if memory:
                    memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete memory from all stores"""
        try:
            sqlite_success = await self.sqlite_store.delete_memory(memory_id)
            vector_success = self.vector_store.delete_embedding(memory_id)
            return sqlite_success and vector_success
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    async def index_file(self, path: str, project_id: str, description: str = "", tags: List[str] = None, content: str = None, file_hash: str = None) -> bool:
        """
        Index a file in the memory system.
        Generates an embedding for the description/content to allow semantic search.
        """
        try:
            # Generate embedding
            # If we have full content, we should ideally chunk it.
            # For now, we'll embed the description + tags + (first 1000 chars of content)
            # to keep it simple and fast.
            # TODO: Implement full chunking for large files.
            
            content_snippet = content[:1000] if content else ""
            content_to_embed = f"{description} {' '.join(tags or [])} {content_snippet}"
            embedding = await self.embedding_generator.generate(content_to_embed)
            
            # Store embedding in Vector Store (using path as ID, or a hash)
            # Using path as ID might be tricky if path changes, but for now it's the PK
            # Let's use a deterministic hash of the path as the vector ID
            import hashlib
            vector_id = hashlib.md5(path.encode()).hexdigest()
            
            metadata = {
                "type": "file",
                "project": project_id,
                "path": path,
                "timestamp": datetime.now().isoformat()
            }
            self.vector_store.add_embedding(vector_id, embedding, metadata)
            
            # Store in SQLite File Index
            return await self.sqlite_store.index_file(path, project_id, description, tags, vector_id, file_hash)
            
        except Exception as e:
            logger.error(f"Failed to index file {path}: {e}")
            return False


    async def search_files(self, query: str, project_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for files using a smart ranking system:
        Aggregates Semantic + Text + Transliterated matches, scores them, and returns top results.
        """
        try:
            candidates: Dict[str, Dict[str, Any]] = {}
            
            # Helper to add/update candidate
            async def add_candidate(path, score_type, score_val, source_match_data=None):
                if not path: return
                
                if path not in candidates:
                    # Fetch details if new
                    file_data = await self.sqlite_store.get_file_index(path)
                    if file_data:
                        candidates[path] = file_data
                        candidates[path]["_scores"] = {score_type: score_val}
                        candidates[path]["score"] = score_val # Base score
                else:
                    # Update score if existing
                    candidates[path]["_scores"][score_type] = score_val
                    # Keep max score or additive? Let's do additive bonuses on top of base vector
                    
            # 1. Semantic Search (Vector) - Base source of truth for "meaning"
            query_embedding = await self.embedding_generator.generate(query)
            filter_criteria = {"type": "file"}
            if project_id:
                filter_criteria["project"] = project_id
                
            # Fetch more than limit to allow re-ranking
            vector_results = self.vector_store.search(query_embedding, limit=limit * 2, filter_criteria=filter_criteria)
            
            for res in vector_results:
                await add_candidate(res["metadata"].get("path"), "vector", res["score"])

            # 2. Text Search (Exact/Partial) - High precision bonus
            text_results = await self.sqlite_store.search_file_index(query)
            for res in text_results:
                await add_candidate(res["path"], "text", 1.0)

            # 3. Transliteration Search (Arabic -> Latin) - Fallback bonus
            # e.g. "كرافت" -> "kraft" to match "CRAFTS"
            import re
            arabic_to_latin = {
                'ا': 'a', 'أ': 'a', 'إ': 'e', 'آ': 'a',
                'ب': 'b', 'ت': 't', 'ث': 'th',
                'ج': 'j', 'ح': 'h', 'خ': 'kh',
                'د': 'd', 'ذ': 'th', 'ر': 'r', 'ز': 'z',
                'س': 's', 'ش': 'sh', 'ص': 's', 'ض': 'd',
                'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh',
                'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l',
                'م': 'm', 'ن': 'n', 'ه': 'h', 'و': 'w',
                'ي': 'y', 'ى': 'a', 'ة': 'a', 'ء': '',
            }
            transliterated = ''.join(arabic_to_latin.get(c, c) for c in query)
            
            if transliterated != query:
                trans_results = await self.sqlite_store.search_file_index(transliterated)
                for res in trans_results:
                    await add_candidate(res["path"], "transliterated", 0.9)

            # 4. Smart Ranking / Scoring Logic
            ranked_results = []
            for path, data in candidates.items():
                scores = data.get("_scores", {})
                
                # Base Score: Vector (or 0.0 if not found in vector search)
                final_score = scores.get("vector", 0.0)
                
                # Boosters
                if scores.get("text"):
                    final_score += 0.3 # Strong bonus for text match
                    
                if scores.get("transliterated"):
                    final_score += 0.2 # Moderate bonus for transliteration match
                
                # Filename exact match bonus (if query is short/specific)
                filename = path.split('/')[-1].lower()
                query_lower = query.lower()
                if query_lower in filename:
                    final_score += 0.1
                if query_lower == filename:
                     final_score += 0.3
                
                data["score"] = final_score
                ranked_results.append(data)
                
            # Sort by Descending Score
            ranked_results.sort(key=lambda x: x["score"], reverse=True)
            
            return ranked_results[:limit]
            
        except Exception as e:
            logger.error(f"File search failed: {e}", exc_info=True)
            return []

# Singleton instance
memory_system = MemorySystem()
