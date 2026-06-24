import os
import hashlib
import math
import re
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import Chroma
import chromadb
from chromadb.config import Settings
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

COLLECTION_NAME = "fpna_documents_hash"


class HashingEmbeddings(Embeddings):
    """Small deterministic local embedder used when no embedding API is available."""

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def _embed_text(self, text: str) -> List[float]:
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        if not tokens:
            tokens = [text.lower()]

        vector = [0.0] * self.dimensions
        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "little") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm:
            vector = [value / norm for value in vector]
        return vector

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_text(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_text(text)


class VectorStore:
    """Manages vector database operations with proper store access"""
    
    def __init__(self):
        self.embedding_model = self._get_embedding_model()
        self.vector_store = self._initialize_vector_store()
        # 🔴 CRITICAL FIX: Create a store attribute for compatibility
        self.store = self.vector_store  # This makes self.store.similarity_search work
        
    def _get_embedding_model(self):
        """Get local deterministic embeddings."""
        embedding_model = HashingEmbeddings()
        logger.info("Using local hashing embeddings")
        return embedding_model
    
    def _initialize_vector_store(self):
        """Initialize vector store based on configuration"""
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        
        if settings.VECTOR_DB_TYPE == "chroma":
            return self._init_chroma()
        else:
            raise ValueError(f"Unsupported vector DB type: {settings.VECTOR_DB_TYPE}")

    def _get_chroma_client(self):
        return chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
    
    def _init_chroma(self):
        """Initialize ChromaDB vector store"""
        try:
            # Check if collection already exists
            client = self._get_chroma_client()
            
            try:
                # Try to get existing collection
                collection = client.get_collection(COLLECTION_NAME)
                logger.info(f"Loaded existing ChromaDB collection with {collection.count()} documents")
                
                # Create Chroma instance with existing collection
                chroma_store = Chroma(
                    client=client,
                    collection_name=COLLECTION_NAME,
                    embedding_function=self.embedding_model
                )
                
            except:
                # Create new collection
                logger.info("Creating new ChromaDB collection")
                chroma_store = Chroma(
                    client=client,
                    embedding_function=self.embedding_model,
                    collection_name=COLLECTION_NAME
                )
            
            logger.info(f"Initialized ChromaDB at {settings.CHROMA_PERSIST_DIR}")
            return chroma_store
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            # Try simple initialization
            try:
                client = self._get_chroma_client()
                chroma_store = Chroma(
                    client=client,
                    embedding_function=self.embedding_model,
                    collection_name=COLLECTION_NAME
                )
                logger.info(f"Simple ChromaDB initialization successful")
                return chroma_store
            except Exception as e2:
                logger.error(f"Failed simple initialization too: {e2}")
                raise
    
    def add_documents(self, documents: List[Document]):
        """Add documents to vector store"""
        try:
            if not documents:
                logger.warning("No documents to add")
                return
            
            # Check if vector_store has add_documents method
            if hasattr(self.vector_store, 'add_documents'):
                self.vector_store.add_documents(documents)
                logger.info(f"Added {len(documents)} documents to vector store")
                
            else:
                logger.warning("Vector store doesn't support add_documents, using from_documents")
                # Create new store with all documents
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embedding_model,
                    client=self._get_chroma_client(),
                    collection_name=COLLECTION_NAME
                )
                self.store = self.vector_store  # Update store reference
                logger.info(f"Created new vector store with {len(documents)} documents")
                
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            # Try alternative method
            try:
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embedding_model,
                    client=self._get_chroma_client(),
                    collection_name=COLLECTION_NAME
                )
                self.store = self.vector_store
                logger.info(f"Alternative method: Created store with {len(documents)} documents")
            except Exception as e2:
                logger.error(f"Failed to add documents: {e2}")
                raise
    
    def similarity_search(self, query: str, k: int = 5, filter_dict: Optional[dict] = None) -> List[Document]:
        """Search for similar documents - MAIN SEARCH METHOD"""
        try:
            # First try the vector_store attribute
            if hasattr(self.vector_store, 'similarity_search'):
                if filter_dict:
                    return self.vector_store.similarity_search(
                        query=query,
                        k=k,
                        filter=filter_dict
                    )
                else:
                    return self.vector_store.similarity_search(
                        query=query,
                        k=k
                    )
            # Then try the store attribute
            elif hasattr(self, 'store') and hasattr(self.store, 'similarity_search'):
                if filter_dict:
                    return self.store.similarity_search(
                        query=query,
                        k=k,
                        filter=filter_dict
                    )
                else:
                    return self.store.similarity_search(
                        query=query,
                        k=k
                    )
            else:
                logger.warning("No similarity_search method found")
                return []
                
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    # 🔴 NEW: Direct search method for retriever
    def search(self, query: str, k: int = 5) -> List[Document]:
        """Simple search interface for retriever"""
        return self.similarity_search(query, k)
    
    def get_document_count(self) -> int:
        """Get number of documents in vector store"""
        try:
            # Try to get count from Chroma client
            client = self._get_chroma_client()
            try:
                collection = client.get_collection(COLLECTION_NAME)
                count = collection.count()
                logger.info(f"Vector store has {count} documents")
                return count
            except:
                return 0
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    def clear(self):
        """Clear all documents from vector store"""
        try:
            client = self._get_chroma_client()
            try:
                client.delete_collection(COLLECTION_NAME)
            except Exception:
                logger.info("ChromaDB collection did not exist")
            logger.info("Cleared ChromaDB collection")
            
            # Reinitialize
            self.vector_store = self._init_chroma()
            self.store = self.vector_store
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
    
    # 🔴 NEW: Get the underlying store for compatibility
    def get_store(self):
        """Get the underlying store object"""
        return self.store if hasattr(self, 'store') else self.vector_store
