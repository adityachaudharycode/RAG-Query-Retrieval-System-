"""
Test script for API fallback system
"""
import asyncio
import time
from datetime import datetime
from services.multi_api_service import MultiAPIService
from services.embedding_service import EmbeddingService
from services.query_processor import QueryProcessor
from services.vector_store import VectorStore


async def test_multi_api_service():
    """Test the multi-API service directly"""
    print("🧪 Testing Multi-API Service")
    print("=" * 50)
    
    multi_api = MultiAPIService()
    
    # Check available providers
    provider_info = multi_api.get_current_provider_info()
    print(f"Available providers: {provider_info['available_providers']}")
    print(f"Current provider: {provider_info['name']} ({provider_info['type']})")
    
    if provider_info['available_providers'] == 0:
        print("❌ No API providers configured!")
        print("Please add API keys to your .env file")
        return False
    
    # Test embeddings
    print("\n🔍 Testing embeddings generation...")
    test_texts = [
        "What is the grace period for premium payment?",
        "What is the waiting period for cataract surgery?",
        "What are the policy benefits?"
    ]
    
    try:
        start_time = time.time()
        embeddings = await multi_api.generate_embeddings(test_texts)
        end_time = time.time()
        
        print(f"✅ Embeddings generated successfully!")
        print(f"Shape: {embeddings.shape}")
        print(f"Time: {end_time - start_time:.2f} seconds")
        print(f"Provider used: {multi_api.get_current_provider_info()['name']}")
        
    except Exception as e:
        print(f"❌ Embeddings failed: {e}")
        return False
    
    # Test text generation
    print("\n💬 Testing text generation...")
    test_query = "What is the grace period for premium payment?"
    test_context = "The grace period for premium payment is 30 days from the due date."
    
    try:
        start_time = time.time()
        answer = await multi_api.generate_text(test_query, test_context)
        end_time = time.time()
        
        print(f"✅ Text generated successfully!")
        print(f"Answer: {answer[:100]}...")
        print(f"Time: {end_time - start_time:.2f} seconds")
        print(f"Provider used: {multi_api.get_current_provider_info()['name']}")
        
    except Exception as e:
        print(f"❌ Text generation failed: {e}")
        return False
    
    return True


async def test_embedding_service():
    """Test the embedding service with fallback"""
    print("\n🔍 Testing Embedding Service with Fallback")
    print("=" * 50)
    
    embedding_service = EmbeddingService()
    await embedding_service.initialize()
    
    test_texts = [
        "Insurance policy terms and conditions",
        "Premium payment grace period details",
        "Coverage benefits and exclusions"
    ]
    
    try:
        start_time = time.time()
        embeddings = await embedding_service.encode(test_texts)
        end_time = time.time()
        
        print(f"✅ Embedding service test passed!")
        print(f"Generated embeddings shape: {embeddings.shape}")
        print(f"Time: {end_time - start_time:.2f} seconds")
        return True
        
    except Exception as e:
        print(f"❌ Embedding service test failed: {e}")
        return False


async def test_query_processor():
    """Test the query processor with fallback"""
    print("\n💬 Testing Query Processor with Fallback")
    print("=" * 50)
    
    # Initialize services
    vector_store = VectorStore()
    await vector_store.initialize()
    
    query_processor = QueryProcessor(vector_store)
    
    test_query = "What is the grace period for premium payment?"
    test_context = """
    Premium Payment Grace Period:
    The policyholder has a grace period of 30 days from the premium due date to make the payment.
    During this grace period, the policy remains in force.
    If the premium is not paid within the grace period, the policy will lapse.
    """
    
    try:
        start_time = time.time()
        answer = await query_processor._generate_answer(test_query, test_context)
        end_time = time.time()
        
        print(f"✅ Query processor test passed!")
        print(f"Answer: {answer[:200]}...")
        print(f"Time: {end_time - start_time:.2f} seconds")
        return True
        
    except Exception as e:
        print(f"❌ Query processor test failed: {e}")
        return False


async def stress_test_rate_limits():
    """Stress test to trigger rate limits and test fallback"""
    print("\n🔥 Stress Testing Rate Limits")
    print("=" * 50)
    print("⚠️  This will make many API calls to test fallback behavior")
    
    response = input("Continue with stress test? (y/N): ")
    if response.lower() != 'y':
        print("Skipping stress test")
        return True
    
    multi_api = MultiAPIService()
    
    # Make many requests quickly to trigger rate limits
    test_texts = [f"Test query number {i}" for i in range(20)]
    
    successful_requests = 0
    failed_requests = 0
    provider_switches = 0
    last_provider = None
    
    for i, text in enumerate(test_texts):
        try:
            print(f"Request {i+1}/20...", end=" ")
            
            current_provider = multi_api.get_current_provider_info()['name']
            if last_provider and current_provider != last_provider:
                provider_switches += 1
                print(f"[SWITCHED to {current_provider}]", end=" ")
            last_provider = current_provider
            
            embeddings = await multi_api.generate_embeddings([text])
            successful_requests += 1
            print("✅")
            
        except Exception as e:
            failed_requests += 1
            print(f"❌ {str(e)[:50]}...")
        
        # Small delay between requests
        await asyncio.sleep(0.5)
    
    print(f"\n📊 Stress Test Results:")
    print(f"Successful requests: {successful_requests}/20")
    print(f"Failed requests: {failed_requests}/20")
    print(f"Provider switches: {provider_switches}")
    print(f"Final provider: {multi_api.get_current_provider_info()['name']}")
    
    return successful_requests > 0


async def main():
    """Main test function"""
    print("🔄 API FALLBACK SYSTEM TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Set up Perplexity for testing
    import os
    os.environ["PERPLEXITY_API_KEY"] = "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"
    os.environ["PERPLEXITY_MODEL"] = "sonar-large-chat"

    tests = [
        ("Multi-API Service", test_multi_api_service),
        ("Embedding Service", test_embedding_service),
        ("Query Processor", test_query_processor),
        ("Stress Test", stress_test_rate_limits)
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
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API fallback system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check your API keys and configuration.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())
