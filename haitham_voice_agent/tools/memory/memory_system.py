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
            return await self.sqlite_store.index_file(path, project_id, description, tags, vector_id)
            
        except Exception as e:
            logger.error(f"Failed to index file {path}: {e}")
            return False


    async def search_files(self, query: str, project_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for files using semantic search + text match
        """
        try:
            # 1. Semantic Search via Vector Store
            query_embedding = await self.embedding_generator.generate(query)
            filter_criteria = {"type": "file"}
            if project_id:
                filter_criteria["project"] = project_id
                
            vector_results = self.vector_store.search(query_embedding, limit=limit, filter_criteria=filter_criteria)
            
            # 2. Retrieve details from SQLite File Index
            results = []
            seen_paths = set()
            
            # Add vector results
            for res in vector_results:
                path = res["metadata"].get("path")
                if path and path not in seen_paths:
                    file_data = await self.sqlite_store.get_file_index(path)
                    if file_data:
                        file_data["score"] = res["score"]
                        results.append(file_data)
                        seen_paths.add(path)
            
            # 3. Fallback/Augment with Text Search (if few results)
            if len(results) < limit:
                text_results = await self.sqlite_store.search_file_index(query)
                for res in text_results:
                    if res["path"] not in seen_paths:
                        res["score"] = 0.5 # Arbitrary score for text match
                        results.append(res)
                        seen_paths.add(res["path"])
                        
            return results[:limit]
            
        except Exception as e:
            logger.error(f"File search failed: {e}")
            return []

# Singleton instance
memory_system = MemorySystem()
