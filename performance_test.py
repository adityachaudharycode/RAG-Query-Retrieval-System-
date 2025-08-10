"""
Performance test script to compare optimized vs original performance
"""
import asyncio
import time
import requests
import json
from datetime import datetime


# Test configuration
API_BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "87e1f87355284c19bac1880413d4a1e7cb868891939fc1c6d8227ee2c1b89cb0"  # From .env.example

# Sample test data
TEST_DOCUMENT_URL = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"

TEST_QUESTIONS = [
    "What is the grace period for premium payment?",
    "What is the waiting period for cataract surgery?",
    "What is the waiting period for pre-existing diseases?"
]


def print_performance_banner():
    """Print performance test banner"""
    print("=" * 70)
    print("⚡ PERFORMANCE TEST - LLM Query-Retrieval System")
    print("=" * 70)
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📄 Document: Policy PDF")
    print(f"❓ Questions: {len(TEST_QUESTIONS)}")
    print("=" * 70)


def test_api_request():
    """Test the optimized API performance"""
    print("🚀 Testing optimized API performance...")
    
    # Prepare request
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "documents": TEST_DOCUMENT_URL,
        "questions": TEST_QUESTIONS
    }
    
    # Measure performance
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
        
        if response.status_code == 200:
            result = response.json()
            answers = result.get("answers", [])
            
            print(f"✅ Request completed successfully!")
            print(f"⏱️  Total time: {total_time:.1f} seconds")
            print(f"📊 Answers received: {len(answers)}")
            print(f"⚡ Average time per question: {total_time/len(TEST_QUESTIONS):.1f} seconds")
            
            # Performance assessment
            if total_time <= 30:
                print("🎯 EXCELLENT: Under 30 seconds!")
            elif total_time <= 60:
                print("✅ GOOD: Under 1 minute")
            elif total_time <= 120:
                print("⚠️  ACCEPTABLE: Under 2 minutes")
            else:
                print("❌ SLOW: Over 2 minutes")
            
            return total_time, answers
            
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"Error: {response.text}")
            return None, None
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (over 2 minutes)")
        return None, None
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return None, None


def check_server_health():
    """Check if the server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy and ready")
            return True
        else:
            print(f"⚠️  Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print("💡 Make sure the server is running with: python run-fast.py")
        return False


def display_performance_summary(total_time, answers):
    """Display performance summary"""
    print("\n" + "=" * 70)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 70)
    
    if total_time and answers:
        print(f"⏱️  Total execution time: {total_time:.1f} seconds")
        print(f"❓ Questions processed: {len(answers)}")
        print(f"⚡ Average per question: {total_time/len(answers):.1f} seconds")
        
        # Performance benchmarks
        print("\n📈 Performance Benchmarks:")
        print(f"   🎯 Target (30s):     {'✅ ACHIEVED' if total_time <= 30 else '❌ MISSED'}")
        print(f"   ✅ Good (60s):       {'✅ ACHIEVED' if total_time <= 60 else '❌ MISSED'}")
        print(f"   ⚠️  Acceptable (120s): {'✅ ACHIEVED' if total_time <= 120 else '❌ MISSED'}")
        
        # Optimization impact
        original_time = 300  # 5 minutes (original performance)
        improvement = ((original_time - total_time) / original_time) * 100
        print(f"\n🚀 Performance Improvement:")
        print(f"   Original time: ~{original_time} seconds")
        print(f"   Optimized time: {total_time:.1f} seconds")
        print(f"   Improvement: {improvement:.1f}% faster")
        
        # Sample answers
        print(f"\n📝 Sample Answers:")
        for i, answer in enumerate(answers[:2], 1):
            print(f"   Q{i}: {answer[:100]}...")
    else:
        print("❌ No performance data available")
    
    print("=" * 70)


def main():
    """Main performance test function"""
    print_performance_banner()
    
    # Check server health
    if not check_server_health():
        return
    
    print("\n🔄 Starting performance test...")
    
    # Run the performance test
    total_time, answers = test_api_request()
    
    # Display results
    display_performance_summary(total_time, answers)
    
    print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
