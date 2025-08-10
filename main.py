"""
Main FastAPI application for LLM-Powered Query-Retrieval System
"""
import os
import sys
import hashlib
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from loguru import logger

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from services.document_processor import DocumentProcessor
from services.vector_store import VectorStore
from services.query_processor import QueryProcessor
from models.schemas import QueryRequest, QueryResponse
from utils.logger import setup_logging

# Global services
document_processor = None
vector_store = None
query_processor = None

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    setup_logging()
    logger.info("Starting LLM-Powered Query-Retrieval System")

    global document_processor, vector_store, query_processor
    document_processor = DocumentProcessor()
    vector_store = VectorStore()
    query_processor = QueryProcessor(vector_store)

    await vector_store.initialize()
    logger.info("System initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down system")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="LLM-Powered Query-Retrieval System",
    description="Intelligent document processing and query answering system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify the bearer token"""
    if credentials.credentials != settings.api_bearer_token:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return credentials.credentials

# Startup is now handled by lifespan event

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "LLM-Powered Query-Retrieval System is running"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "document_processor": "ready",
            "vector_store": "ready",
            "query_processor": "ready"
        }
    }

# Add the webhook endpoint for submission
@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
async def webhook_endpoint(
    request: QueryRequest,
    _token: str = Depends(verify_token)
):
    """
    Webhook endpoint for submission (matches required format)
    """
    return await run_query_internal(request)

@app.post("/hackrx/run", response_model=QueryResponse)
async def run_query(
    request: QueryRequest,
    _token: str = Depends(verify_token)
):
    """
    Main endpoint for processing documents and answering queries (optimized)
    """
    return await run_query_internal(request)

async def run_query_internal(request: QueryRequest):
    """
    Internal function for processing documents and answering queries (optimized)
    """
    try:
        logger.info(f"Processing request with {len(request.questions)} questions")

        # Process the document
        document_text = await document_processor.process_document(request.documents)

        # Create document hash for caching
        document_hash = hashlib.md5(document_text.encode()).hexdigest()

        # Create embeddings and store in vector database with caching
        chunks = await document_processor.chunk_text(document_text)
        await vector_store.add_documents(chunks, document_hash)

        # Process queries in parallel for better performance
        async def process_single_query(question):
            return await query_processor.process_query(question, document_text)

        # Use asyncio.gather for concurrent processing
        logger.info("Processing queries concurrently...")
        answers = await asyncio.gather(*[
            process_single_query(question) for question in request.questions
        ])

        logger.info(f"Successfully processed {len(answers)} questions")
        return QueryResponse(answers=answers)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Use import string for reload support
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
