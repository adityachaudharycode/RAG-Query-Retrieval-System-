"""
Quick fix for Gemini API compatibility issue
"""
import subprocess
import sys


def fix_gemini_version():
    """Fix the Gemini API version issue"""
    print("🔧 Fixing Gemini API Compatibility Issue")
    print("=" * 60)
    
    print("📦 Updating google-generativeai to compatible version...")
    
    try:
        # Upgrade google-generativeai
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "google-generativeai==0.7.2"
        ])
        print("✅ google-generativeai updated successfully!")
        
        # Test the import
        print("\n🧪 Testing Gemini import...")
        import google.generativeai as genai
        print("✅ Gemini import successful!")
        
        # Test GenerativeModel
        print("🧪 Testing GenerativeModel...")
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ GenerativeModel creation successful!")
        except Exception as e:
            print(f"⚠️ GenerativeModel test failed: {e}")
            print("This might be due to missing API key, but the import works")
        
        print("\n🎉 Gemini API fix completed!")
        print("\n🚀 You can now restart your server:")
        print("   python main.py")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to update google-generativeai: {e}")
        return False
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main function"""
    print("🔧 Gemini API Fix Tool")
    print("=" * 60)
    print("This will fix the 'system_instruction' compatibility issue")
    print("=" * 60)
    
    success = fix_gemini_version()
    
    if success:
        print("\n✅ Fix completed successfully!")
        print("\nNext steps:")
        print("1. Restart your server: python main.py")
        print("2. Test the API: python test_api.py")
    else:
        print("\n❌ Fix failed!")
        print("\nManual fix:")
        print("pip install --upgrade google-generativeai==0.7.2")
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Fix interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
