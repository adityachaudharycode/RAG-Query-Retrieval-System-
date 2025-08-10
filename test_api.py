"""
Test script for the LLM-Powered Query-Retrieval System API
"""
import asyncio
import json
import requests
from typing import List, Dict, Any


class APITester:
    """Test client for the API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", token: str = None):
        self.base_url = base_url
        self.token = token or "87e1f87355284c19bac1880413d4a1e7cb868891939fc1c6d8227ee2c1b89cb0"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_health_check(self):
        """Test the health check endpoint"""
        print("Testing health check...")
        try:
            response = requests.get(f"{self.base_url}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def test_query_processing(self):
        """Test the main query processing endpoint"""
        print("\nTesting query processing...")
        
        # Sample request data
        test_data = {
            "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "questions": [
                "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
                "What is the waiting period for pre-existing diseases (PED) to be covered?",
                "Does this policy cover maternity expenses, and what are the conditions?",
                "What is the waiting period for cataract surgery?",
                "Are the medical expenses for an organ donor covered under this policy?"
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/hackrx/run",
                headers=self.headers,
                json=test_data,
                timeout=120  # 2 minutes timeout
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Number of answers: {len(result.get('answers', []))}")
                
                for i, answer in enumerate(result.get('answers', []), 1):
                    print(f"\nQuestion {i}: {test_data['questions'][i-1]}")
                    print(f"Answer {i}: {answer}")
                    print("-" * 80)
                
                return True
            else:
                print(f"Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"Query processing test failed: {e}")
            return False
    
    def test_simple_query(self):
        """Test with a simple single question"""
        print("\nTesting simple query...")
        
        simple_data = {
            "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "questions": [
                "What is the grace period for premium payment?"
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/hackrx/run",
                headers=self.headers,
                json=simple_data,
                timeout=60
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Answer: {result['answers'][0]}")
                return True
            else:
                print(f"Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"Simple query test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 80)
        print("LLM-Powered Query-Retrieval System API Tests")
        print("=" * 80)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Simple Query", self.test_simple_query),
            ("Full Query Processing", self.test_query_processing)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            results[test_name] = test_func()
        
        print(f"\n{'='*80}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*80}")
        
        for test_name, passed in results.items():
            status = "PASSED" if passed else "FAILED"
            print(f"{test_name}: {status}")
        
        total_passed = sum(results.values())
        total_tests = len(results)
        print(f"\nOverall: {total_passed}/{total_tests} tests passed")
        
        return total_passed == total_tests


if __name__ == "__main__":
    # Create tester instance
    tester = APITester()
    
    # Run all tests
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed. Check the logs for details.")
