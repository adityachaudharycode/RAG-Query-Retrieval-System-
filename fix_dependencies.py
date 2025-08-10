"""
Fix script for dependency issues
"""
import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def fix_huggingface_issue():
    """Fix the huggingface_hub compatibility issue"""
    print("🚀 Fixing HuggingFace Hub Compatibility Issue")
    print("=" * 60)
    
    # Step 1: Uninstall problematic packages
    commands = [
        ("pip uninstall -y sentence-transformers huggingface_hub transformers torch", 
         "Uninstalling conflicting packages"),
        
        # Step 2: Install specific compatible versions
        ("pip install huggingface_hub==0.20.3", 
         "Installing compatible huggingface_hub"),
        
        ("pip install transformers==4.36.2", 
         "Installing compatible transformers"),
        
        ("pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu", 
         "Installing PyTorch CPU version"),
        
        ("pip install sentence-transformers==2.7.0", 
         "Installing compatible sentence-transformers"),
        
        # Step 3: Install other requirements
        ("pip install -r requirements.txt", 
         "Installing remaining requirements"),
    ]
    
    success_count = 0
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"📊 RESULTS: {success_count}/{len(commands)} operations successful")
    
    if success_count == len(commands):
        print("🎉 All dependency issues fixed!")
        print("\n🚀 Try running the server again:")
        print("   python main.py")
        print("   or")
        print("   python run.py")
    else:
        print("⚠️ Some operations failed. Try manual installation:")
        print("\n📝 Manual steps:")
        print("1. pip uninstall sentence-transformers huggingface_hub transformers torch")
        print("2. pip install huggingface_hub==0.20.3")
        print("3. pip install transformers==4.36.2")
        print("4. pip install torch==2.1.2")
        print("5. pip install sentence-transformers==2.7.0")
        print("6. pip install -r requirements.txt")
    
    return success_count == len(commands)


def test_imports():
    """Test if the problematic imports work"""
    print("\n🧪 Testing imports...")
    
    try:
        from huggingface_hub import cached_download
        print("✅ huggingface_hub.cached_download - OK")
    except ImportError as e:
        print(f"❌ huggingface_hub.cached_download - FAILED: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence_transformers - OK")
    except ImportError as e:
        print(f"❌ sentence_transformers - FAILED: {e}")
        return False
    
    try:
        import google.generativeai as genai
        print("✅ google.generativeai - OK")
    except ImportError as e:
        print(f"❌ google.generativeai - FAILED: {e}")
        return False
    
    print("🎉 All imports successful!")
    return True


def main():
    """Main function"""
    print("🔧 Dependency Fix Tool")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        print("Please run this script from the project root directory.")
        return
    
    # Test current imports
    print("🔍 Checking current state...")
    if test_imports():
        print("✅ All dependencies are already working!")
        return
    
    print("\n🔧 Dependencies need fixing...")
    
    # Ask user confirmation
    response = input("\nProceed with automatic fix? (y/N): ")
    if response.lower() != 'y':
        print("👋 Fix cancelled by user")
        return
    
    # Fix the issues
    success = fix_huggingface_issue()
    
    if success:
        print("\n🧪 Final test...")
        test_imports()


if __name__ == "__main__":
    main()
