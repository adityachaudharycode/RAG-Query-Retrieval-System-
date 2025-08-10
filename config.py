"""
Configuration settings for the LLM-Powered Query-Retrieval System
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_bearer_token: str = Field(env="API_BEARER_TOKEN")
    
    # Multi-API Configuration (Fallback System)
    gemini_api_key: str = Field(env="GEMINI_API_KEY")
    gemini_api_key_2: Optional[str] = Field(default=None, env="GEMINI_API_KEY_2")
    gemini_api_key_3: Optional[str] = Field(default=None, env="GEMINI_API_KEY_3")

    # OpenAI Configuration (Fallback)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")

    # Hugging Face Configuration (Free Fallback)
    huggingface_api_key: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")

    # Perplexity Configuration (Pro Sonar)
    perplexity_api_key: Optional[str] = Field(default=None, env="PERPLEXITY_API_KEY")
    perplexity_model: str = Field(default="sonar-large-chat", env="PERPLEXITY_MODEL")

    # Primary Configuration
    gemini_model: str = Field(default="gemini-1.5-flash", env="GEMINI_MODEL")
    embedding_provider: str = Field(default="multi", env="EMBEDDING_PROVIDER")  # "multi", "gemini", "openai", "huggingface"
    max_tokens: int = Field(default=4000, env="MAX_TOKENS")
    temperature: float = Field(default=0.1, env="TEMPERATURE")
    
    # Vector Database Configuration
    vector_dimension: int = Field(default=768, env="VECTOR_DIMENSION")  # Gemini embeddings are 768-dimensional
    faiss_index_path: str = Field(default="./data/faiss_index", env="FAISS_INDEX_PATH")
    chunk_size: int = Field(default=1024, env="CHUNK_SIZE")  # Larger chunks for faster processing
    chunk_overlap: int = Field(default=100, env="CHUNK_OVERLAP")  # Increased overlap for better context

    # Model Configuration
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")  # Fallback for sentence-transformers
    gemini_embedding_model: str = Field(default="models/embedding-001", env="GEMINI_EMBEDDING_MODEL")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", env="LOG_FILE")
    
    # Cache Configuration
    enable_cache: bool = Field(default=True, env="ENABLE_CACHE")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Create necessary directories
os.makedirs(os.path.dirname(settings.faiss_index_path), exist_ok=True)
os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
os.makedirs("./temp", exist_ok=True)
