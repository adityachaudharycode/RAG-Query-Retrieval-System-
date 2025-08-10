"""
Test script for Perplexity Pro Sonar integration
"""
import asyncio
import requests
import json
from datetime import datetime
from services.multi_api_service import MultiAPIService


def test_perplexity_direct():
    """Test Perplexity API directly"""
    print("🔍 Testing Perplexity API Directly")
    print("=" * 50)
    
    # Your Perplexity API key from the file
    api_key = "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"
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Test different Perplexity models
    models_to_test = [
        "sonar-large-chat",
        "sonar-medium-chat", 
        "sonar",
        "llama-3.1-sonar-large-128k-chat",
        "llama-3.1-sonar-small-128k-chat"
    ]
    
    test_message = {
        "role": "user", 
        "content": "What is the grace period for premium payment in insurance policies?"
    }
    
    working_models = []
    
    for model in models_to_test:
        print(f"\n🧪 Testing model: {model}")
        
        data = {
            "model": model,
            "messages": [test_message],
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    answer = result["choices"][0]["message"]["content"]
                    print(f"✅ {model} - SUCCESS")
                    print(f"Answer: {answer[:100]}...")
                    working_models.append(model)
                else:
                    print(f"❌ {model} - No content in response")
            else:
                print(f"❌ {model} - HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ {model} - Error: {str(e)}")
    
    print(f"\n📊 Working models: {working_models}")
    return working_models


async def test_perplexity_in_multi_api():
    """Test Perplexity integration in multi-API service"""
    print("\n🔄 Testing Perplexity in Multi-API Service")
    print("=" * 50)
    
    # Set up environment variable for testing
    import os
    os.environ["PERPLEXITY_API_KEY"] = "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"
    os.environ["PERPLEXITY_MODEL"] = "sonar-large-chat"
    
    # Reload config to pick up new environment variables
    from importlib import reload
    import config
    reload(config)
    
    multi_api = MultiAPIService()
    
    # Check if Perplexity is available
    provider_info = multi_api.get_current_provider_info()
    print(f"Available providers: {provider_info['available_providers']}")
    
    perplexity_available = any(p["type"] == "perplexity" for p in multi_api.api_providers)
    print(f"Perplexity available: {perplexity_available}")
    
    if not perplexity_available:
        print("❌ Perplexity not configured in multi-API service")
        return False
    
    # Test text generation
    test_query = "What is the grace period for premium payment?"
    test_context = """
    Insurance Policy Terms:
    The grace period for premium payment is typically 30 days from the due date.
    During this period, the policy remains in force even if the premium is not paid.
    If payment is not received within the grace period, the policy may lapse.
    """
    
    try:
        print(f"\n💬 Testing text generation...")
        print(f"Query: {test_query}")
        
        answer = await multi_api.generate_text(test_query, test_context)
        
        print(f"✅ Perplexity text generation successful!")
        print(f"Answer: {answer}")
        
        current_provider = multi_api.get_current_provider_info()
        print(f"Provider used: {current_provider['name']} ({current_provider['type']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Perplexity text generation failed: {e}")
        return False


async def test_fallback_chain():
    """Test the complete fallback chain including Perplexity"""
    print("\n🔗 Testing Complete Fallback Chain")
    print("=" * 50)
    
    # Set up all environment variables
    import os
    os.environ["PERPLEXITY_API_KEY"] = "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"
    os.environ["PERPLEXITY_MODEL"] = "sonar-large-chat"
    
    # Reload config
    from importlib import reload
    import config
    reload(config)
    
    multi_api = MultiAPIService()
    
    print("🔍 Available providers in fallback chain:")
    for i, provider in enumerate(multi_api.api_providers):
        print(f"{i+1}. {provider['name']} ({provider['type']})")
    
    # Test multiple requests to see provider switching
    test_queries = [
        "What is the grace period for premium payment?",
        "What is the waiting period for cataract surgery?", 
        "What are the policy benefits and coverage?",
        "How does the claim process work?",
        "What are the exclusions in the policy?"
    ]
    
    test_context = """
    Insurance Policy Document:
    This policy provides comprehensive coverage with a 30-day grace period for premium payments.
    Cataract surgery has a 2-year waiting period. The policy covers medical expenses up to the sum insured.
    Claims must be filed within 30 days of treatment. Pre-existing diseases have a 4-year waiting period.
    """
    
    successful_requests = 0
    provider_usage = {}
    
    for i, query in enumerate(test_queries):
        print(f"\n📝 Request {i+1}: {query[:50]}...")
        
        try:
            answer = await multi_api.generate_text(query, test_context)
            
            current_provider = multi_api.get_current_provider_info()
            provider_name = current_provider['name']
            
            if provider_name not in provider_usage:
                provider_usage[provider_name] = 0
            provider_usage[provider_name] += 1
            
            print(f"✅ Success with {provider_name}")
            print(f"Answer: {answer[:100]}...")
            successful_requests += 1
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
        
        # Small delay between requests
        await asyncio.sleep(1)
    
    print(f"\n📊 Fallback Chain Test Results:")
    print(f"Successful requests: {successful_requests}/{len(test_queries)}")
    print(f"Provider usage: {provider_usage}")
    
    return successful_requests > 0


async def main():
    """Main test function"""
    print("🚀 PERPLEXITY PRO SONAR INTEGRATION TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Direct Perplexity API", test_perplexity_direct),
        ("Perplexity in Multi-API", test_perplexity_in_multi_api),
        ("Complete Fallback Chain", test_fallback_chain)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 PERPLEXITY INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Perplexity Pro Sonar successfully integrated!")
        print("🔄 Your fallback chain now includes:")
        print("   1. Gemini APIs (3 keys)")
        print("   2. Perplexity Pro Sonar")
        print("   3. OpenAI (if configured)")
        print("   4. Hugging Face (if configured)")
    else:
        print("⚠️  Some tests failed. Check your Perplexity API key and configuration.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())
