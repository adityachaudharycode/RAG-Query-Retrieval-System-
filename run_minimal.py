"""
Minimal startup script using only Gemini (no sentence-transformers)
"""
import os
import sys
import subprocess


def install_minimal_dependencies():
    """Install minimal dependencies"""
    print("📦 Installing minimal dependencies (Gemini-only)...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_minimal.txt"
        ])
        print("✅ Minimal dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_gemini_only_env():
    """Setup environment for Gemini-only mode"""
    print("⚙️ Setting up Gemini-only environment...")
    
    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        print("Creating .env file...")
        env_content = """# Gemini Configuration (ONLY API KEY NEEDED)
GEMINI_API_KEY=your_gemini_api_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_BEARER_TOKEN=87e1f87355284c19bac1880413d4a1e7cb868891939fc1c6d8227ee2c1b89cb0

# Force Gemini-only mode
EMBEDDING_PROVIDER=gemini
GEMINI_EMBEDDING_MODEL=models/embedding-001
GEMINI_MODEL=gemini-1.5-flash

# Vector Database Configuration
VECTOR_DIMENSION=768
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Other settings
MAX_TOKENS=4000
TEMPERATURE=0.1
LOG_LEVEL=INFO
"""
        with open(".env", "w") as f:
            f.write(env_content)
        
        print("✅ Created .env file")
        print("⚠️  IMPORTANT: Edit .env and add your GEMINI_API_KEY!")
    else:
        print("✅ .env file already exists")
    
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    print("✅ Created necessary directories")


def check_gemini_key():
    """Check if Gemini API key is set"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv not found, using system environment")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        print("⚠️ Gemini API key not set!")
        print("   Please edit .env file and add your GEMINI_API_KEY")
        print("   Get it from: https://makersuite.google.com/app/apikey")
        return False
    
    print("✅ Gemini API key configured")
    return True


def test_minimal_setup():
    """Test if minimal setup works"""
    print("🧪 Testing minimal setup...")
    
    try:
        # Test basic imports
        import google.generativeai as genai
        print("✅ google.generativeai - OK")
        
        import faiss
        print("✅ faiss - OK")
        
        import numpy as np
        print("✅ numpy - OK")
        
        # Test Gemini API key
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            genai.configure(api_key=gemini_key)
            # Try to list models to test API key
            try:
                models = list(genai.list_models())
                print("✅ Gemini API connection - OK")
            except Exception as e:
                print(f"⚠️ Gemini API test failed: {e}")
        
        print("🎉 Minimal setup test passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False


def run_server():
    """Run the server"""
    print("🚀 Starting server...")
    try:
        import uvicorn

        print("📍 Server starting at: http://localhost:8000")
        print("📖 API docs at: http://localhost:8000/docs")
        print("🔍 Health check at: http://localhost:8000/health")
        print("=" * 60)

        uvicorn.run(
            "main:app",  # Use import string instead of app object
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Failed to start server: {e}")
        print("Make sure dependencies are installed")
    except Exception as e:
        print(f"❌ Server error: {e}")


def main():
    """Main function"""
    print("🚀 Gemini-Only Minimal Setup")
    print("=" * 60)
    print("This script installs minimal dependencies and uses only Gemini AI")
    print("(No sentence-transformers to avoid compatibility issues)")
    print("=" * 60)
    
    # Step 1: Install minimal dependencies
    if not install_minimal_dependencies():
        print("❌ Setup failed: Could not install dependencies")
        return
    
    # Step 2: Setup environment
    setup_gemini_only_env()
    
    # Step 3: Check API key
    api_key_ok = check_gemini_key()
    if not api_key_ok:
        print("\n⚠️ Please set up your Gemini API key before continuing")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Please add your API key to .env and try again")
            return
    
    # Step 4: Test setup
    if not test_minimal_setup():
        print("⚠️ Some tests failed, but you can still try running the server")
    
    print("\n" + "=" * 60)
    print("🎯 Minimal setup complete!")
    print("=" * 60)
    
    # Step 5: Run server
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
