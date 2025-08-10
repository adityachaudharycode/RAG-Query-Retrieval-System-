"""
OPTIMIZED Local-only LLM FastAPI server - FAST & ACCURATE
Target: 30-60 seconds total, accurate answers from documents only
"""
import asyncio
import aiohttp
import numpy as np
import json
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import tempfile
import os
import re

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Document processing imports
import fitz  # PyMuPDF
from docx import Document
import requests
from urllib.parse import urlparse


# Pydantic models for API
class QueryRequest(BaseModel):
    documents: str
    questions: List[str]


class QueryResponse(BaseModel):
    answers: List[str]


class HealthResponse(BaseModel):
    status: str
    version: str
    local_llm_available: bool
    models: Dict[str, str]


# FastAPI app
app = FastAPI(
    title="FAST Local-Only LLM System",
    description="Optimized Document Q&A using local Ollama models - 30-60s target",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global LLM instance
local_llm = None


class FastLocalLLM:
    """OPTIMIZED Local LLM system - Fast & Accurate"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.embedding_model = "nomic-embed-text"
        self.text_model = "llama3.2:3b"
        self.fallback_text_model = "llama3.2:1b"
        self.session = None
        self.document_cache = {}  # Cache processed documents
        
    async def initialize(self):
        """Initialize the optimized local LLM system"""
        print("⚡ Initializing FAST Local-Only LLM System")
        print("🎯 Target: 30-60 seconds, accurate answers only")
        print("=" * 50)
        
        self.session = aiohttp.ClientSession()
        
        # Check Ollama service
        try:
            async with self.session.get(f"{self.base_url}/api/version", timeout=5) as response:
                if response.status == 200:
                    version_info = await response.json()
                    print(f"✅ Ollama service: {version_info.get('version', 'Unknown')}")
                    return await self._check_models()
                else:
                    raise Exception("Ollama not responding")
        except Exception as e:
            print(f"❌ Ollama service not available: {e}")
            return False
    
    async def _check_models(self) -> bool:
        """Quick model check"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    available_models = [model["name"] for model in data.get("models", [])]
                    
                    embedding_ok = any(self.embedding_model in model for model in available_models)
                    text_ok = any(self.text_model in model for model in available_models)
                    
                    if embedding_ok and text_ok:
                        print(f"✅ Models ready: {self.embedding_model}, {self.text_model}")
                        return True
                    else:
                        print(f"❌ Missing models. Available: {available_models}")
                        return False
        except Exception as e:
            print(f"❌ Model check failed: {e}")
            return False
    
    async def process_document_fast(self, document_url: str) -> str:
        """FAST document processing with caching"""
        doc_hash = hashlib.md5(document_url.encode()).hexdigest()
        
        if doc_hash in self.document_cache:
            print(f"⚡ Using cached document ({len(self.document_cache[doc_hash])} chars)")
            return self.document_cache[doc_hash]
        
        print(f"📄 Processing document: {document_url[:60]}...")
        
        try:
            # Download with timeout
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(document_url, headers=headers, timeout=20)
            response.raise_for_status()
            
            # Quick file type detection
            if 'pdf' in response.headers.get('content-type', '').lower() or document_url.lower().endswith('.pdf'):
                text = self._extract_pdf_fast(response.content)
            else:
                text = self._extract_docx_fast(response.content)
            
            # Cache the result
            self.document_cache[doc_hash] = text
            print(f"✅ Extracted {len(text)} characters")
            return text
            
        except Exception as e:
            print(f"❌ Document processing failed: {e}")
            raise
    
    def _extract_pdf_fast(self, content: bytes) -> str:
        """Fast PDF extraction"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            doc = fitz.open(temp_file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        finally:
            os.unlink(temp_file_path)
    
    def _extract_docx_fast(self, content: bytes) -> str:
        """Fast DOCX extraction"""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            doc = Document(temp_file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        finally:
            os.unlink(temp_file_path)
    
    def create_smart_chunks(self, text: str) -> List[Dict[str, Any]]:
        """SMART chunking - larger, context-aware chunks"""
        print("✂️  Creating smart chunks...")
        
        # Clean text first
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Larger chunks for better context
        chunk_size = 2000  # Doubled from 1000
        overlap = 200      # Increased overlap
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                'content': chunk_text,
                'index': len(chunks),
                'word_count': len(chunk_words)
            })
        
        print(f"✅ Created {len(chunks)} smart chunks (avg {chunk_size} words)")
        return chunks
    
    async def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """BATCH embedding generation - much faster"""
        print(f"⚡ Batch generating embeddings for {len(texts)} chunks...")
        
        start_time = time.time()
        embeddings = []
        
        # Process in batches of 5 for speed
        batch_size = 5
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = []
            
            # Process batch concurrently
            tasks = []
            for text in batch:
                task = self._generate_single_embedding(text[:800])  # Limit text length
                tasks.append(task)
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"⚠️  Embedding failed: {result}")
                    # Use zero vector as fallback
                    batch_embeddings.append(np.zeros(768, dtype=np.float32))
                else:
                    batch_embeddings.append(result)
            
            embeddings.extend(batch_embeddings)
            print(f"   Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
        
        embeddings_array = np.vstack(embeddings)
        
        # Normalize
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        embeddings_array = embeddings_array / (norms + 1e-8)
        
        end_time = time.time()
        print(f"✅ Generated embeddings in {end_time - start_time:.1f}s")
        
        return embeddings_array
    
    async def _generate_single_embedding(self, text: str) -> np.ndarray:
        """Generate single embedding"""
        async with self.session.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.embedding_model, "prompt": text},
            timeout=15
        ) as response:
            if response.status == 200:
                result = await response.json()
                return np.array(result["embedding"], dtype=np.float32)
            else:
                raise Exception(f"Embedding failed: {response.status}")
    
    def find_best_chunks(self, query_embedding: np.ndarray, chunk_embeddings: np.ndarray, chunks: List[Dict], top_k: int = 3) -> List[Dict]:
        """Find most relevant chunks"""
        similarities = np.dot(chunk_embeddings, query_embedding)
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        best_chunks = []
        for idx in top_indices:
            chunk = chunks[idx].copy()
            chunk['similarity'] = float(similarities[idx])
            best_chunks.append(chunk)
        
        similarities = [f"{c['similarity']:.3f}" for c in best_chunks]
        print(f"🔍 Found {len(best_chunks)} relevant chunks (similarity: {similarities})")

        return best_chunks
    
    async def generate_accurate_answer(self, question: str, context_chunks: List[Dict]) -> str:
        """Generate ACCURATE answer from document context only"""
        
        # Combine context from best chunks
        context = "\n\n".join([chunk['content'] for chunk in context_chunks])
        
        # OPTIMIZED prompt for accuracy
        prompt = f"""You are a document analysis assistant. Answer the question using ONLY the information provided in the context below. 

IMPORTANT RULES:
1. Use ONLY information from the provided context
2. If the answer is not in the context, say "The information is not mentioned in the document"
3. Be specific and quote relevant parts when possible
4. Do not add information from outside the context
5. Keep answers concise but complete

CONTEXT:
{context[:3000]}

QUESTION: {question}

ANSWER (based only on the context above):"""

        print(f"💬 Generating answer with {self.text_model}...")
        
        try:
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.text_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 300,  # Shorter answers
                        "temperature": 0.0,  # Most deterministic
                        "top_p": 0.8,
                        "stop": ["QUESTION:", "CONTEXT:", "\n\nQUESTION:", "\n\nCONTEXT:"]
                    }
                },
                timeout=30  # Shorter timeout
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    answer = result.get("response", "").strip()
                    
                    end_time = time.time()
                    print(f"✅ Answer generated in {end_time - start_time:.1f}s")
                    
                    return self._clean_answer(answer)
                else:
                    print(f"❌ Text generation failed: {response.status}")
                    return "I apologize, but I couldn't generate an answer due to a technical issue."
                    
        except Exception as e:
            print(f"❌ Answer generation error: {e}")
            return "I apologize, but I couldn't generate an answer due to a technical issue."
    
    def _clean_answer(self, answer: str) -> str:
        """Clean the generated answer"""
        # Remove artifacts
        answer = re.sub(r'^(Answer|ANSWER):\s*', '', answer, flags=re.IGNORECASE)
        answer = answer.strip()
        
        # Limit length
        if len(answer) > 800:
            sentences = answer.split('. ')
            answer = '. '.join(sentences[:3])
            if not answer.endswith('.'):
                answer += '.'
        
        return answer
    
    async def process_questions_fast(self, document_text: str, questions: List[str]) -> List[str]:
        """FAST question processing pipeline"""
        print(f"⚡ FAST processing pipeline for {len(questions)} questions")
        
        # Step 1: Smart chunking
        chunks = self.create_smart_chunks(document_text)
        
        # Step 2: Batch embedding generation
        chunk_texts = [chunk['content'] for chunk in chunks]
        chunk_embeddings = await self.generate_embeddings_batch(chunk_texts)
        
        # Step 3: Process all questions
        answers = []
        for i, question in enumerate(questions, 1):
            print(f"\n❓ Question {i}/{len(questions)}: {question[:50]}...")
            
            # Generate question embedding
            question_embedding = await self._generate_single_embedding(question)
            
            # Find best chunks
            best_chunks = self.find_best_chunks(question_embedding, chunk_embeddings, chunks, top_k=2)
            
            # Generate answer
            answer = await self.generate_accurate_answer(question, best_chunks)
            answers.append(answer)
            
            print(f"✅ Answer {i}: {answer[:100]}...")
        
        return answers
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()


# FastAPI endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize the fast local LLM system"""
    global local_llm
    print("⚡ Starting FAST Local-Only LLM Server")
    print("🎯 Target: 30-60 seconds, accurate answers")
    print("=" * 50)
    
    local_llm = FastLocalLLM()
    
    if await local_llm.initialize():
        print("✅ FAST Local LLM server ready!")
        print("🌐 Server: http://localhost:8000")
        print("🎯 Endpoint: POST /api/v1/hackrx/run")
    else:
        print("❌ Failed to initialize. Check Ollama: ollama serve")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up"""
    global local_llm
    if local_llm:
        await local_llm.close()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check"""
    global local_llm
    
    if not local_llm:
        raise HTTPException(status_code=503, detail="Local LLM not initialized")
    
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        local_llm_available=True,
        models={
            "embedding": local_llm.embedding_model,
            "text": local_llm.text_model,
            "fallback": local_llm.fallback_text_model
        }
    )


@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
async def process_query_fast(request: QueryRequest):
    """FAST & ACCURATE endpoint - 30-60 second target"""
    global local_llm
    
    if not local_llm:
        raise HTTPException(status_code=503, detail="Local LLM not initialized")
    
    try:
        print(f"\n⚡ FAST processing: {len(request.questions)} questions")
        print(f"📄 Document: {request.documents[:60]}...")
        
        total_start = time.time()
        
        # Process document
        document_text = await local_llm.process_document_fast(request.documents)
        
        # Process all questions with optimized pipeline
        answers = await local_llm.process_questions_fast(document_text, request.questions)
        
        total_end = time.time()
        total_time = total_end - total_start
        
        print(f"\n🎉 COMPLETED SUCCESSFULLY!")
        print(f"⚡ Total time: {total_time:.1f} seconds")
        print(f"🎯 Target met: {'✅ YES' if total_time <= 60 else '❌ NO'}")
        print(f"💰 Cost: $0.00")
        
        return QueryResponse(answers=answers)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "⚡ FAST Local-Only LLM System",
        "description": "Optimized for 30-60s response time with accurate answers",
        "version": "2.0.0",
        "target_time": "30-60 seconds",
        "features": [
            "⚡ Batch embedding processing",
            "🎯 Smart chunking strategy", 
            "📄 Document caching",
            "💰 Zero API costs",
            "🔒 Complete privacy"
        ]
    }


def main():
    """Run the FAST server"""
    print("⚡ FAST Local-Only LLM Server")
    print("🎯 Target: 30-60 seconds, accurate answers")
    print("🌐 http://localhost:8000")
    print("=" * 50)
    
    uvicorn.run(
        "run_local_fast:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
