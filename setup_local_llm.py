"""
Setup script for local LLM using Ollama
"""
import os
import sys
import subprocess
import platform
import requests
import time
from pathlib import Path


def download_ollama():
    """Download and install Ollama"""
    print("🔽 Downloading Ollama...")
    
    system = platform.system().lower()
    
    if system == "windows":
        print("📥 Downloading Ollama for Windows...")
        url = "https://ollama.com/download/OllamaSetup.exe"
        filename = "OllamaSetup.exe"
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Downloaded {filename}")
            print("🚀 Please run OllamaSetup.exe to install Ollama")
            print("⚠️  After installation, restart this script")
            return False
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    elif system == "linux":
        print("📥 Installing Ollama for Linux...")
        try:
            subprocess.run(["curl", "-fsSL", "https://ollama.com/install.sh"], 
                         stdout=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    elif system == "darwin":  # macOS
        print("📥 Please install Ollama manually from https://ollama.com/download")
        print("Or use: brew install ollama")
        return False
    
    return False


def check_ollama_installed():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama installed: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Ollama not found")
    return False


def start_ollama_service():
    """Start Ollama service"""
    print("🚀 Starting Ollama service...")
    
    try:
        # Try to start Ollama service
        if platform.system().lower() == "windows":
            subprocess.Popen(["ollama", "serve"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(["ollama", "serve"])
        
        # Wait for service to start
        time.sleep(5)
        
        # Check if service is running
        response = requests.get("http://localhost:11434/api/version", timeout=10)
        if response.status_code == 200:
            print("✅ Ollama service started successfully")
            return True
    except Exception as e:
        print(f"⚠️  Ollama service start: {e}")
    
    return False


def download_models():
    """Download required models"""
    models_to_download = [
        {
            "name": "llama3.2:3b",
            "description": "Llama 3.2 3B - Fast and efficient for text generation",
            "size": "~2GB"
        },
        {
            "name": "nomic-embed-text",
            "description": "Nomic Embed - Specialized for embeddings",
            "size": "~274MB"
        },
        {
            "name": "llama3.2:1b", 
            "description": "Llama 3.2 1B - Ultra-fast lightweight model",
            "size": "~1.3GB"
        }
    ]
    
    print("\n📦 Available models to download:")
    for i, model in enumerate(models_to_download, 1):
        print(f"{i}. {model['name']} - {model['description']} ({model['size']})")
    
    print("\n🔽 Downloading recommended models...")
    
    downloaded_models = []
    
    for model in models_to_download[:2]:  # Download first 2 models
        print(f"\n📥 Downloading {model['name']}...")
        try:
            result = subprocess.run(
                ["ollama", "pull", model["name"]], 
                capture_output=True, text=True, timeout=600  # 10 minute timeout
            )
                
            if result.returncode == 0:
                print(f"✅ {model['name']} downloaded successfully")
                downloaded_models.append(model['name'])
            else:
                print(f"❌ Failed to download {model['name']}: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Download timeout for {model['name']}")
        except Exception as e:
            print(f"❌ Error downloading {model['name']}: {e}")
    
    return downloaded_models


def test_models(models):
    """Test downloaded models"""
    print("\n🧪 Testing downloaded models...")
    
    working_models = {"embedding": None, "text": None}
    
    # Test embedding model
    if "nomic-embed-text" in models:
        print("🔍 Testing embedding model...")
        try:
            response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": "What is the grace period for premium payment?"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "embedding" in result:
                    print("✅ Embedding model working")
                    working_models["embedding"] = "nomic-embed-text"
        except Exception as e:
            print(f"❌ Embedding model test failed: {e}")
    
    # Test text generation models
    text_models = ["llama3.2:3b", "llama3.2:1b"]
    for model in text_models:
        if model in models:
            print(f"💬 Testing {model}...")
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model,
                        "prompt": "What is insurance?",
                        "stream": False
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "response" in result and result["response"]:
                        print(f"✅ {model} working")
                        working_models["text"] = model
                        break  # Use first working model
            except Exception as e:
                print(f"❌ {model} test failed: {e}")
    
    return working_models


def create_local_config():
    """Create configuration for local LLM"""
    config = {
        "ollama_base_url": "http://localhost:11434",
        "embedding_model": "nomic-embed-text",
        "text_model": "llama3.2:3b",
        "fallback_text_model": "llama3.2:1b"
    }
    
    # Save to config file
    import json
    with open("local_llm_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Local LLM configuration saved")
    return config


def main():
    """Main setup function"""
    print("🏠 LOCAL LLM SETUP")
    print("=" * 50)
    print("This will set up Ollama with local models for:")
    print("• Text embeddings (nomic-embed-text)")
    print("• Text generation (llama3.2)")
    print("• Zero API costs")
    print("• No rate limits")
    print("=" * 50)
    
    # Step 1: Check if Ollama is installed
    if not check_ollama_installed():
        print("\n🔽 Ollama not found. Downloading...")
        if not download_ollama():
            print("❌ Please install Ollama manually from https://ollama.com/download")
            return
        
        if not check_ollama_installed():
            print("❌ Please install Ollama and restart this script")
            return
    
    # Step 2: Start Ollama service
    if not start_ollama_service():
        print("❌ Could not start Ollama service")
        print("💡 Try running 'ollama serve' manually in another terminal")
        return
    
    # Step 3: Download models
    downloaded_models = download_models()
    
    if not downloaded_models:
        print("❌ No models downloaded successfully")
        return
    
    # Step 4: Test models
    working_models = test_models(downloaded_models)
    
    if not working_models["embedding"] or not working_models["text"]:
        print("❌ Models not working properly")
        return
    
    # Step 5: Create configuration
    config = create_local_config()
    
    print("\n🎉 LOCAL LLM SETUP COMPLETE!")
    print("=" * 50)
    print(f"✅ Embedding model: {working_models['embedding']}")
    print(f"✅ Text model: {working_models['text']}")
    print("✅ Ollama service running on http://localhost:11434")
    print("✅ Configuration saved to local_llm_config.json")
    print("\n🚀 You can now use local LLM with zero API costs!")
    print("💡 Run 'python test_local_llm.py' to test the integration")


if __name__ == "__main__":
    main()
