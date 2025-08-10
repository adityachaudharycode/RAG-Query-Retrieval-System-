"""
Query processing service for handling user queries and generating answers with multi-API fallback
"""
import re
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from loguru import logger

from config import settings
from services.vector_store import VectorStore
from services.multi_api_service import MultiAPIService
from models.schemas import SearchResult, AnswerWithExplanation


class QueryProcessor:
    """Service for processing queries and generating contextual answers"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.multi_api_service = MultiAPIService()  # Multi-API fallback system
        # Configure Gemini (fallback)
        genai.configure(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature
        
    async def process_query(self, query: str, document_text: str = None) -> str:
        """
        Process a single query and generate an answer
        
        Args:
            query: User question
            document_text: Full document text (optional, for fallback)
            
        Returns:
            Generated answer
        """
        try:
            logger.info(f"Processing query: '{query[:100]}...'")
            
            # Preprocess the query
            processed_query = self._preprocess_query(query)
            
            # Get relevant context from vector store (reduced chunks for speed)
            context = await self.vector_store.get_relevant_context(
                processed_query,
                max_chunks=2  # Reduced from 3 to 2 for faster processing
            )
            
            # If no relevant context found, use document text directly
            if not context and document_text:
                context = self._extract_relevant_sections(query, document_text)
            
            # Generate answer using LLM
            answer = await self._generate_answer(query, context)
            
            logger.info(f"Generated answer with {len(answer)} characters")
            return answer
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"I apologize, but I encountered an error while processing your query: {str(e)}"
    
    def _preprocess_query(self, query: str) -> str:
        """
        Preprocess the query to improve search results
        
        Args:
            query: Raw user query
            
        Returns:
            Processed query
        """
        # Remove question words that don't add semantic value
        query = re.sub(r'\b(what|how|when|where|why|does|is|are|can|will|would)\b', '', query, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Extract key terms for better matching
        key_terms = self._extract_key_terms(query)
        if key_terms:
            query = f"{query} {' '.join(key_terms)}"
        
        return query
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract important terms from the query"""
        # Simple keyword extraction - can be improved with NLP libraries
        important_terms = []
        
        # Insurance/legal specific terms
        insurance_terms = [
            'premium', 'policy', 'coverage', 'deductible', 'claim', 'benefit',
            'waiting period', 'grace period', 'exclusion', 'maternity',
            'pre-existing', 'surgery', 'hospital', 'treatment', 'discount'
        ]
        
        query_lower = query.lower()
        for term in insurance_terms:
            if term in query_lower:
                important_terms.append(term)
        
        return important_terms
    
    def _extract_relevant_sections(self, query: str, document_text: str, max_length: int = 2000) -> str:
        """
        Extract relevant sections from document text based on query
        
        Args:
            query: User query
            document_text: Full document text
            max_length: Maximum length of extracted context
            
        Returns:
            Relevant text sections
        """
        try:
            # Split document into paragraphs
            paragraphs = document_text.split('\n')
            
            # Score paragraphs based on query relevance
            scored_paragraphs = []
            query_terms = set(query.lower().split())
            
            for para in paragraphs:
                if len(para.strip()) < 20:  # Skip very short paragraphs
                    continue
                
                para_lower = para.lower()
                score = sum(1 for term in query_terms if term in para_lower)
                
                if score > 0:
                    scored_paragraphs.append((score, para))
            
            # Sort by score and take top paragraphs
            scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
            
            # Combine top paragraphs up to max_length
            context = ""
            for score, para in scored_paragraphs:
                if len(context) + len(para) <= max_length:
                    context += para + "\n\n"
                else:
                    break
            
            return context.strip()
            
        except Exception as e:
            logger.error(f"Error extracting relevant sections: {str(e)}")
            return document_text[:max_length] if document_text else ""
    
    async def _generate_answer(self, query: str, context: str) -> str:
        """
        Generate answer using multi-API service with automatic fallback

        Args:
            query: User question
            context: Relevant context from documents

        Returns:
            Generated answer
        """
        try:
            # Try multi-API service first
            try:
                answer = await self.multi_api_service.generate_text(query, context)
                # Post-process the answer
                answer = self._post_process_answer(answer)
                return answer
            except Exception as multi_api_error:
                logger.warning(f"Multi-API service failed: {multi_api_error}")

                # Fallback to direct Gemini
                logger.info("Falling back to direct Gemini API...")
                return await self._generate_answer_gemini_direct(query, context)

        except Exception as e:
            logger.error(f"All API methods failed: {str(e)}")
            return "I apologize, but I'm unable to generate an answer at this time due to API limitations. Please try again in a few minutes."

    async def _generate_answer_gemini_direct(self, query: str, context: str) -> str:
        """
        Generate answer using direct Gemini API (fallback method)
        """
        try:
            # Construct the prompt
            prompt = self._build_prompt(query, context)

            # Initialize Gemini model
            model = genai.GenerativeModel(
                model_name=self.model,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=0.9
                )
            )

            # Generate response
            response = model.generate_content(prompt)

            if response.text:
                answer = response.text.strip()
                # Post-process the answer
                answer = self._post_process_answer(answer)
                return answer
            else:
                logger.warning("Direct Gemini returned empty response")
                return "I apologize, but I couldn't generate a response for your query."

        except Exception as e:
            logger.error(f"Direct Gemini API also failed: {str(e)}")
            return "I apologize, but I'm unable to generate an answer at this time due to a technical issue."
    
    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build the prompt for the LLM

        Args:
            query: User question
            context: Relevant context

        Returns:
            Formatted prompt
        """
        prompt = f"""You are an expert assistant specializing in insurance, legal, HR, and compliance documents. Provide accurate, concise answers based on the given context.

Based on the following document context, please answer the question accurately and concisely.

Context:
{context}

Question: {query}

Instructions:
1. Answer based only on the information provided in the context
2. Be specific and cite relevant details from the context
3. If the exact information is not available, state that clearly
4. Keep the answer concise but complete
5. Use professional language appropriate for insurance/legal documents

Answer:"""

        return prompt
    
    def _post_process_answer(self, answer: str) -> str:
        """
        Post-process the generated answer
        
        Args:
            answer: Raw answer from LLM
            
        Returns:
            Cleaned and formatted answer
        """
        # Remove any unwanted prefixes
        answer = re.sub(r'^(Answer:|Response:)\s*', '', answer, flags=re.IGNORECASE)
        
        # Clean up formatting
        answer = re.sub(r'\n+', ' ', answer)
        answer = re.sub(r'\s+', ' ', answer)
        
        # Ensure proper sentence ending
        if answer and not answer.endswith(('.', '!', '?')):
            answer += '.'
        
        return answer.strip()
    
    async def process_query_with_explanation(self, query: str) -> AnswerWithExplanation:
        """
        Process query and return detailed answer with explanation
        
        Args:
            query: User question
            
        Returns:
            Detailed answer with confidence and reasoning
        """
        try:
            # Get search results
            search_results = await self.vector_store.search(query, top_k=5)
            
            # Generate answer
            context = await self.vector_store.get_relevant_context(query, max_chunks=3)
            answer = await self._generate_answer(query, context)
            
            # Calculate confidence based on search scores
            confidence = self._calculate_confidence(search_results)
            
            # Extract source information
            sources = [f"chunk_{result.chunk.id}" for result in search_results[:3]]
            
            # Generate reasoning
            reasoning = self._generate_reasoning(search_results, answer)
            
            return AnswerWithExplanation(
                answer=answer,
                confidence=confidence,
                sources=sources,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Error processing query with explanation: {str(e)}")
            return AnswerWithExplanation(
                answer="Error processing query",
                confidence=0.0,
                sources=[],
                reasoning=f"Error: {str(e)}"
            )
    
    def _calculate_confidence(self, search_results: List[SearchResult]) -> float:
        """Calculate confidence score based on search results"""
        if not search_results:
            return 0.0
        
        # Use the highest similarity score as base confidence
        max_score = max(result.score for result in search_results)
        
        # Normalize to 0-1 range (assuming cosine similarity)
        confidence = min(max_score, 1.0)
        
        return round(confidence, 3)
    
    def _generate_reasoning(self, search_results: List[SearchResult], answer: str) -> str:
        """Generate reasoning explanation"""
        if not search_results:
            return "No relevant context found in the document."
        
        reasoning = f"Based on analysis of {len(search_results)} relevant document sections "
        reasoning += f"with similarity scores ranging from {min(r.score for r in search_results):.3f} "
        reasoning += f"to {max(r.score for r in search_results):.3f}. "
        reasoning += "The answer was derived from the most relevant passages in the document."
        
        return reasoning
