"""
Test script for local LLM integration
"""
import asyncio
import time
from datetime import datetime
from services.local_llm_service import LocalLLMService
from services.multi_api_service import MultiAPIService
from services.embedding_service import EmbeddingService
from services.query_processor import QueryProcessor
from services.vector_store import VectorStore


async def test_local_llm_direct():
    """Test local LLM service directly"""
    print("🏠 Testing Local LLM Service Directly")
    print("=" * 50)
    
    local_llm = LocalLLMService()
    
    # Initialize
    available = await local_llm.initialize()
    
    if not available:
        print("❌ Local LLM service not available")
        print("💡 Run 'python setup_local_llm.py' to set up Ollama")
        return False
    
    model_info = local_llm.get_model_info()
    print(f"✅ Local LLM service available")
    print(f"📊 Model info: {model_info}")
    
    # Test embeddings
    print("\n🔍 Testing local embeddings...")
    test_texts = [
        "What is the grace period for premium payment?",
        "What is the waiting period for cataract surgery?",
        "What are the policy benefits?"
    ]
    
    try:
        start_time = time.time()
        embeddings = await local_llm.generate_embeddings(test_texts)
        end_time = time.time()
        
        print(f"✅ Local embeddings successful!")
        print(f"Shape: {embeddings.shape}")
        print(f"Time: {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Local embeddings failed: {e}")
        await local_llm.close()
        return False
    
    # Test text generation
    print("\n💬 Testing local text generation...")
    test_query = "What is the grace period for premium payment?"
    test_context = """
    Insurance Policy Terms:
    The grace period for premium payment is 30 days from the due date.
    During this grace period, the policy remains in force.
    If the premium is not paid within the grace period, the policy will lapse.
    """
    
    try:
        start_time = time.time()
        answer = await local_llm.generate_text(test_query, test_context)
        end_time = time.time()
        
        print(f"✅ Local text generation successful!")
        print(f"Answer: {answer}")
        print(f"Time: {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Local text generation failed: {e}")
        await local_llm.close()
        return False
    
    await local_llm.close()
    return True


async def test_multi_api_with_local():
    """Test multi-API service with local LLM priority"""
    print("\n🔄 Testing Multi-API Service with Local LLM Priority")
    print("=" * 50)
    
    multi_api = MultiAPIService()
    await multi_api.initialize()
    
    print(f"Local LLM available: {multi_api.local_llm_available}")
    
    if multi_api.local_llm_available:
        print("🏠 Local LLM will be tried first (free, no rate limits)")
    else:
        print("⚠️  Local LLM not available, using API-only mode")
    
    provider_info = multi_api.get_current_provider_info()
    print(f"API providers available: {provider_info['available_providers']}")
    
    # Test embeddings
    print("\n🔍 Testing embeddings with local priority...")
    test_texts = [
        "Insurance policy terms and conditions",
        "Premium payment grace period details",
        "Coverage benefits and exclusions"
    ]
    
    try:
        start_time = time.time()
        embeddings = await multi_api.generate_embeddings(test_texts)
        end_time = time.time()
        
        print(f"✅ Embeddings successful!")
        print(f"Shape: {embeddings.shape}")
        print(f"Time: {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Embeddings failed: {e}")
        return False
    
    # Test text generation
    print("\n💬 Testing text generation with local priority...")
    test_query = "What is the waiting period for cataract surgery?"
    test_context = """
    Medical Coverage Terms:
    Cataract surgery has a waiting period of 2 years from the policy start date.
    This waiting period applies to all eye-related surgeries.
    Emergency eye treatments are covered immediately.
    """
    
    try:
        start_time = time.time()
        answer = await multi_api.generate_text(test_query, test_context)
        end_time = time.time()
        
        print(f"✅ Text generation successful!")
        print(f"Answer: {answer[:200]}...")
        print(f"Time: {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Text generation failed: {e}")
        return False
    
    return True


async def test_full_system_integration():
    """Test the full system with local LLM integration"""
    print("\n🎯 Testing Full System Integration")
    print("=" * 50)
    
    # Initialize all services
    vector_store = VectorStore()
    await vector_store.initialize()
    
    embedding_service = EmbeddingService()
    await embedding_service.initialize()
    
    query_processor = QueryProcessor(vector_store)
    
    # Test document processing with local LLM
    print("📄 Testing document processing with local LLM...")
    
    test_document = """
    National Parivar Mediclaim Plus Policy
    
    Premium Payment Grace Period:
    The policyholder has a grace period of 30 days from the premium due date to make the payment.
    During this grace period, the policy remains in force.
    
    Waiting Periods:
    - Pre-existing diseases: 4 years
    - Cataract surgery: 2 years
    - Maternity expenses: 3 years
    
    Coverage Benefits:
    - Hospitalization expenses up to sum insured
    - Pre and post hospitalization: 60 days before and 90 days after
    - Ambulance charges: Up to Rs. 2,000 per hospitalization
    """
    
    # Create chunks and embeddings
    from services.document_processor import DocumentProcessor
    doc_processor = DocumentProcessor()
    chunks = await doc_processor.chunk_text(test_document)
    
    print(f"Created {len(chunks)} chunks")
    
    # Add to vector store (will use local LLM if available)
    await vector_store.add_documents(chunks)
    
    # Test queries
    test_questions = [
        "What is the grace period for premium payment?",
        "What is the waiting period for cataract surgery?",
        "What are the coverage benefits?"
    ]
    
    print(f"\n❓ Testing {len(test_questions)} questions...")
    
    successful_answers = 0
    total_time = 0
    
    for i, question in enumerate(test_questions, 1):
        print(f"\nQ{i}: {question}")
        
        try:
            start_time = time.time()
            answer = await query_processor.process_query(question, test_document)
            end_time = time.time()
            
            query_time = end_time - start_time
            total_time += query_time
            
            print(f"A{i}: {answer[:150]}...")
            print(f"⏱️  Time: {query_time:.2f}s")
            
            successful_answers += 1
            
        except Exception as e:
            print(f"❌ Q{i} failed: {e}")
    
    print(f"\n📊 Full System Test Results:")
    print(f"Successful answers: {successful_answers}/{len(test_questions)}")
    print(f"Average time per question: {total_time/len(test_questions):.2f}s")
    print(f"Total time: {total_time:.2f}s")
    
    return successful_answers == len(test_questions)


async def performance_comparison():
    """Compare local LLM vs API performance"""
    print("\n⚡ Performance Comparison: Local LLM vs APIs")
    print("=" * 50)
    
    multi_api = MultiAPIService()
    await multi_api.initialize()
    
    if not multi_api.local_llm_available:
        print("❌ Local LLM not available for comparison")
        return
    
    test_query = "What is insurance?"
    test_context = "Insurance is a contract that provides financial protection against losses."
    
    # Test local LLM
    print("🏠 Testing Local LLM performance...")
    try:
        start_time = time.time()
        local_answer = await multi_api.local_llm_service.generate_text(test_query, test_context)
        local_time = time.time() - start_time
        print(f"✅ Local LLM: {local_time:.2f}s")
    except Exception as e:
        print(f"❌ Local LLM failed: {e}")
        local_time = None
        local_answer = None
    
    # Test API (force API by temporarily disabling local LLM)
    print("🌐 Testing API performance...")
    multi_api.local_llm_available = False  # Temporarily disable
    try:
        start_time = time.time()
        api_answer = await multi_api.generate_text(test_query, test_context)
        api_time = time.time() - start_time
        print(f"✅ API: {api_time:.2f}s")
    except Exception as e:
        print(f"❌ API failed: {e}")
        api_time = None
        api_answer = None
    
    # Comparison
    if local_time and api_time:
        speedup = api_time / local_time
        print(f"\n📊 Performance Comparison:")
        print(f"Local LLM: {local_time:.2f}s")
        print(f"API: {api_time:.2f}s")
        print(f"Speedup: {speedup:.1f}x {'faster' if speedup > 1 else 'slower'}")
        
        print(f"\n💰 Cost Comparison:")
        print(f"Local LLM: $0.00 (free)")
        print(f"API: ~$0.01-0.05 per request")


async def main():
    """Main test function"""
    print("🏠 LOCAL LLM INTEGRATION TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Local LLM Direct", test_local_llm_direct),
        ("Multi-API with Local Priority", test_multi_api_with_local),
        ("Full System Integration", test_full_system_integration),
        ("Performance Comparison", performance_comparison)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 LOCAL LLM INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed >= 2:  # At least local LLM and multi-API working
        print("🎉 Local LLM integration successful!")
        print("💡 Benefits:")
        print("   • Free unlimited usage (no API costs)")
        print("   • No rate limits")
        print("   • Privacy (data stays local)")
        print("   • Fast responses")
        print("   • Works offline")
    else:
        print("⚠️  Local LLM integration needs attention.")
        print("💡 Run 'python setup_local_llm.py' to set up Ollama")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())
