"""
Embedding service supporting multiple APIs with automatic fallback
"""
import numpy as np
from typing import List, Union
from loguru import logger
import google.generativeai as genai

from config import settings
from services.multi_api_service import MultiAPIService

# Try to import sentence-transformers, but don't fail if not available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not available, using Gemini-only mode")
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class EmbeddingService:
    """Service for generating embeddings using different providers"""
    
    def __init__(self):
        self.provider = settings.embedding_provider
        self.gemini_model = None
        self.sentence_transformer_model = None
        self.dimension = settings.vector_dimension
        self.multi_api_service = MultiAPIService()  # Multi-API fallback system
        
    async def initialize(self):
        """Initialize the embedding service with multi-API support"""
        try:
            logger.info(f"Initializing embedding service with provider: {self.provider}")

            if self.provider == "multi":
                # Initialize multi-API service (including local LLM)
                await self.multi_api_service.initialize()
                provider_info = self.multi_api_service.get_current_provider_info()
                logger.info(f"Multi-API service initialized with {provider_info['available_providers']} providers")

                # Check if local LLM is available
                if self.multi_api_service.local_llm_available:
                    logger.info("🏠 Local LLM available for embeddings (free, no rate limits)")

                self.dimension = 768  # Standard dimension for most embedding models
            else:
                # Use single provider (legacy mode)
                await self._initialize_gemini()

            logger.info(f"Embedding service initialized with dimension: {self.dimension}")

        except Exception as e:
            logger.error(f"Error initializing embedding service: {str(e)}")
            raise
    
    async def _initialize_gemini(self):
        """Initialize Gemini embedding service"""
        try:
            # Configure Gemini API
            genai.configure(api_key=settings.gemini_api_key)
            
            # Test the connection and get model info
            model_info = genai.get_model(settings.gemini_embedding_model)
            logger.info(f"Using Gemini model: {model_info.name}")
            
            # Gemini embedding-001 produces 768-dimensional embeddings
            self.dimension = 768
            
        except Exception as e:
            logger.error(f"Error initializing Gemini: {str(e)}")
            raise
    
    async def _initialize_sentence_transformers(self):
        """Initialize sentence-transformers embedding service"""
        try:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                raise ImportError("sentence-transformers not available")

            self.sentence_transformer_model = SentenceTransformer(settings.embedding_model)
            self.dimension = self.sentence_transformer_model.get_sentence_embedding_dimension()

        except Exception as e:
            logger.error(f"Error initializing sentence-transformers: {str(e)}")
            raise
    
    async def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Generate embeddings for the given texts with automatic fallback

        Args:
            texts: Single text or list of texts to embed
            normalize: Whether to normalize embeddings for cosine similarity

        Returns:
            Numpy array of embeddings
        """
        try:
            if isinstance(texts, str):
                texts = [texts]

            if self.provider == "multi":
                # Use multi-API service with automatic fallback
                embeddings = await self.multi_api_service.generate_embeddings(texts)
            elif self.provider == "gemini":
                embeddings = await self._encode_with_gemini(texts)
            elif self.provider == "sentence-transformers":
                embeddings = await self._encode_with_sentence_transformers(texts, normalize)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

            logger.debug(f"Generated embeddings for {len(texts)} texts with shape: {embeddings.shape}")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            # If multi-API fails, try fallback to direct Gemini
            if self.provider == "multi":
                logger.warning("Multi-API failed, trying direct Gemini fallback...")
                try:
                    embeddings = await self._encode_with_gemini(texts)
                    logger.info("Direct Gemini fallback successful")
                    return embeddings
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
            raise
    
    async def _encode_with_gemini(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using Gemini with batch processing"""
        try:
            embeddings = []
            batch_size = 10  # Process in smaller batches for better performance

            # Process texts in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = []

                # Use batch embedding if available, otherwise process individually
                try:
                    # Try batch processing first
                    result = genai.embed_content(
                        model=settings.gemini_embedding_model,
                        content=batch,
                        task_type="retrieval_document"
                    )

                    if isinstance(result['embedding'][0], list):
                        # Multiple embeddings returned
                        for emb in result['embedding']:
                            batch_embeddings.append(np.array(emb, dtype=np.float32))
                    else:
                        # Single embedding returned
                        batch_embeddings.append(np.array(result['embedding'], dtype=np.float32))

                except Exception:
                    # Fallback to individual processing
                    for text in batch:
                        result = genai.embed_content(
                            model=settings.gemini_embedding_model,
                            content=text,
                            task_type="retrieval_document"
                        )
                        batch_embeddings.append(np.array(result['embedding'], dtype=np.float32))

                embeddings.extend(batch_embeddings)

            embeddings_array = np.vstack(embeddings)

            # Normalize for cosine similarity
            norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
            embeddings_array = embeddings_array / (norms + 1e-8)

            return embeddings_array
            
        except Exception as e:
            logger.error(f"Error with Gemini embeddings: {str(e)}")
            raise
    
    async def _encode_with_sentence_transformers(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """Generate embeddings using sentence-transformers"""
        try:
            embeddings = self.sentence_transformer_model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=normalize
            )
            
            return embeddings.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Error with sentence-transformers embeddings: {str(e)}")
            raise
    
    async def encode_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query (optimized for search)
        
        Args:
            query: Query text
            
        Returns:
            Query embedding
        """
        try:
            if self.provider == "gemini":
                # Use retrieval_query task type for queries
                result = genai.embed_content(
                    model=settings.gemini_embedding_model,
                    content=query,
                    task_type="retrieval_query"  # Optimized for query retrieval
                )
                
                embedding = np.array(result['embedding'], dtype=np.float32)
                
                # Normalize for cosine similarity
                norm = np.linalg.norm(embedding)
                embedding = embedding / (norm + 1e-8)
                
                return embedding.reshape(1, -1)  # Return as 2D array
            else:
                # Use regular encoding for sentence-transformers
                return await self.encode(query, normalize=True)
                
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise
    
    def get_dimension(self) -> int:
        """Get the embedding dimension"""
        return self.dimension
    
    def get_provider_info(self) -> dict:
        """Get information about the current provider"""
        return {
            "provider": self.provider,
            "dimension": self.dimension,
            "model": (
                settings.gemini_embedding_model if self.provider == "gemini" 
                else settings.embedding_model
            )
        }
