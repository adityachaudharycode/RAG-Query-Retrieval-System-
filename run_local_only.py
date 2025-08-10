"""
Local-only LLM FastAPI server using Ollama
No API calls, completely offline, free unlimited usage
Runs as server at /api/v1/hackrx/run endpoint
"""
import asyncio
import aiohttp
import numpy as np
import json
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
import os

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
    title="Local-Only LLM System",
    description="Document Q&A using local Ollama models - Zero API costs",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global LLM instance
local_llm = None


class LocalOnlyLLM:
    """Complete local LLM system using Ollama"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.embedding_model = "nomic-embed-text"
        self.text_model = "llama3.2:3b"
        self.fallback_text_model = "llama3.2:1b"
        self.session = None
        self.vector_store = {}  # Simple in-memory vector store
        self.document_chunks = []
        
    async def initialize(self):
        """Initialize the local LLM system"""
        print("🏠 Initializing Local-Only LLM System")
        print("=" * 50)
        
        self.session = aiohttp.ClientSession()
        
        # Check Ollama service
        try:
            async with self.session.get(f"{self.base_url}/api/version", timeout=5) as response:
                if response.status == 200:
                    version_info = await response.json()
                    print(f"✅ Ollama service running: {version_info.get('version', 'Unknown')}")
                else:
                    raise Exception("Ollama not responding")
        except Exception as e:
            print(f"❌ Ollama service not available: {e}")
            print("💡 Make sure Ollama is running: ollama serve")
            return False
        
        # Check models
        available_models = await self._check_models()
        if not available_models:
            return False
        
        print("✅ Local-only LLM system ready!")
        print(f"📊 Using models:")
        print(f"   • Embeddings: {self.embedding_model}")
        print(f"   • Text: {self.text_model}")
        print(f"   • Fallback: {self.fallback_text_model}")
        return True
    
    async def _check_models(self) -> bool:
        """Check if required models are available"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    available_models = [model["name"] for model in data.get("models", [])]
                    
                    embedding_available = any(self.embedding_model in model for model in available_models)
                    text_available = any(self.text_model in model for model in available_models)
                    fallback_available = any(self.fallback_text_model in model for model in available_models)
                    
                    print(f"📋 Available models: {len(available_models)}")
                    for model in available_models:
                        print(f"   • {model}")
                    
                    if not embedding_available:
                        print(f"❌ Embedding model '{self.embedding_model}' not found")
                        print(f"💡 Download with: ollama pull {self.embedding_model}")
                        return False
                    
                    if not text_available:
                        print(f"❌ Text model '{self.text_model}' not found")
                        print(f"💡 Download with: ollama pull {self.text_model}")
                        return False
                    
                    print("✅ All required models available")
                    return True
                    
        except Exception as e:
            print(f"❌ Error checking models: {e}")
            return False
    
    async def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using local Ollama"""
        print(f"🔍 Generating embeddings for {len(texts)} texts using {self.embedding_model}")
        
        embeddings = []
        start_time = time.time()
        
        for i, text in enumerate(texts):
            print(f"   Processing {i+1}/{len(texts)}...", end=" ")
            
            try:
                async with self.session.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text[:1000]  # Limit text length
                    },
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        embedding = np.array(result["embedding"], dtype=np.float32)
                        embeddings.append(embedding)
                        print("✅")
                    else:
                        error_text = await response.text()
                        print(f"❌ {error_text}")
                        raise Exception(f"Embedding failed: {error_text}")
                        
            except Exception as e:
                print(f"❌ Error: {e}")
                raise
        
        embeddings_array = np.vstack(embeddings)
        
        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        embeddings_array = embeddings_array / (norms + 1e-8)
        
        end_time = time.time()
        print(f"✅ Generated {len(embeddings)} embeddings in {end_time - start_time:.2f}s")
        print(f"📊 Embedding shape: {embeddings_array.shape}")
        
        return embeddings_array
    
    async def generate_text(self, prompt: str, context: str = "") -> str:
        """Generate text using local Ollama"""
        print(f"💬 Generating text using {self.text_model}")
        print(f"❓ Query: {prompt[:100]}...")
        
        # Construct optimized prompt
        if context:
            full_prompt = f"""You are a helpful assistant that answers questions based on provided context.

Context:
{context[:2000]}

Question: {prompt}

Instructions:
- Answer based only on the provided context
- Be accurate and specific
- If the context doesn't contain the answer, say so
- Keep the answer concise but complete

Answer:"""
        else:
            full_prompt = f"Question: {prompt}\n\nAnswer:"
        
        # Try primary model first, then fallback
        models_to_try = [self.text_model, self.fallback_text_model]
        
        for model in models_to_try:
            try:
                print(f"🤖 Trying model: {model}")
                start_time = time.time()
                
                async with self.session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "num_predict": 500,  # Max tokens
                            "temperature": 0.1,  # Low temperature for accuracy
                            "top_p": 0.9,
                            "stop": ["Question:", "Context:", "\n\nQuestion:", "\n\nContext:"]
                        }
                    },
                    timeout=120
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        answer = result.get("response", "").strip()
                        
                        if answer:
                            end_time = time.time()
                            print(f"✅ Generated response in {end_time - start_time:.2f}s")
                            print(f"📝 Answer length: {len(answer)} characters")
                            
                            # Clean up the answer
                            answer = self._clean_answer(answer)
                            return answer
                        else:
                            print(f"⚠️  Empty response from {model}")
                    else:
                        error_text = await response.text()
                        print(f"❌ {model} failed: {error_text}")
                        
            except Exception as e:
                print(f"❌ Error with {model}: {e}")
                continue
        
        raise Exception("All local text models failed")
    
    def _clean_answer(self, answer: str) -> str:
        """Clean and format the generated answer"""
        # Remove common artifacts
        answer = answer.replace("Answer:", "").strip()
        
        # Remove repetitive patterns
        lines = answer.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and line not in cleaned_lines[-2:]:  # Avoid recent repetitions
                cleaned_lines.append(line)
        
        answer = '\n'.join(cleaned_lines)
        
        # Limit length
        if len(answer) > 1000:
            sentences = answer.split('. ')
            answer = '. '.join(sentences[:4])  # Keep first 4 sentences
            if not answer.endswith('.'):
                answer += '.'
        
        return answer
    
    async def process_document(self, document_url: str) -> str:
        """Process document from URL"""
        print(f"📄 Processing document: {document_url[:60]}...")
        
        try:
            # Download document
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(document_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Determine file type
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' in content_type or document_url.lower().endswith('.pdf'):
                text = self._extract_pdf_text(response.content)
            elif 'word' in content_type or document_url.lower().endswith(('.docx', '.doc')):
                text = self._extract_docx_text(response.content)
            else:
                # Try PDF first, then DOCX
                try:
                    text = self._extract_pdf_text(response.content)
                except:
                    text = self._extract_docx_text(response.content)
            
            print(f"✅ Extracted {len(text)} characters from document")
            return text
            
        except Exception as e:
            print(f"❌ Document processing failed: {e}")
            raise
    
    def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF content"""
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
    
    def _extract_docx_text(self, content: bytes) -> str:
        """Extract text from DOCX content"""
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
    
    def create_chunks(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[Dict[str, Any]]:
        """Create text chunks for processing"""
        print(f"✂️  Creating chunks (size: {chunk_size}, overlap: {overlap})")
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                'content': chunk_text,
                'index': len(chunks),
                'start_word': i,
                'end_word': i + len(chunk_words)
            })
        
        print(f"✅ Created {len(chunks)} chunks")
        return chunks
    
    async def build_vector_store(self, chunks: List[Dict[str, Any]]):
        """Build vector store from chunks"""
        print("🗄️  Building vector store...")
        
        texts = [chunk['content'] for chunk in chunks]
        embeddings = await self.generate_embeddings(texts)
        
        # Store chunks with embeddings
        self.document_chunks = chunks
        for i, chunk in enumerate(chunks):
            chunk['embedding'] = embeddings[i]
        
        print(f"✅ Vector store built with {len(chunks)} chunks")
    
    def search_similar_chunks(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        if not self.document_chunks:
            return []
        
        # Calculate similarities
        similarities = []
        for chunk in self.document_chunks:
            similarity = np.dot(query_embedding, chunk['embedding'])
            similarities.append((similarity, chunk))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [chunk for _, chunk in similarities[:top_k]]
        
        print(f"🔍 Found {len(top_chunks)} similar chunks")
        for i, chunk in enumerate(top_chunks):
            print(f"   {i+1}. Similarity: {similarities[i][0]:.3f} | Content: {chunk['content'][:100]}...")
        
        return top_chunks
    
    async def answer_question(self, question: str) -> str:
        """Answer question using local LLM and vector store"""
        print(f"\n❓ Processing question: {question}")
        
        # Generate query embedding
        query_embeddings = await self.generate_embeddings([question])
        query_embedding = query_embeddings[0]
        
        # Find relevant chunks
        relevant_chunks = self.search_similar_chunks(query_embedding, top_k=5)
        
        # Combine context
        context = "\n\n".join([chunk['content'] for chunk in relevant_chunks])
        
        # Generate answer
        answer = await self.generate_text(question, context)
        
        return answer
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()


# FastAPI endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize the local LLM system on startup"""
    global local_llm
    print("🏠 Starting Local-Only LLM Server")
    print("=" * 50)

    local_llm = LocalOnlyLLM()

    if await local_llm.initialize():
        print("✅ Local LLM server ready!")
        print("🌐 Server running at: http://localhost:8000")
        print("📖 API docs at: http://localhost:8000/docs")
        print("🎯 Test endpoint: POST /api/v1/hackrx/run")
    else:
        print("❌ Failed to initialize local LLM system")
        print("💡 Make sure Ollama is running: ollama serve")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    global local_llm
    if local_llm:
        await local_llm.close()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    global local_llm

    if not local_llm:
        raise HTTPException(status_code=503, detail="Local LLM not initialized")

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        local_llm_available=True,
        models={
            "embedding": local_llm.embedding_model,
            "text": local_llm.text_model,
            "fallback": local_llm.fallback_text_model
        }
    )


@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Main endpoint for processing documents and answering queries using local LLM
    """
    global local_llm

    if not local_llm:
        raise HTTPException(status_code=503, detail="Local LLM not initialized")

    try:
        print(f"\n🔄 Processing request with {len(request.questions)} questions")
        print(f"📄 Document: {request.documents[:60]}...")

        start_time = time.time()

        # Process document
        print("📄 Processing document...")
        document_text = await local_llm.process_document(request.documents)

        # Create chunks and build vector store
        print("✂️  Creating chunks and building vector store...")
        chunks = local_llm.create_chunks(document_text)
        await local_llm.build_vector_store(chunks)

        # Process all questions
        print(f"❓ Processing {len(request.questions)} questions...")
        answers = []

        for i, question in enumerate(request.questions, 1):
            print(f"   Question {i}/{len(request.questions)}: {question[:50]}...")
            answer = await local_llm.answer_question(question)
            answers.append(answer)
            print(f"   ✅ Answer {i} generated")

        end_time = time.time()
        total_time = end_time - start_time

        print(f"✅ Request completed successfully!")
        print(f"⏱️  Total time: {total_time:.2f} seconds")
        print(f"⚡ Average per question: {total_time/len(request.questions):.2f} seconds")
        print(f"💰 Cost: $0.00 (completely free!)")

        return QueryResponse(answers=answers)

    except Exception as e:
        print(f"❌ Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with system info"""
    return {
        "message": "🏠 Local-Only LLM System",
        "description": "Document Q&A using local Ollama models - Zero API costs",
        "endpoints": {
            "health": "/health",
            "main": "/api/v1/hackrx/run",
            "docs": "/docs"
        },
        "features": [
            "✅ Zero API costs",
            "✅ No rate limits",
            "✅ Complete privacy",
            "✅ Works offline"
        ]
    }


def main():
    """Run the FastAPI server"""
    print("🚀 Starting Local-Only LLM FastAPI Server")
    print("=" * 50)
    print("🏠 Local LLM with Ollama")
    print("🌐 Server: http://localhost:8000")
    print("� API Docs: http://localhost:8000/docs")
    print("🎯 Endpoint: POST /api/v1/hackrx/run")
    print("=" * 50)

    uvicorn.run(
        "run_local_only:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
