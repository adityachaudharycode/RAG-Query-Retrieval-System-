"""
Multi-API service with automatic fallback for handling rate limits
"""
import asyncio
import time
from typing import List, Dict, Any, Optional, Union
from loguru import logger
import google.generativeai as genai
import numpy as np

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available - install with: pip install openai")

try:
    import requests
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

from config import settings
from services.local_llm_service import LocalLLMService


class MultiAPIService:
    """Service that handles multiple API providers with automatic fallback"""
    
    def __init__(self):
        self.api_providers = []
        self.current_provider_index = 0
        self.rate_limit_cooldown = {}  # Track cooldown periods
        self.local_llm_service = LocalLLMService()  # Local LLM fallback
        self.local_llm_available = False
        self.setup_providers()
    
    async def initialize(self):
        """Initialize the multi-API service including local LLM"""
        # Try to initialize local LLM
        try:
            self.local_llm_available = await self.local_llm_service.initialize()
            if self.local_llm_available:
                logger.info("✅ Local LLM service available - will be used as primary fallback")
            else:
                logger.info("⚠️  Local LLM service not available - using API-only mode")
        except Exception as e:
            logger.warning(f"Local LLM initialization failed: {e}")
            self.local_llm_available = False

    def setup_providers(self):
        """Setup available API providers in priority order"""

        # Gemini providers (multiple keys)
        gemini_keys = [
            settings.gemini_api_key,
            settings.gemini_api_key_2,
            settings.gemini_api_key_3
        ]
        
        for i, key in enumerate(gemini_keys):
            if key and key != "your_gemini_api_key_here":
                self.api_providers.append({
                    "name": f"gemini_{i+1}",
                    "type": "gemini",
                    "api_key": key,
                    "model": settings.gemini_model,
                    "embedding_model": settings.gemini_embedding_model
                })
        
        # OpenAI provider
        if OPENAI_AVAILABLE and settings.openai_api_key:
            self.api_providers.append({
                "name": "openai",
                "type": "openai", 
                "api_key": settings.openai_api_key,
                "model": settings.openai_model,
                "embedding_model": "text-embedding-ada-002"
            })
        
        # Perplexity provider (Pro Sonar)
        if settings.perplexity_api_key:
            self.api_providers.append({
                "name": "perplexity",
                "type": "perplexity",
                "api_key": settings.perplexity_api_key,
                "model": settings.perplexity_model,
                "embedding_model": None  # Perplexity doesn't provide embeddings
            })

        # Hugging Face provider (free)
        if HUGGINGFACE_AVAILABLE and settings.huggingface_api_key:
            self.api_providers.append({
                "name": "huggingface",
                "type": "huggingface",
                "api_key": settings.huggingface_api_key,
                "model": "microsoft/DialoGPT-medium",
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            })
        
        logger.info(f"Initialized {len(self.api_providers)} API providers: {[p['name'] for p in self.api_providers]}")
    
    def is_provider_available(self, provider: Dict[str, Any]) -> bool:
        """Check if provider is available (not in cooldown)"""
        provider_name = provider["name"]
        if provider_name in self.rate_limit_cooldown:
            cooldown_until = self.rate_limit_cooldown[provider_name]
            if time.time() < cooldown_until:
                return False
            else:
                # Remove expired cooldown
                del self.rate_limit_cooldown[provider_name]
        return True
    
    def set_provider_cooldown(self, provider: Dict[str, Any], cooldown_minutes: int = 5):
        """Set cooldown period for rate-limited provider"""
        provider_name = provider["name"]
        cooldown_until = time.time() + (cooldown_minutes * 60)
        self.rate_limit_cooldown[provider_name] = cooldown_until
        logger.warning(f"Provider {provider_name} in cooldown for {cooldown_minutes} minutes")
    
    async def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings with automatic fallback (Local LLM first, then APIs)"""

        # Try local LLM first (free, no rate limits)
        if self.local_llm_available:
            try:
                logger.info("🏠 Trying local LLM for embeddings...")
                embeddings = await self.local_llm_service.generate_embeddings(texts)
                logger.info("✅ Local LLM embeddings successful")
                return embeddings
            except Exception as e:
                logger.warning(f"Local LLM embeddings failed: {e}")
                logger.info("🔄 Falling back to API providers...")

        # Fallback to API providers
        for attempt in range(len(self.api_providers)):
            provider = self.api_providers[self.current_provider_index]
            
            if not self.is_provider_available(provider):
                logger.info(f"Provider {provider['name']} in cooldown, trying next...")
                self.current_provider_index = (self.current_provider_index + 1) % len(self.api_providers)
                continue
            
            try:
                logger.info(f"Generating embeddings using {provider['name']}")
                
                if provider["type"] == "gemini":
                    return await self._generate_gemini_embeddings(texts, provider)
                elif provider["type"] == "openai":
                    return await self._generate_openai_embeddings(texts, provider)
                elif provider["type"] == "perplexity":
                    # Perplexity doesn't provide embeddings, skip to next provider
                    logger.info(f"Perplexity doesn't support embeddings, trying next provider...")
                    self.current_provider_index = (self.current_provider_index + 1) % len(self.api_providers)
                    continue
                elif provider["type"] == "huggingface":
                    return await self._generate_huggingface_embeddings(texts, provider)
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check for rate limit errors
                if any(term in error_msg for term in ["rate limit", "quota", "429", "too many requests"]):
                    logger.warning(f"Rate limit hit for {provider['name']}: {e}")
                    self.set_provider_cooldown(provider, cooldown_minutes=5)
                else:
                    logger.error(f"Error with {provider['name']}: {e}")
                
                # Try next provider
                self.current_provider_index = (self.current_provider_index + 1) % len(self.api_providers)
        
        raise Exception("All API providers failed or are rate limited")
    
    async def generate_text(self, prompt: str, context: str = "") -> str:
        """Generate text with automatic fallback (Local LLM first, then APIs)"""

        # Try local LLM first (free, no rate limits)
        if self.local_llm_available:
            try:
                logger.info("🏠 Trying local LLM for text generation...")
                answer = await self.local_llm_service.generate_text(prompt, context)
                logger.info("✅ Local LLM text generation successful")
                return answer
            except Exception as e:
                logger.warning(f"Local LLM text generation failed: {e}")
                logger.info("🔄 Falling back to API providers...")

        # Fallback to API providers
        for attempt in range(len(self.api_providers)):
            provider = self.api_providers[self.current_provider_index]
            
            if not self.is_provider_available(provider):
                logger.info(f"Provider {provider['name']} in cooldown, trying next...")
                self.current_provider_index = (self.current_provider_index + 1) % len(self.api_providers)
                continue
            
            try:
                logger.info(f"Generating text using {provider['name']}")
                
                if provider["type"] == "gemini":
                    return await self._generate_gemini_text(prompt, context, provider)
                elif provider["type"] == "openai":
                    return await self._generate_openai_text(prompt, context, provider)
                elif provider["type"] == "perplexity":
                    return await self._generate_perplexity_text(prompt, context, provider)
                elif provider["type"] == "huggingface":
                    return await self._generate_huggingface_text(prompt, context, provider)
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check for rate limit errors
                if any(term in error_msg for term in ["rate limit", "quota", "429", "too many requests"]):
                    logger.warning(f"Rate limit hit for {provider['name']}: {e}")
                    self.set_provider_cooldown(provider, cooldown_minutes=5)
                else:
                    logger.error(f"Error with {provider['name']}: {e}")
                
                # Try next provider
                self.current_provider_index = (self.current_provider_index + 1) % len(self.api_providers)
        
        raise Exception("All API providers failed or are rate limited")
    
    async def _generate_gemini_embeddings(self, texts: List[str], provider: Dict[str, Any]) -> np.ndarray:
        """Generate embeddings using Gemini API"""
        genai.configure(api_key=provider["api_key"])
        
        embeddings = []
        batch_size = 10
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = []
            
            for text in batch:
                result = genai.embed_content(
                    model=provider["embedding_model"],
                    content=text,
                    task_type="retrieval_document"
                )
                batch_embeddings.append(np.array(result['embedding'], dtype=np.float32))
            
            embeddings.extend(batch_embeddings)
            
            # Small delay to avoid rate limits
            if i + batch_size < len(texts):
                await asyncio.sleep(0.1)
        
        embeddings_array = np.vstack(embeddings)
        
        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        embeddings_array = embeddings_array / (norms + 1e-8)
        
        return embeddings_array
    
    async def _generate_gemini_text(self, prompt: str, context: str, provider: Dict[str, Any]) -> str:
        """Generate text using Gemini API"""
        genai.configure(api_key=provider["api_key"])
        
        model = genai.GenerativeModel(
            model_name=provider["model"],
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=settings.max_tokens,
                temperature=settings.temperature,
                top_p=0.9
            )
        )
        
        full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nAnswer:"
        response = model.generate_content(full_prompt)
        
        if response.text:
            return response.text.strip()
        else:
            raise Exception("Empty response from Gemini")
    
    async def _generate_openai_embeddings(self, texts: List[str], provider: Dict[str, Any]) -> np.ndarray:
        """Generate embeddings using OpenAI API"""
        if not OPENAI_AVAILABLE:
            raise Exception("OpenAI library not available")
        
        openai.api_key = provider["api_key"]
        
        embeddings = []
        batch_size = 100  # OpenAI allows larger batches
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            response = await openai.Embedding.acreate(
                model=provider["embedding_model"],
                input=batch
            )
            
            batch_embeddings = [np.array(item['embedding'], dtype=np.float32) for item in response['data']]
            embeddings.extend(batch_embeddings)
        
        embeddings_array = np.vstack(embeddings)
        
        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        embeddings_array = embeddings_array / (norms + 1e-8)
        
        return embeddings_array
    
    async def _generate_openai_text(self, prompt: str, context: str, provider: Dict[str, Any]) -> str:
        """Generate text using OpenAI API"""
        if not OPENAI_AVAILABLE:
            raise Exception("OpenAI library not available")
        
        openai.api_key = provider["api_key"]
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"}
        ]
        
        response = await openai.ChatCompletion.acreate(
            model=provider["model"],
            messages=messages,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature
        )
        
        return response.choices[0].message.content.strip()
    
    async def _generate_huggingface_embeddings(self, texts: List[str], provider: Dict[str, Any]) -> np.ndarray:
        """Generate embeddings using Hugging Face API"""
        # This would require implementing HF Inference API calls
        # For now, return a placeholder
        raise Exception("Hugging Face embeddings not implemented yet")
    
    async def _generate_perplexity_text(self, prompt: str, context: str, provider: Dict[str, Any]) -> str:
        """Generate text using Perplexity Pro Sonar API"""
        import requests
        import json

        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {provider['api_key']}"
        }

        # Construct messages for Perplexity
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions based on the provided context. Provide accurate, concise answers."
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nQuestion: {prompt}\n\nPlease provide a clear and accurate answer based on the context provided."
            }
        ]

        data = {
            "model": provider["model"],
            "messages": messages,
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature,
            "stream": False
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                answer = result["choices"][0]["message"]["content"].strip()
                return answer
            else:
                raise Exception("No response content from Perplexity")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Perplexity API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Perplexity response: {str(e)}")

    async def _generate_huggingface_text(self, prompt: str, context: str, provider: Dict[str, Any]) -> str:
        """Generate text using Hugging Face API"""
        # This would require implementing HF Inference API calls
        # For now, return a placeholder
        raise Exception("Hugging Face text generation not implemented yet")
    
    def get_current_provider_info(self) -> Dict[str, Any]:
        """Get information about current provider"""
        if self.api_providers:
            provider = self.api_providers[self.current_provider_index]
            return {
                "name": provider["name"],
                "type": provider["type"],
                "available_providers": len(self.api_providers),
                "cooldowns": list(self.rate_limit_cooldown.keys())
            }
        return {"name": "none", "type": "none", "available_providers": 0, "cooldowns": []}
