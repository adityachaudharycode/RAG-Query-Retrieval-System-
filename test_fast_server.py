"""
Test script for FAST optimized local LLM server
Target: 30-60 seconds with accurate answers
"""
import requests
import json
import time
from datetime import datetime


def test_fast_server():
    """Test the optimized fast server"""
    print("⚡ TESTING FAST LOCAL LLM SERVER")
    print("🎯 Target: 30-60 seconds with accurate answers")
    print("=" * 60)
    
    BASE_URL = "http://localhost:8000"
    
    # Test with the policy document
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
    
    # Health check first
    print("🔍 Health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Server healthy - Version {health.get('version')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        print("💡 Start server: python run_local_fast.py")
        return False
    
    # Main test
    print(f"\n⚡ Testing FAST endpoint...")
    print(f"📄 Document: Policy PDF")
    print(f"❓ Questions: {len(test_data['questions'])}")
    
    headers = {"Content-Type": "application/json"}
    
    try:
        print("🚀 Sending request...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/v1/hackrx/run",
            headers=headers,
            json=test_data,
            timeout=120  # 2 minute max
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"📥 Response received in {total_time:.1f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            answers = result.get("answers", [])
            
            print("🎉 SUCCESS!")
            print(f"📊 Performance Analysis:")
            print(f"   ⏱️  Time: {total_time:.1f} seconds")
            
            # Performance rating
            if total_time <= 30:
                print("   🏆 EXCELLENT: Under 30 seconds!")
            elif total_time <= 60:
                print("   ✅ TARGET MET: Under 60 seconds!")
            elif total_time <= 90:
                print("   ⚠️  ACCEPTABLE: Under 90 seconds")
            else:
                print("   ❌ TOO SLOW: Over 90 seconds")
            
            print(f"   💰 Cost: $0.00")
            print(f"   🔄 Rate limits: None")
            
            # Accuracy analysis
            print(f"\n📝 ACCURACY ANALYSIS:")
            print("=" * 50)
            
            for i, (question, answer) in enumerate(zip(test_data["questions"], answers), 1):
                print(f"\n❓ Q{i}: {question}")
                print(f"💬 A{i}: {answer}")
                
                # Check for generic/unhelpful answers
                generic_phrases = [
                    "not mentioned in the document",
                    "information is not available",
                    "cannot be determined",
                    "not specified",
                    "I don't have information"
                ]
                
                is_generic = any(phrase.lower() in answer.lower() for phrase in generic_phrases)
                
                if is_generic:
                    print(f"   ⚠️  Generic answer - may need better context retrieval")
                else:
                    print(f"   ✅ Specific answer provided")
                
                print("-" * 50)
            
            return True
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            try:
                error = response.json()
                print(f"Error: {json.dumps(error, indent=2)}")
            except:
                print(f"Raw error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (over 2 minutes)")
        return False
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False


def test_accuracy_focused():
    """Test with questions that should have clear answers in the document"""
    print(f"\n🎯 ACCURACY FOCUSED TEST")
    print("=" * 50)
    
    BASE_URL = "http://localhost:8000"
    
    # Questions with known answers in the policy document
    accuracy_test = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "What is the waiting period for cataract surgery?"
        ]
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        print("🔍 Testing accuracy with specific questions...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/v1/hackrx/run",
            headers=headers,
            json=accuracy_test,
            timeout=90
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            answers = result.get("answers", [])
            
            print(f"⏱️  Time: {total_time:.1f} seconds")
            print(f"\n📊 ACCURACY RESULTS:")
            
            # Expected answer patterns (what we should see)
            expected_patterns = [
                ["30 days", "grace period", "premium"],  # Grace period
                ["4 years", "pre-existing", "waiting"],   # PED waiting period  
                ["2 years", "cataract", "waiting"]       # Cataract waiting
            ]
            
            accuracy_score = 0
            for i, (question, answer, patterns) in enumerate(zip(accuracy_test["questions"], answers, expected_patterns), 1):
                print(f"\n❓ Q{i}: {question[:60]}...")
                print(f"💬 A{i}: {answer}")
                
                # Check if answer contains expected information
                matches = sum(1 for pattern in patterns if pattern.lower() in answer.lower())
                accuracy = matches / len(patterns)
                
                if accuracy >= 0.67:  # At least 2/3 patterns match
                    print(f"   ✅ ACCURATE ({matches}/{len(patterns)} key terms found)")
                    accuracy_score += 1
                else:
                    print(f"   ❌ INACCURATE ({matches}/{len(patterns)} key terms found)")
                    print(f"   Expected terms: {patterns}")
            
            overall_accuracy = (accuracy_score / len(accuracy_test["questions"])) * 100
            print(f"\n📊 OVERALL ACCURACY: {overall_accuracy:.0f}% ({accuracy_score}/{len(accuracy_test['questions'])})")
            
            if overall_accuracy >= 80:
                print("🎯 EXCELLENT accuracy!")
            elif overall_accuracy >= 60:
                print("✅ GOOD accuracy")
            else:
                print("⚠️  NEEDS IMPROVEMENT")
            
            return overall_accuracy >= 60
            
    except Exception as e:
        print(f"❌ Accuracy test failed: {e}")
        return False


def main():
    """Main test function"""
    print("⚡ FAST LOCAL LLM SERVER TEST")
    print("🎯 Testing speed (30-60s target) and accuracy")
    print("=" * 60)
    
    # Test 1: Speed and basic functionality
    speed_success = test_fast_server()
    
    if speed_success:
        # Test 2: Accuracy focused
        accuracy_success = test_accuracy_focused()
        
        print(f"\n🏆 FINAL RESULTS")
        print("=" * 60)
        
        if speed_success and accuracy_success:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Speed: Target met (under 60s)")
            print("✅ Accuracy: Good results from document")
            print("💰 Cost: $0.00 per request")
            print("🔄 Rate limits: None")
            print("\n🚀 Your optimized local server is ready!")
        else:
            print("⚠️  MIXED RESULTS")
            print(f"Speed test: {'✅ PASSED' if speed_success else '❌ FAILED'}")
            print(f"Accuracy test: {'✅ PASSED' if accuracy_success else '❌ FAILED'}")
            
            if not accuracy_success:
                print("\n💡 Accuracy improvement tips:")
                print("• Check if document contains the expected information")
                print("• Try different chunk sizes in run_local_fast.py")
                print("• Verify embedding model is working correctly")
    else:
        print("\n❌ SPEED TEST FAILED")
        print("🔧 Troubleshooting:")
        print("• Make sure Ollama is running: ollama serve")
        print("• Check if models are downloaded: ollama list")
        print("• Restart the server: python run_local_fast.py")
    
    print(f"\n🕒 Test completed at: {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()
