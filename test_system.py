"""
Comprehensive system test for the LLM-Powered Query-Retrieval System
"""
import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from services.document_processor import DocumentProcessor
from services.vector_store import VectorStore
from services.query_processor import QueryProcessor
from config import settings


async def test_document_processing():
    """Test document processing functionality"""
    print("🔍 Testing Document Processing...")
    
    processor = DocumentProcessor()
    
    # Test with the sample document URL
    test_url = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
    
    try:
        # Process document
        text = await processor.process_document(test_url)
        print(f"   ✅ Document processed: {len(text)} characters extracted")
        
        # Test chunking
        chunks = await processor.chunk_text(text)
        print(f"   ✅ Text chunked: {len(chunks)} chunks created")
        
        return text, chunks
        
    except Exception as e:
        print(f"   ❌ Document processing failed: {e}")
        return None, None


async def test_vector_store(chunks):
    """Test vector store functionality"""
    print("🔍 Testing Vector Store...")
    
    if not chunks:
        print("   ⚠️ No chunks to test with")
        return None
    
    try:
        vector_store = VectorStore()
        await vector_store.initialize()
        print("   ✅ Vector store initialized")
        
        # Add documents
        await vector_store.add_documents(chunks)
        print(f"   ✅ Added {len(chunks)} chunks to vector store")
        
        # Test search
        test_query = "grace period premium payment"
        results = await vector_store.search(test_query, top_k=3)
        print(f"   ✅ Search completed: {len(results)} results found")
        
        if results:
            print(f"   📊 Top result score: {results[0].score:.3f}")
        
        return vector_store
        
    except Exception as e:
        print(f"   ❌ Vector store test failed: {e}")
        return None


async def test_query_processing(vector_store, document_text):
    """Test query processing functionality"""
    print("🔍 Testing Query Processing...")
    
    if not vector_store:
        print("   ⚠️ No vector store to test with")
        return False
    
    try:
        query_processor = QueryProcessor(vector_store)
        
        # Test queries
        test_queries = [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?",
            "Does this policy cover maternity expenses?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"   🤔 Query {i}: {query}")
            answer = await query_processor.process_query(query, document_text)
            print(f"   💡 Answer {i}: {answer[:100]}...")
            print()
        
        print("   ✅ Query processing completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Query processing test failed: {e}")
        return False


async def test_full_system():
    """Test the complete system end-to-end"""
    print("=" * 60)
    print("🧪 COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    
    # Check environment
    print("🔧 Checking Environment...")
    
    # Check Gemini API key
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        print("   ⚠️ Gemini API key not set - system may fail")
    else:
        print("   ✅ Gemini API key configured")
    
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    print("   ✅ Directories created")
    
    print()
    
    # Test each component
    text, chunks = await test_document_processing()
    print()
    
    vector_store = await test_vector_store(chunks)
    print()
    
    query_success = await test_query_processing(vector_store, text)
    print()
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    tests = [
        ("Document Processing", text is not None and chunks is not None),
        ("Vector Store", vector_store is not None),
        ("Query Processing", query_success)
    ]
    
    passed = 0
    for test_name, success in tests:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! System is ready to use.")
        print("\n🚀 To start the server, run:")
        print("   python main.py")
        print("   or")
        print("   python run.py")
    else:
        print("\n⚠️ Some tests failed. Please check the configuration and try again.")
    
    return passed == len(tests)


def main():
    """Main test function"""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Run async tests
        success = asyncio.run(test_full_system())
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
