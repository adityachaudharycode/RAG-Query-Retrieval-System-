"""
Test script specifically for Google Drive DOCX files
"""
import requests
import json
import time
from datetime import datetime


# Configuration
API_BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "87e1f87355284c19bac1880413d4a1e7cb868891939fc1c6d8227ee2c1b89cb0"

# Google Drive DOCX URL (your example)
GOOGLE_DRIVE_DOCX_URL = "https://drive.google.com/uc?export=download&id=1l9C5DmyxNgNdXGkhVkJ53V491tat1H1x"

# Test questions for DOCX document
TEST_QUESTIONS = [
    "What is the main topic of this document?",
    "What are the key points mentioned?",
    "What information is provided in the document?"
]


def test_google_drive_docx():
    """Test Google Drive DOCX processing"""
    print("=" * 70)
    print("📄 GOOGLE DRIVE DOCX TEST")
    print("=" * 70)
    print(f"🔗 Testing URL: {GOOGLE_DRIVE_DOCX_URL}")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Prepare request
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "documents": GOOGLE_DRIVE_DOCX_URL,
        "questions": TEST_QUESTIONS
    }
    
    print(f"\n📤 Request payload:")
    print(f"Documents: {payload['documents']}")
    print(f"Questions: {len(payload['questions'])} questions")
    
    # Make request
    start_time = time.time()
    try:
        print(f"\n🚀 Sending request to API...")
        response = requests.post(
            f"{API_BASE_URL}/hackrx/run",
            headers=headers,
            json=payload,
            timeout=120  # 2 minute timeout
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n📥 Response received:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {total_time:.1f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            answers = result.get("answers", [])
            
            print("✅ SUCCESS: Google Drive DOCX processed successfully!")
            print(f"📊 Received {len(answers)} answers")
            
            # Display answers
            print(f"\n📝 Answers from DOCX document:")
            for i, (question, answer) in enumerate(zip(TEST_QUESTIONS, answers), 1):
                print(f"\n❓ Q{i}: {question}")
                print(f"💬 A{i}: {answer[:300]}{'...' if len(answer) > 300 else ''}")
            
            # Performance assessment
            print(f"\n⚡ Performance:")
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
            print("❌ VALIDATION ERROR (422):")
            try:
                error_detail = response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Raw error: {response.text}")
            return False
            
        elif response.status_code == 500:
            print("❌ SERVER ERROR (500):")
            print("This might be due to:")
            print("- Document processing issues")
            print("- Google Drive access problems")
            print("- File format detection issues")
            try:
                error_detail = response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Raw error: {response.text}")
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


def test_document_download():
    """Test direct document download to verify accessibility"""
    print("\n🔍 Testing direct document download...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(GOOGLE_DRIVE_DOCX_URL, headers=headers, timeout=30)
        
        print(f"Download Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        # Check file signature
        if response.content:
            if response.content.startswith(b'PK'):
                print("✅ File signature: DOCX/ZIP format detected")
            elif response.content.startswith(b'%PDF'):
                print("📄 File signature: PDF format detected")
            elif response.content.startswith(b'\xd0\xcf\x11\xe0'):
                print("📄 File signature: DOC format detected")
            else:
                print(f"❓ Unknown file signature: {response.content[:10]}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Download test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 GOOGLE DRIVE DOCX PROCESSING TEST")
    
    # Test 1: Direct download
    if not test_document_download():
        print("\n❌ Document download failed. Check the Google Drive URL.")
        return
    
    # Test 2: API processing
    success = test_google_drive_docx()
    
    print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("🎉 Google Drive DOCX processing is working!")
    else:
        print("❌ Google Drive DOCX processing needs attention.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
