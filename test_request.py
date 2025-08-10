"""
Test script to make a proper request to the optimized API
"""
import requests
import json
import time
from datetime import datetime


# Configuration
API_BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "87e1f87355284c19bac1880413d4a1e7cb868891939fc1c6d8227ee2c1b89cb0"  # From .env.example

# Test documents and questions
TEST_DOCUMENTS = {
    "PDF": {
        "url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for cataract surgery?",
            "What is the waiting period for pre-existing diseases?"
        ]
    },
    "DOCX": {
        "url": "https://drive.google.com/uc?export=download&id=1l9C5DmyxNgNdXGkhVkJ53V491tat1H1x",
        "questions": [
            "What is the main topic of this document?",
            "What are the key points mentioned?",
            "What information is provided in the document?"
        ]
    }
}

# Default test (PDF)
TEST_DOCUMENT_URL = TEST_DOCUMENTS["PDF"]["url"]
TEST_QUESTIONS = TEST_DOCUMENTS["PDF"]["questions"]


def test_health_endpoint():
    """Test the health endpoint first"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_main_endpoint():
    """Test the main /hackrx/run endpoint"""
    print("\n🚀 Testing main endpoint...")
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Prepare payload
    payload = {
        "documents": TEST_DOCUMENT_URL,
        "questions": TEST_QUESTIONS
    }
    
    print("📤 Request details:")
    print(f"URL: {API_BASE_URL}/hackrx/run")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    # Make request
    start_time = time.time()
    try:
        response = requests.post(
            f"{API_BASE_URL}/hackrx/run",
            headers=headers,
            json=payload,
            timeout=120  # 2 minute timeout
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n📥 Response details:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {total_time:.1f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            answers = result.get("answers", [])
            
            print("✅ Request successful!")
            print(f"📊 Received {len(answers)} answers")
            
            # Display answers
            print("\n📝 Answers:")
            for i, (question, answer) in enumerate(zip(TEST_QUESTIONS, answers), 1):
                print(f"\nQ{i}: {question}")
                print(f"A{i}: {answer[:200]}{'...' if len(answer) > 200 else ''}")
            
            # Performance assessment
            print(f"\n⚡ Performance Assessment:")
            if total_time <= 30:
                print("🎯 EXCELLENT: Under 30 seconds!")
            elif total_time <= 60:
                print("✅ GOOD: Under 1 minute")
            elif total_time <= 120:
                print("⚠️  ACCEPTABLE: Under 2 minutes")
            else:
                print("❌ SLOW: Over 2 minutes")
                
            return True
            
        elif response.status_code == 422:
            print("❌ Validation Error (422):")
            try:
                error_detail = response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Raw error: {response.text}")
            return False
            
        elif response.status_code == 401:
            print("❌ Authentication Error (401):")
            print("Check your bearer token in .env file")
            print(f"Expected: {BEARER_TOKEN}")
            return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}:")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (over 2 minutes)")
        return False
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False


def test_schema_validation():
    """Test different payload formats to identify validation issues"""
    print("\n🔍 Testing schema validation...")
    
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test cases
    test_cases = [
        {
            "name": "Valid payload",
            "payload": {
                "documents": TEST_DOCUMENT_URL,
                "questions": TEST_QUESTIONS
            }
        },
        {
            "name": "Missing documents",
            "payload": {
                "questions": TEST_QUESTIONS
            }
        },
        {
            "name": "Missing questions",
            "payload": {
                "documents": TEST_DOCUMENT_URL
            }
        },
        {
            "name": "Empty questions list",
            "payload": {
                "documents": TEST_DOCUMENT_URL,
                "questions": []
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        try:
            response = requests.post(
                f"{API_BASE_URL}/hackrx/run",
                headers=headers,
                json=test_case["payload"],
                timeout=10
            )
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                try:
                    error = response.json()
                    print(f"Error: {json.dumps(error, indent=2)}")
                except:
                    print(f"Raw error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")


def test_both_document_types():
    """Test both PDF and DOCX document processing"""
    print("\n📄 Testing both document types...")

    results = {}

    for doc_type, doc_info in TEST_DOCUMENTS.items():
        print(f"\n{'='*50}")
        print(f"🔍 Testing {doc_type} document")
        print(f"{'='*50}")

        # Prepare request
        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "documents": doc_info["url"],
            "questions": doc_info["questions"]
        }

        print(f"📄 Document: {doc_info['url'][:60]}...")
        print(f"❓ Questions: {len(doc_info['questions'])}")

        # Make request
        start_time = time.time()
        try:
            response = requests.post(
                f"{API_BASE_URL}/hackrx/run",
                headers=headers,
                json=payload,
                timeout=120
            )

            end_time = time.time()
            total_time = end_time - start_time

            if response.status_code == 200:
                result = response.json()
                answers = result.get("answers", [])

                print(f"✅ {doc_type} processing successful!")
                print(f"⏱️  Time: {total_time:.1f} seconds")
                print(f"📊 Answers: {len(answers)}")

                # Show first answer
                if answers:
                    print(f"📝 Sample answer: {answers[0][:150]}...")

                results[doc_type] = {"success": True, "time": total_time, "answers": len(answers)}
            else:
                print(f"❌ {doc_type} processing failed: {response.status_code}")
                results[doc_type] = {"success": False, "error": response.status_code}

        except Exception as e:
            print(f"❌ {doc_type} processing error: {e}")
            results[doc_type] = {"success": False, "error": str(e)}

    # Summary
    print(f"\n{'='*60}")
    print("📊 DOCUMENT TYPE TEST SUMMARY")
    print(f"{'='*60}")

    for doc_type, result in results.items():
        if result["success"]:
            print(f"✅ {doc_type}: Success ({result['time']:.1f}s, {result['answers']} answers)")
        else:
            print(f"❌ {doc_type}: Failed ({result.get('error', 'Unknown error')})")

    return results


def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 API REQUEST TEST SCRIPT")
    print("=" * 60)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Test health endpoint
    if not test_health_endpoint():
        print("\n❌ Health check failed. Make sure the server is running.")
        return

    # Step 2: Test main endpoint (PDF by default)
    success = test_main_endpoint()

    if success:
        # Step 3: Test both document types
        test_both_document_types()
    else:
        # Step 3: Test schema validation if main test failed
        test_schema_validation()

    print(f"\n🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
