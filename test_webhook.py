"""
Test script for deployed webhook on Render
"""
import requests
import json
import time
from datetime import datetime


def test_webhook(webhook_url):
    """Test the deployed webhook endpoint"""
    
    print("=" * 70)
    print("🌐 WEBHOOK DEPLOYMENT TEST")
    print("=" * 70)
    print(f"🔗 Testing URL: {webhook_url}")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration
    BEARER_TOKEN = "87e1f87355284c19bac1880413d4a1e7cb868891939fc1c6d8227ee2c1b89cb0"
    
    # Test documents
    test_cases = [
        {
            "name": "PDF Document",
            "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "questions": [
                "What is the grace period for premium payment?",
                "What is the waiting period for cataract surgery?"
            ]
        },
        {
            "name": "Google Drive DOCX",
            "documents": "https://drive.google.com/uc?export=download&id=1l9C5DmyxNgNdXGkhVkJ53V491tat1H1x",
            "questions": [
                "What is the main topic of this document?",
                "What are the key points mentioned?"
            ]
        }
    ]
    
    # Test health endpoint first
    print("\n🔍 Testing health endpoint...")
    try:
        health_url = webhook_url.replace('/api/v1/hackrx/run', '/health')
        response = requests.get(health_url, timeout=30)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"⚠️  Health check returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test webhook endpoint
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"🧪 Test {i}: {test_case['name']}")
        print(f"{'='*50}")
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "documents": test_case["documents"],
            "questions": test_case["questions"]
        }
        
        print(f"📄 Document: {test_case['documents'][:60]}...")
        print(f"❓ Questions: {len(test_case['questions'])}")
        
        # Make request
        start_time = time.time()
        try:
            print("🚀 Sending request...")
            response = requests.post(
                webhook_url,
                headers=headers,
                json=payload,
                timeout=180  # 3 minute timeout for deployed service
            )
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"📥 Response received in {total_time:.1f} seconds")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                answers = result.get("answers", [])
                
                print(f"✅ SUCCESS: {test_case['name']} processed!")
                print(f"📊 Received {len(answers)} answers")
                
                # Show sample answer
                if answers:
                    print(f"📝 Sample answer: {answers[0][:200]}...")
                
                # Performance assessment
                if total_time <= 60:
                    print("🎯 EXCELLENT: Under 1 minute!")
                elif total_time <= 120:
                    print("✅ GOOD: Under 2 minutes")
                else:
                    print("⚠️  ACCEPTABLE: Over 2 minutes (cold start expected)")
                
                results.append({
                    "test": test_case['name'],
                    "success": True,
                    "time": total_time,
                    "answers": len(answers)
                })
                
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                try:
                    error = response.json()
                    print(f"Error: {json.dumps(error, indent=2)}")
                except:
                    print(f"Raw error: {response.text}")
                
                results.append({
                    "test": test_case['name'],
                    "success": False,
                    "error": response.status_code
                })
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
            results.append({
                "test": test_case['name'],
                "success": False,
                "error": "Timeout"
            })
        except Exception as e:
            print(f"❌ Request failed: {e}")
            results.append({
                "test": test_case['name'],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 WEBHOOK TEST SUMMARY")
    print(f"{'='*70}")
    
    successful_tests = sum(1 for r in results if r["success"])
    total_tests = len(results)
    
    print(f"✅ Successful tests: {successful_tests}/{total_tests}")
    
    for result in results:
        if result["success"]:
            print(f"✅ {result['test']}: {result['time']:.1f}s ({result['answers']} answers)")
        else:
            print(f"❌ {result['test']}: {result.get('error', 'Unknown error')}")
    
    if successful_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED! Webhook is ready for submission.")
        print(f"🔗 Submit this URL: {webhook_url}")
    else:
        print(f"\n⚠️  Some tests failed. Check the errors above.")
    
    print(f"\n🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return successful_tests == total_tests


def main():
    """Main test function"""
    print("🌐 RENDER WEBHOOK TESTER")
    print("=" * 70)
    
    # Get webhook URL from user
    webhook_url = input("Enter your Render webhook URL: ").strip()
    
    if not webhook_url:
        print("❌ No URL provided. Exiting.")
        return
    
    # Ensure URL has correct endpoint
    if not webhook_url.endswith('/api/v1/hackrx/run'):
        if webhook_url.endswith('/'):
            webhook_url = webhook_url + 'api/v1/hackrx/run'
        else:
            webhook_url = webhook_url + '/api/v1/hackrx/run'
        print(f"🔧 Corrected URL: {webhook_url}")
    
    # Run tests
    success = test_webhook(webhook_url)
    
    if success:
        print(f"\n🎯 READY FOR SUBMISSION!")
        print(f"Copy this URL: {webhook_url}")
    else:
        print(f"\n🔧 Fix the issues and test again.")


if __name__ == "__main__":
    main()
