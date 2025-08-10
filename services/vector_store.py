"""
Vector store service using FAISS for efficient similarity search
"""
import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple, Optional
from loguru import logger

from config import settings
from models.schemas import DocumentChunk, SearchResult
from services.embedding_service import EmbeddingService


class VectorStore:
    """FAISS-based vector store for document embeddings"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.index = None
        self.chunks = []
        self.dimension = settings.vector_dimension
        self.index_path = settings.faiss_index_path
        self._document_hash = None  # Track current document for caching
        
    async def initialize(self):
        """Initialize the embedding service and FAISS index"""
        try:
            logger.info("Initializing vector store...")

            # Initialize embedding service
            await self.embedding_service.initialize()
            self.dimension = self.embedding_service.get_dimension()

            # Initialize FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity

            # Try to load existing index
            await self._load_index()

            provider_info = self.embedding_service.get_provider_info()
            logger.info(f"Vector store initialized with {provider_info}")

        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    async def add_documents(self, chunks: List[DocumentChunk], document_hash: str = None) -> None:
        """
        Add document chunks to the vector store with caching

        Args:
            chunks: List of document chunks to add
            document_hash: Hash of the document for caching
        """
        try:
            if not chunks:
                logger.warning("No chunks provided to add to vector store")
                return

            # Check if we already have this document processed
            if document_hash and self._document_hash == document_hash and len(self.chunks) > 0:
                logger.info(f"Document already processed (hash: {document_hash[:8]}...), skipping embedding generation")
                return

            logger.info(f"Adding {len(chunks)} chunks to vector store")

            # Clear existing data for new document
            self.chunks = []
            self.index.reset()

            # Generate embeddings for all chunks in batches
            texts = [chunk.content for chunk in chunks]
            logger.info("Generating embeddings...")
            embeddings = await self.embedding_service.encode(texts, normalize=True)

            # Add embeddings to chunks
            for i, chunk in enumerate(chunks):
                chunk.embedding = embeddings[i].tolist()

            # Add to FAISS index
            self.index.add(embeddings.astype(np.float32))

            # Store chunks and document hash
            self.chunks = chunks
            self._document_hash = document_hash

            # Save index
            await self._save_index()

            logger.info(f"Successfully added {len(chunks)} chunks to vector store")

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    async def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Search for similar chunks using vector similarity
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of search results with similarity scores
        """
        try:
            if not self.chunks:
                logger.warning("No documents in vector store")
                return []
            
            logger.info(f"Searching for query: '{query[:50]}...' with top_k={top_k}")

            # Generate query embedding
            query_embedding = await self.embedding_service.encode_query(query)
            
            # Search in FAISS index
            scores, indices = self.index.search(
                query_embedding.astype(np.float32),
                min(top_k, len(self.chunks))
            )
            
            # Create search results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.chunks):  # Valid index
                    result = SearchResult(
                        chunk=self.chunks[idx],
                        score=float(score),
                        rank=i + 1
                    )
                    results.append(result)
            
            logger.info(f"Found {len(results)} search results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise
    
    async def get_relevant_context(self, query: str, max_chunks: int = 3) -> str:
        """
        Get relevant context for a query by combining top matching chunks
        
        Args:
            query: Search query
            max_chunks: Maximum number of chunks to include
            
        Returns:
            Combined context text
        """
        try:
            search_results = await self.search(query, top_k=max_chunks)
            
            if not search_results:
                return ""
            
            # Combine chunks with score-based weighting
            context_parts = []
            for result in search_results:
                context_parts.append(f"[Score: {result.score:.3f}] {result.chunk.content}")
            
            context = "\n\n".join(context_parts)
            logger.info(f"Generated context with {len(context)} characters from {len(search_results)} chunks")
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            return ""
    
    async def _save_index(self) -> None:
        """Save FAISS index and chunks to disk"""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, f"{self.index_path}.faiss")
            
            # Save chunks
            with open(f"{self.index_path}.chunks", 'wb') as f:
                pickle.dump(self.chunks, f)
            
            logger.info("Vector store saved to disk")
            
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
    
    async def _load_index(self) -> None:
        """Load FAISS index and chunks from disk"""
        try:
            index_file = f"{self.index_path}.faiss"
            chunks_file = f"{self.index_path}.chunks"
            
            if os.path.exists(index_file) and os.path.exists(chunks_file):
                # Load FAISS index
                self.index = faiss.read_index(index_file)
                
                # Load chunks
                with open(chunks_file, 'rb') as f:
                    self.chunks = pickle.load(f)
                
                logger.info(f"Loaded vector store with {len(self.chunks)} chunks")
            else:
                logger.info("No existing vector store found, starting fresh")
                
        except Exception as e:
            logger.warning(f"Could not load existing vector store: {str(e)}")
            # Reset to fresh state
            self.index = faiss.IndexFlatIP(self.dimension)
            self.chunks = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        provider_info = self.embedding_service.get_provider_info()
        return {
            "total_chunks": len(self.chunks),
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "embedding_provider": provider_info
        }
