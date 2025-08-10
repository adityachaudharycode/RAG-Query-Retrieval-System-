"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Any, Optional
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for query processing"""
    documents: str = Field(..., description="URL to the document (PDF/DOCX)")
    questions: List[str] = Field(..., description="List of questions to answer")
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": "https://example.com/document.pdf",
                "questions": [
                    "What is the grace period for premium payment?",
                    "What is the waiting period for pre-existing diseases?"
                ]
            }
        }


class QueryResponse(BaseModel):
    """Response model for query results"""
    answers: List[str] = Field(..., description="List of answers corresponding to the questions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answers": [
                    "The grace period for premium payment is 30 days.",
                    "The waiting period for pre-existing diseases is 36 months."
                ]
            }
        }


class DocumentChunk(BaseModel):
    """Model for document chunks"""
    id: str = Field(..., description="Unique identifier for the chunk")
    content: str = Field(..., description="Text content of the chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of the chunk")
    
    class Config:
        arbitrary_types_allowed = True


class SearchResult(BaseModel):
    """Model for search results"""
    chunk: DocumentChunk = Field(..., description="The matching document chunk")
    score: float = Field(..., description="Similarity score")
    rank: int = Field(..., description="Rank in search results")


class ProcessingStatus(BaseModel):
    """Model for processing status"""
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class AnswerWithExplanation(BaseModel):
    """Extended answer model with explanation"""
    answer: str = Field(..., description="The answer to the question")
    confidence: float = Field(..., description="Confidence score (0-1)")
    sources: List[str] = Field(..., description="Source chunks used for the answer")
    reasoning: str = Field(..., description="Explanation of the reasoning")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The grace period is 30 days.",
                "confidence": 0.95,
                "sources": ["chunk_1", "chunk_3"],
                "reasoning": "Based on section 4.2 of the policy document..."
            }
        }
