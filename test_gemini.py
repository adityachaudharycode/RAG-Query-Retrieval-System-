"""
Test script for Gemini AI (embeddings and text generation)
"""
import os
import sys
import asyncio
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from services.embedding_service import EmbeddingService
from config import settings


async def test_gemini_ai():
    """Test Gemini AI functionality (embeddings and text generation)"""
    print("🧪 Testing Gemini AI")
    print("=" * 50)
    
    # Check API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        print("❌ Gemini API key not set!")
        print("Please set GEMINI_API_KEY in your .env file")
        print("See get_api_keys.md for instructions")
        return False
    
    print("✅ Gemini API key found")
    
    try:
        # Initialize embedding service
        print("\n🔧 Initializing Gemini embedding service...")
        embedding_service = EmbeddingService()
        await embedding_service.initialize()
        
        provider_info = embedding_service.get_provider_info()
        print(f"✅ Initialized: {provider_info}")
        
        # Test document embedding
        print("\n📄 Testing document embedding...")
        test_documents = [
            "This is a test document about insurance policies.",
            "The grace period for premium payment is 30 days.",
            "Pre-existing diseases have a waiting period of 36 months."
        ]
        
        doc_embeddings = await embedding_service.encode(test_documents)
        print(f"✅ Generated embeddings for {len(test_documents)} documents")
        print(f"   Shape: {doc_embeddings.shape}")
        print(f"   Dimension: {doc_embeddings.shape[1]}")
        
        # Test query embedding
        print("\n🔍 Testing query embedding...")
        test_query = "What is the grace period for premium payment?"
        
        query_embedding = await embedding_service.encode_query(test_query)
        print(f"✅ Generated query embedding")
        print(f"   Shape: {query_embedding.shape}")
        
        # Test similarity calculation
        print("\n📊 Testing similarity calculation...")
        import numpy as np
        
        # Calculate cosine similarity between query and documents
        similarities = np.dot(query_embedding, doc_embeddings.T).flatten()
        
        print("Similarity scores:")
        for i, (doc, score) in enumerate(zip(test_documents, similarities)):
            print(f"   Doc {i+1}: {score:.4f} - {doc[:50]}...")
        
        # Find best match
        best_match_idx = np.argmax(similarities)
        best_score = similarities[best_match_idx]
        
        print(f"\n🎯 Best match (score: {best_score:.4f}):")
        print(f"   {test_documents[best_match_idx]}")

        # Test text generation
        print("\n🤖 Testing Gemini text generation...")
        import google.generativeai as genai

        model = genai.GenerativeModel('gemini-1.5-flash')
        test_prompt = f"Based on this context: '{test_documents[best_match_idx]}', answer this question: '{test_query}'"

        response = model.generate_content(test_prompt)
        if response.text:
            print(f"✅ Generated response: {response.text[:100]}...")
        else:
            print("⚠️ No response generated")

        print("\n✅ All Gemini AI tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Gemini AI test failed: {str(e)}")
        print("\nPossible issues:")
        print("1. Invalid API key")
        print("2. Network connectivity issues")
        print("3. Gemini API quota exceeded")
        print("4. Missing dependencies")
        return False


async def test_fallback_embeddings():
    """Test sentence-transformers as fallback"""
    print("\n🔄 Testing Sentence-Transformers Fallback")
    print("=" * 50)
    
    try:
        # Temporarily switch to sentence-transformers
        original_provider = settings.embedding_provider
        settings.embedding_provider = "sentence-transformers"
        
        embedding_service = EmbeddingService()
        await embedding_service.initialize()
        
        provider_info = embedding_service.get_provider_info()
        print(f"✅ Fallback initialized: {provider_info}")
        
        # Test with same documents
        test_text = "This is a test document for sentence-transformers."
        embeddings = await embedding_service.encode([test_text])
        
        print(f"✅ Generated fallback embeddings")
        print(f"   Shape: {embeddings.shape}")
        print(f"   Dimension: {embeddings.shape[1]}")
        
        # Restore original provider
        settings.embedding_provider = original_provider
        
        print("✅ Sentence-transformers fallback works!")
        return True
        
    except Exception as e:
        print(f"❌ Fallback test failed: {str(e)}")
        return False


def main():
    """Main test function"""
    print("🚀 Gemini AI Test Suite")
    print("=" * 60)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv not installed, using system environment")
    
    async def run_tests():
        results = []
        
        # Test Gemini AI
        gemini_success = await test_gemini_ai()
        results.append(("Gemini AI (Embeddings + Text Generation)", gemini_success))
        
        # Test fallback
        fallback_success = await test_fallback_embeddings()
        results.append(("Sentence-Transformers Fallback", fallback_success))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        for test_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name}: {status}")
            if success:
                passed += 1
        
        print(f"\nOverall: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("\n🎉 All Gemini AI tests passed!")
            print("Your system is ready to use Gemini for both embeddings and text generation!")
        else:
            print("\n⚠️ Some tests failed.")
            print("Check your API key and network connection.")
            print("The system can still work with sentence-transformers fallback for embeddings.")
        
        return passed == len(results)
    
    try:
        success = asyncio.run(run_tests())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
