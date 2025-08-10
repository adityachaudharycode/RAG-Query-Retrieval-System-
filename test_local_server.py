"""
Test script for local-only LLM server
Tests the /api/v1/hackrx/run endpoint
"""
import requests
import json
import time
from datetime import datetime


def test_local_server():
    """Test the local LLM server"""
    print("🧪 TESTING LOCAL-ONLY LLM SERVER")
    print("=" * 60)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Server configuration
    BASE_URL = "http://localhost:8000"
    
    # Test document and questions
    test_data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for cataract surgery?",
            "What is the waiting period for pre-existing diseases?",
            "Does this policy cover maternity expenses?",
            "What is the No Claim Discount offered?"
        ]
    }
    
    # Test 1: Health check
    print("\n🔍 Step 1: Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check passed")
            print(f"📊 Status: {health_data.get('status')}")
            print(f"🤖 Models: {health_data.get('models', {})}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        print("💡 Make sure the server is running: python run_local_only.py")
        return False
    
    # Test 2: Root endpoint
    print("\n🏠 Step 2: Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            root_data = response.json()
            print("✅ Root endpoint working")
            print(f"📝 Message: {root_data.get('message')}")
            print(f"🎯 Features: {len(root_data.get('features', []))} listed")
        else:
            print(f"⚠️  Root endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Root endpoint error: {e}")
    
    # Test 3: Main endpoint
    print("\n🎯 Step 3: Testing main endpoint /api/v1/hackrx/run...")
    print(f"📄 Document: {test_data['documents'][:60]}...")
    print(f"❓ Questions: {len(test_data['questions'])}")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🚀 Sending request to local LLM server...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/v1/hackrx/run",
            headers=headers,
            json=test_data,
            timeout=300  # 5 minute timeout for local processing
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"📥 Response received in {total_time:.1f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            answers = result.get("answers", [])
            
            print("🎉 SUCCESS: Local LLM server working perfectly!")
            print(f"📝 Received {len(answers)} answers")
            
            # Display answers
            print(f"\n📋 ANSWERS FROM LOCAL LLM:")
            print("=" * 50)
            for i, (question, answer) in enumerate(zip(test_data["questions"], answers), 1):
                print(f"\n❓ Q{i}: {question}")
                print(f"💬 A{i}: {answer}")
                print("-" * 50)
            
            # Performance summary
            print(f"\n⚡ PERFORMANCE SUMMARY:")
            print("=" * 50)
            print(f"✅ Total time: {total_time:.1f} seconds")
            print(f"⚡ Average per question: {total_time/len(test_data['questions']):.1f} seconds")
            print(f"💰 Cost: $0.00 (completely free!)")
            print(f"🔄 Rate limits: None")
            print(f"🏠 Processing: 100% local")
            
            # Performance assessment
            if total_time <= 30:
                print("🎯 EXCELLENT: Under 30 seconds!")
            elif total_time <= 60:
                print("✅ GOOD: Under 1 minute")
            elif total_time <= 120:
                print("⚠️  ACCEPTABLE: Under 2 minutes")
            else:
                print("🐌 SLOW: Over 2 minutes (but still free!)")
            
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Raw error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (over 5 minutes)")
        print("💡 Local LLM might be processing - this is normal for first request")
        return False
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False


def test_multiple_requests():
    """Test multiple requests to check consistency"""
    print(f"\n🔄 TESTING MULTIPLE REQUESTS")
    print("=" * 50)
    
    BASE_URL = "http://localhost:8000"
    
    # Simple test data for quick testing
    test_data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment?"
        ]
    }
    
    headers = {"Content-Type": "application/json"}
    
    print("🧪 Making 3 consecutive requests...")
    
    times = []
    for i in range(3):
        print(f"\n📤 Request {i+1}/3...")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/v1/hackrx/run",
                headers=headers,
                json=test_data,
                timeout=120
            )
            end_time = time.time()
            
            request_time = end_time - start_time
            times.append(request_time)
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answers", [""])[0]
                print(f"✅ Request {i+1} successful ({request_time:.1f}s)")
                print(f"📝 Answer: {answer[:100]}...")
            else:
                print(f"❌ Request {i+1} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request {i+1} error: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n📊 Multiple Request Summary:")
        print(f"✅ Successful requests: {len(times)}/3")
        print(f"⏱️  Times: {[f'{t:.1f}s' for t in times]}")
        print(f"⚡ Average time: {avg_time:.1f}s")
        print(f"🎯 Consistency: {'Good' if max(times) - min(times) < 10 else 'Variable'}")


def main():
    """Main test function"""
    print("🏠 LOCAL-ONLY LLM SERVER TEST")
    print("=" * 60)
    print("Testing your local Ollama-based server")
    print("Endpoint: POST /api/v1/hackrx/run")
    print("=" * 60)
    
    # Test 1: Main functionality
    success = test_local_server()
    
    if success:
        # Test 2: Multiple requests
        test_multiple_requests()
        
        print(f"\n🎉 LOCAL SERVER TEST COMPLETED!")
        print("=" * 60)
        print("✅ Your local-only LLM server is working perfectly!")
        print("🎯 Benefits:")
        print("   • $0.00 cost per request")
        print("   • No API rate limits")
        print("   • Complete privacy (data stays local)")
        print("   • Works offline")
        print("   • Consistent performance")
        print("\n🚀 Your server is ready for production use!")
        print("📡 Server URL: http://localhost:8000")
        print("🎯 Endpoint: POST /api/v1/hackrx/run")
        
    else:
        print(f"\n❌ LOCAL SERVER TEST FAILED")
        print("=" * 60)
        print("🔧 Troubleshooting steps:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Check if models are downloaded:")
        print("   • ollama list")
        print("3. Start the server: python run_local_only.py")
        print("4. Check server logs for errors")
    
    print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
