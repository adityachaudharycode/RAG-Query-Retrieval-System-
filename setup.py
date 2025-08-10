"""
Setup script for the LLM-Powered Query-Retrieval System
"""
import os
import sys
import subprocess
from pathlib import Path


def main():
    """Install dependencies and setup the project"""
    print("🚀 Setting up LLM-Powered Query-Retrieval System...")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    # Create directories
    print("📁 Creating directories...")
    directories = ["data", "logs", "temp"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   Created: {directory}/")
    
    # Setup environment file
    print("⚙️ Setting up environment...")
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as f:
                content = f.read()
            with open(".env", "w") as f:
                f.write(content)
            print("   Created .env file from template")
        else:
            print("   ⚠️ No .env.example found")
    else:
        print("   .env file already exists")
    
    print("\n✅ Setup complete!")
    print("\n📝 Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python main.py")
    print("3. Or run: python run.py (for guided startup)")
    print("\n🌐 The API will be available at: http://localhost:8000")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
