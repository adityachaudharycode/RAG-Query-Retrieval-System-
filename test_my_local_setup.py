"""
Quick test script to verify your local Ollama setup
"""
import asyncio
import aiohttp
import requests
import json
import time


async def test_ollama_service():
    """Test if Ollama service is running"""
    print("🔍 Testing Ollama Service")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            print(f"✅ Ollama running: {version_info.get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ Ollama responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama not accessible: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False


def test_available_models():
    """Test what models are available"""
    print("\n📋 Checking Available Models")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            
            print(f"Found {len(models)} models:")
            for model in models:
                name = model.get("name", "Unknown")
                size = model.get("size", 0)
                size_gb = size / (1024**3) if size > 0 else 0
                print(f"   • {name} ({size_gb:.1f}GB)")
            
            # Check for required models
            model_names = [model["name"] for model in models]
            
            required_models = {
                "nomic-embed-text": "Embedding model",
                "llama3.2:3b": "Text generation (primary)",
                "llama3.2:1b": "Text generation (fallback)"
            }
            
            print(f"\n🎯 Required Models Check:")
            all_available = True
            for model, description in required_models.items():
                available = any(model in name for name in model_names)
                status = "✅" if available else "❌"
                print(f"   {status} {model} - {description}")
                if not available:
                    all_available = False
                    print(f"      💡 Download with: ollama pull {model}")
            
            return all_available
            
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False


async def test_embedding_model():
    """Test the embedding model"""
    print("\n🔍 Testing Embedding Model")
    print("=" * 30)
    
    try:
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            async with session.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": "What is the grace period for premium payment?"
                },
                timeout=30
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    embedding = result.get("embedding", [])
                    
                    end_time = time.time()
                    
                    print(f"✅ Embedding generated successfully!")
                    print(f"📊 Embedding dimensions: {len(embedding)}")
                    print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
                    print(f"🔢 Sample values: {embedding[:5]}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Embedding failed: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False


async def test_text_generation():
    """Test text generation models"""
    print("\n💬 Testing Text Generation Models")
    print("=" * 30)
    
    models_to_test = ["llama3.2:3b", "llama3.2:1b"]
    
    for model in models_to_test:
        print(f"\n🤖 Testing {model}...")
        
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                
                async with session.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model,
                        "prompt": "What is insurance? Answer in one sentence.",
                        "stream": False,
                        "options": {
                            "num_predict": 100,
                            "temperature": 0.1
                        }
                    },
                    timeout=60
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        answer = result.get("response", "").strip()
                        
                        end_time = time.time()
                        
                        print(f"✅ {model} working!")
                        print(f"📝 Answer: {answer}")
                        print(f"⏱️  Time: {end_time - start_time:.2f} seconds")
                    else:
                        error_text = await response.text()
                        print(f"❌ {model} failed: {error_text}")
                        
        except Exception as e:
            print(f"❌ {model} test failed: {e}")


async def test_full_pipeline():
    """Test the complete pipeline"""
    print("\n🔄 Testing Complete Pipeline")
    print("=" * 30)
    
    # Test question and context
    question = "What is the grace period for premium payment?"
    context = """
    Insurance Policy Terms:
    The grace period for premium payment is 30 days from the due date.
    During this grace period, the policy remains in force.
    If the premium is not paid within the grace period, the policy will lapse.
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            # Step 1: Generate embedding for question
            print("🔍 Step 1: Generating question embedding...")
            start_time = time.time()
            
            async with session.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": question
                },
                timeout=30
            ) as response:
                
                if response.status == 200:
                    embedding_result = await response.json()
                    embedding_time = time.time() - start_time
                    print(f"✅ Embedding generated in {embedding_time:.2f}s")
                else:
                    print("❌ Embedding failed")
                    return False
            
            # Step 2: Generate answer using context
            print("💬 Step 2: Generating answer...")
            start_time = time.time()
            
            full_prompt = f"""Context: {context.strip()}

Question: {question}

Please provide a clear answer based on the context.

Answer:"""
            
            async with session.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 200,
                        "temperature": 0.1
                    }
                },
                timeout=60
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    answer = result.get("response", "").strip()
                    generation_time = time.time() - start_time
                    
                    print(f"✅ Answer generated in {generation_time:.2f}s")
                    print(f"📝 Answer: {answer}")
                    
                    total_time = embedding_time + generation_time
                    print(f"⏱️  Total pipeline time: {total_time:.2f}s")
                    return True
                else:
                    print("❌ Text generation failed")
                    return False
                    
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🧪 LOCAL OLLAMA SETUP TEST")
    print("=" * 50)
    print("Testing your existing setup:")
    print("• Ollama service")
    print("• llama3.2:3b & llama3.2:1b")
    print("• nomic-embed-text")
    print("=" * 50)
    
    # Test 1: Ollama service
    if not test_ollama_service():
        print("\n❌ Ollama service not running. Please start it with: ollama serve")
        return
    
    # Test 2: Available models
    if not test_available_models():
        print("\n❌ Some required models are missing. Please download them.")
        return
    
    # Test 3: Embedding model
    if not await test_embedding_model():
        print("\n❌ Embedding model not working properly.")
        return
    
    # Test 4: Text generation models
    await test_text_generation()
    
    # Test 5: Full pipeline
    pipeline_success = await test_full_pipeline()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    if pipeline_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your local setup is working perfectly")
        print("🚀 Ready to run: python run_local_only.py")
        print("\n💡 Benefits of your local setup:")
        print("   • $0.00 cost per request")
        print("   • No rate limits")
        print("   • Complete privacy")
        print("   • Works offline")
        print("   • Consistent performance")
    else:
        print("⚠️  Some tests failed")
        print("💡 Check the errors above and fix them")
        print("🔧 Common fixes:")
        print("   • Make sure Ollama is running: ollama serve")
        print("   • Download missing models: ollama pull <model-name>")
        print("   • Restart Ollama service if needed")


if __name__ == "__main__":
    asyncio.run(main())
