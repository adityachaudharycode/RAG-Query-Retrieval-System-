"""
Startup script for the LLM-Powered Query-Retrieval System
"""
import os
import sys
import subprocess


def install_dependencies():
    """Install required dependencies with optimization"""
    print("Installing core dependencies for fast startup...")

    try:
        # Use the fast requirements file
        if os.path.exists("requirements-fast.txt"):
            print("Using optimized requirements file...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements-fast.txt"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Fallback to original requirements
            print("Fast requirements not found, using standard requirements...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("✅ Dependencies installed successfully")
        print("ℹ️  Using optimized setup for faster startup (Gemini embeddings only)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_environment():
    """Setup environment variables"""
    print("Setting up environment...")
    
    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        print("Creating .env file from template...")
        with open(".env.example", "r") as template:
            content = template.read()
        
        with open(".env", "w") as env_file:
            env_file.write(content)
        
        print("⚠️  Please update the .env file with your actual API keys!")
        print("   - Set your OPENAI_API_KEY")
        print("   - Verify other configuration settings")
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    print("✅ Environment setup complete")


def check_api_key():
    """Check if Gemini API key is set"""
    from dotenv import load_dotenv
    load_dotenv()

    gemini_key = os.getenv("GEMINI_API_KEY")

    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        print("⚠️  WARNING: Gemini API key not set!")
        print("   Please set GEMINI_API_KEY in your .env file")
        print("   This is required for both embeddings and LLM responses")
        return False

    print("✅ Gemini API key is configured")
    return True


def run_server():
    """Run the FastAPI server"""
    print("Starting the server...")
    try:
        import uvicorn

        uvicorn.run(
            "main:app",  # Use import string instead of app object
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Failed to start server: {e}")
        print("Make sure all dependencies are installed")
    except Exception as e:
        print(f"❌ Server error: {e}")


def main():
    """Main startup function"""
    print("=" * 60)
    print("🚀 LLM-Powered Query-Retrieval System Startup")
    print("=" * 60)
    
    # Step 1: Install dependencies
    if not install_dependencies():
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
    
    print("\n" + "=" * 60)
    print("🎯 System ready! Starting server...")
    print("=" * 60)
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
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
