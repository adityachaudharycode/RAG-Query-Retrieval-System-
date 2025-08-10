"""
Local LLM service using Ollama for embeddings and text generation
"""
import json
import asyncio
import aiohttp
import numpy as np
from typing import List, Dict, Any, Optional
from loguru import logger
import os


class LocalLLMService:
    """Service for local LLM operations using Ollama"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.config = self._load_config()
        self.embedding_model = self.config.get("embedding_model", "nomic-embed-text")
        self.text_model = self.config.get("text_model", "llama3.2:3b")
        self.fallback_text_model = self.config.get("fallback_text_model", "llama3.2:1b")
        self.session = None
        self.available = False
    
    def _load_config(self) -> Dict[str, Any]:
        """Load local LLM configuration"""
        config_file = "local_llm_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load local LLM config: {e}")
        
        # Default configuration
        return {
            "ollama_base_url": "http://localhost:11434",
            "embedding_model": "nomic-embed-text",
            "text_model": "llama3.2:3b",
            "fallback_text_model": "llama3.2:1b"
        }
    
    async def initialize(self) -> bool:
        """Initialize the local LLM service"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Check if Ollama is running
            async with self.session.get(f"{self.base_url}/api/version", timeout=5) as response:
                if response.status == 200:
                    version_info = await response.json()
                    logger.info(f"Ollama service detected: {version_info}")
                    
                    # Check if models are available
                    if await self._check_models():
                        self.available = True
                        logger.info("Local LLM service initialized successfully")
                        return True
                    else:
                        logger.warning("Required models not available")
                        return False
                else:
                    logger.warning("Ollama service not responding")
                    return False
                    
        except Exception as e:
            logger.warning(f"Local LLM service not available: {e}")
            return False
    
    async def _check_models(self) -> bool:
        """Check if required models are available"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    available_models = [model["name"] for model in data.get("models", [])]
                    
                    embedding_available = any(self.embedding_model in model for model in available_models)
                    text_available = any(self.text_model in model for model in available_models)
                    
                    logger.info(f"Available models: {available_models}")
                    logger.info(f"Embedding model ({self.embedding_model}) available: {embedding_available}")
                    logger.info(f"Text model ({self.text_model}) available: {text_available}")
                    
                    return embedding_available and text_available
                    
        except Exception as e:
            logger.error(f"Error checking models: {e}")
            return False
    
    async def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using local model"""
        if not self.available:
            raise Exception("Local LLM service not available")
        
        embeddings = []
        
        for text in texts:
            try:
                async with self.session.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text
                    },
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        embedding = np.array(result["embedding"], dtype=np.float32)
                        embeddings.append(embedding)
                    else:
                        error_text = await response.text()
                        raise Exception(f"Embedding request failed: {error_text}")
                        
            except Exception as e:
                logger.error(f"Error generating embedding for text: {str(e)}")
                raise
        
        if not embeddings:
            raise Exception("No embeddings generated")
        
        embeddings_array = np.vstack(embeddings)
        
        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        embeddings_array = embeddings_array / (norms + 1e-8)
        
        logger.info(f"Generated {len(embeddings)} local embeddings")
        return embeddings_array
    
    async def generate_text(self, prompt: str, context: str = "", max_tokens: int = 1000) -> str:
        """Generate text using local model"""
        if not self.available:
            raise Exception("Local LLM service not available")
        
        # Construct the full prompt
        if context:
            full_prompt = f"""Context: {context}

Question: {prompt}

Please provide a clear and accurate answer based on the context provided. Be concise and specific.

Answer:"""
        else:
            full_prompt = prompt
        
        # Try primary model first
        models_to_try = [self.text_model, self.fallback_text_model]
        
        for model in models_to_try:
            try:
                logger.info(f"Generating text with local model: {model}")
                
                async with self.session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens,
                            "temperature": 0.1,
                            "top_p": 0.9,
                            "stop": ["Question:", "Context:"]
                        }
                    },
                    timeout=120  # 2 minute timeout for text generation
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        answer = result.get("response", "").strip()
                        
                        if answer:
                            logger.info(f"Generated text with {model}: {len(answer)} characters")
                            return self._post_process_answer(answer)
                        else:
                            logger.warning(f"Empty response from {model}")
                    else:
                        error_text = await response.text()
                        logger.warning(f"Text generation failed with {model}: {error_text}")
                        
            except Exception as e:
                logger.warning(f"Error with {model}: {str(e)}")
                continue
        
        raise Exception("All local text models failed")
    
    def _post_process_answer(self, answer: str) -> str:
        """Post-process the generated answer"""
        # Remove common artifacts
        answer = answer.replace("Answer:", "").strip()
        
        # Remove repetitive patterns
        lines = answer.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and line not in cleaned_lines[-3:]:  # Avoid recent repetitions
                cleaned_lines.append(line)
        
        answer = '\n'.join(cleaned_lines)
        
        # Limit length if too long
        if len(answer) > 2000:
            sentences = answer.split('. ')
            truncated = '. '.join(sentences[:5])  # Keep first 5 sentences
            if not truncated.endswith('.'):
                truncated += '.'
            answer = truncated
        
        return answer
    
    async def close(self):
        """Close the service"""
        if self.session:
            await self.session.close()
    
    def is_available(self) -> bool:
        """Check if local LLM service is available"""
        return self.available
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about loaded models"""
        return {
            "embedding_model": self.embedding_model,
            "text_model": self.text_model,
            "fallback_text_model": self.fallback_text_model,
            "base_url": self.base_url,
            "available": self.available
        }
