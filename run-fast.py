"""
Fast startup script for the LLM-Powered Query-Retrieval System
Optimized for 30-second startup time
"""
import os
import sys
import subprocess
import time
from datetime import datetime


def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🚀 LLM-Powered Query-Retrieval System (FAST MODE)")
    print("=" * 60)
    print("⚡ Optimized for 30-second startup")
    print("🎯 Using Gemini embeddings only")
    print("📦 Lightweight dependencies")
    print("=" * 60)


def install_fast_dependencies():
    """Install only essential dependencies for fast startup"""
    print("📦 Installing fast dependencies...")
    start_time = time.time()
    
    try:
        # Use the optimized requirements file
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements-fast.txt", "--quiet"
        ])
        
        install_time = time.time() - start_time
        print(f"✅ Dependencies installed in {install_time:.1f} seconds")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_environment():
    """Quick environment setup"""
    print("🔧 Setting up environment...")
    
    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as template:
                content = template.read()
            with open(".env", "w") as env_file:
                env_file.write(content)
            print("📝 Created .env file from template")
        else:
            # Create minimal .env file
            with open(".env", "w") as env_file:
                env_file.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
                env_file.write("API_BEARER_TOKEN=your_bearer_token_here\n")
            print("📝 Created minimal .env file")
    
    # Create necessary directories
    for dir_name in ["data", "logs", "temp"]:
        os.makedirs(dir_name, exist_ok=True)
    
    print("✅ Environment ready")


def check_api_key():
    """Quick API key check"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key or gemini_key == "your_gemini_api_key_here":
            print("⚠️  WARNING: Gemini API key not set!")
            print("   Please set GEMINI_API_KEY in your .env file")
            return False
        
        print("✅ API key configured")
        return True
    except ImportError:
        print("⚠️  python-dotenv not installed, skipping API key check")
        return True


def run_server():
    """Start the FastAPI server"""
    print("🚀 Starting server...")
    try:
        import uvicorn
        
        print("📍 Server starting at: http://localhost:8000")
        print("📖 API docs at: http://localhost:8000/docs")
        print("🔍 Health check at: http://localhost:8000/health")
        print("=" * 60)
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload for faster startup
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Failed to start server: {e}")
    except Exception as e:
        print(f"❌ Server error: {e}")


def main():
    """Main fast startup function"""
    start_time = time.time()
    print_banner()
    
    # Step 1: Install dependencies
    if not install_fast_dependencies():
        print("❌ Startup failed: Could not install dependencies")
        return
    
    # Step 2: Setup environment
    setup_environment()
    
    # Step 3: Check API key
    api_key_ok = check_api_key()
    if not api_key_ok:
        print("\n⚠️  You can still run the system, but it won't work without a valid API key")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Please set up your API key and try again")
            return
    
    total_time = time.time() - start_time
    print(f"\n🎯 System ready in {total_time:.1f} seconds!")
    print("=" * 60)
    
    # Step 4: Run the server
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
