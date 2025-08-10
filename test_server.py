"""
Simple test to verify the server starts correctly
"""
import os
import sys
import time
import requests
import subprocess
from threading import Thread


def test_server_startup():
    """Test if the server starts without errors"""
    print("🧪 Testing Server Startup")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("Please create .env file with GEMINI_API_KEY")
        return False
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv not installed")
    
    # Check API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        print("⚠️ GEMINI_API_KEY not set, server may fail")
    else:
        print("✅ GEMINI_API_KEY found")
    
    # Test imports
    print("\n🔍 Testing imports...")
    try:
        from main import app
        print("✅ FastAPI app import - OK")
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")
        return False
    
    try:
        import google.generativeai as genai
        print("✅ Gemini import - OK")
    except Exception as e:
        print(f"❌ Gemini import failed: {e}")
        return False
    
    try:
        import faiss
        print("✅ FAISS import - OK")
    except Exception as e:
        print(f"❌ FAISS import failed: {e}")
        return False
    
    print("\n🚀 Starting server test...")
    
    # Start server in background
    server_process = None
    try:
        server_process = subprocess.Popen([
            sys.executable, "-c", 
            "import uvicorn; from main import app; uvicorn.run(app, host='127.0.0.1', port=8001, log_level='error')"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Test health endpoint
        try:
            response = requests.get("http://127.0.0.1:8001/health", timeout=10)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                print(f"   Health check: {response.json()}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to server: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    finally:
        # Clean up
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()


def main():
    """Main test function"""
    print("🔧 Server Startup Test")
    print("=" * 60)
    
    success = test_server_startup()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Server startup test PASSED!")
        print("\n✅ Your server should start correctly with:")
        print("   python main.py")
        print("   or")
        print("   python run.py")
    else:
        print("❌ Server startup test FAILED!")
        print("\n🔧 Try these fixes:")
        print("1. Run: python fix_dependencies.py")
        print("2. Or run: python run_minimal.py")
        print("3. Check your .env file has GEMINI_API_KEY")
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
