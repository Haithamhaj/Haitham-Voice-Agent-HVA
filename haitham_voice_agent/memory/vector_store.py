import logging
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Vector Store Manager (Layer 2)
    Handles semantic search using ChromaDB and local embeddings.
    """
    
    def __init__(self):
        self.memory_root = Path.home() / "HVA_Memory" / "VectorDB"
        self.memory_root.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        try:
            self.client = chromadb.PersistentClient(path=str(self.memory_root))
            self.collection = self.client.get_or_create_collection(name="hva_memory")
            logger.info(f"ChromaDB initialized at {self.memory_root}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.client = None
            self.collection = None

        # Initialize Embedding Model
        try:
            # lightweight model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded: all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.model = None

    def add_document(self, text: str, metadata: Dict[str, Any] = None):
        """
        Add a document to the vector store.
        """
        if not self.collection or not self.model:
            logger.warning("Vector store not initialized properly.")
            return

        try:
            # Generate ID
            doc_id = str(uuid.uuid4())
            
            # Generate Embedding
            embedding = self.model.encode(text).tolist()
            
            # Add to collection
            self.collection.add(
                documents=[text],
                embeddings=[embedding],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )
            logger.info(f"Added document to vector store: {doc_id}")
            
        except Exception as e:
            logger.error(f"Error adding document to vector store: {e}")

    def search(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant documents.
        """
        if not self.collection or not self.model:
            return []

        try:
            # Generate query embedding
            query_embedding = self.model.encode(query).tolist()
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    meta = results['metadatas'][0][i] if results['metadatas'] else {}
                    formatted_results.append({
                        "content": doc,
                        "metadata": meta,
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []

# Singleton
_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
