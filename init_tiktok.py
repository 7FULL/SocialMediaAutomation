#!/usr/bin/env python3
"""
TikTok Integration Initialization Script
This script performs all necessary setup for TikTok functionality
"""

import os
import sys
import subprocess
import json

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing TikTok requirements...")
    
    try:
        # Install core requirements
        requirements = [
            "customtkinter>=5.0.0",
            "moviepy>=1.0.3", 
            "requests>=2.28.0",
            "Pillow>=9.0.0",
            "python-dateutil>=2.8.0"
        ]
        
        for req in requirements:
            print(f"Installing {req}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", req
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {req} installed successfully")
            else:
                print(f"⚠️ Warning installing {req}: {result.stderr}")
        
        print("✅ Basic requirements installed")
        return True
        
    except Exception as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_directory_structure():
    """Create necessary directory structure"""
    print("\n📁 Creating directory structure...")
    
    directories = [
        "tiktok_automation",
        "tiktok_automation/account_clips", 
        "tiktok_automation/account_tokens",
        "tiktok_automation/logs",
        "youtube_automation",
        "youtube_automation/account_clips",
        "youtube_automation/account_tokens", 
        "youtube_automation/logs",
        "config"
    ]
    
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"✅ Created: {directory}")
            else:
                print(f"📁 Exists: {directory}")
        except Exception as e:
            print(f"❌ Error creating {directory}: {e}")
    
    return True

def create_config_files():
    """Create initial configuration files"""
    print("\n⚙️ Creating configuration files...")
    
    # TikTok config template
    tiktok_config = {
        "client_key": "YOUR_TIKTOK_CLIENT_KEY",
        "client_secret": "YOUR_TIKTOK_CLIENT_SECRET",
        "redirect_uri": "http://localhost:8080/callback",
        "environment": "sandbox",
        "instructions": {
            "step_1": "Go to https://developers.tiktok.com/",
            "step_2": "Create a new app and get your Client Key and Client Secret",
            "step_3": "Replace the values above with your real credentials",
            "step_4": "Set redirect_uri in your TikTok app settings",
            "step_5": "Change environment to 'production' when ready for real uploads"
        }
    }
    
    config_file = "tiktok_automation/tiktok_config.json"
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(tiktok_config, f, indent=4)
        print(f"✅ Created: {config_file}")
    else:
        print(f"📄 Exists: {config_file}")
    
    # Main config template
    main_config = {
        "YouTube": {
            "auto_upload": False,
            "accounts": {}
        },
        "TikTok": {
            "auto_upload": False,
            "accounts": {}
        },
        "Instagram": {
            "auto_upload": False,
            "accounts": {}
        },
        "Twitter": {
            "auto_upload": False,
            "accounts": {}
        }
    }
    
    main_config_file = "config/config.json"
    if not os.path.exists(main_config_file):
        with open(main_config_file, 'w') as f:
            json.dump(main_config, f, indent=4)
        print(f"✅ Created: {main_config_file}")
    else:
        print(f"📄 Exists: {main_config_file}")
    
    return True

def test_imports():
    """Test if all imports work correctly"""
    print("\n🧪 Testing imports...")
    
    import_tests = [
        ("customtkinter", "CustomTkinter GUI library"),
        ("requests", "HTTP requests library"),
        ("json", "JSON handling"),
        ("threading", "Threading support"),
        ("tkinter", "Tkinter GUI"),
        ("datetime", "Date/time handling"),
    ]
    
    all_good = True
    
    for module, description in import_tests:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except ImportError as e:
            print(f"❌ {module} - {description}: {e}")
            all_good = False
    
    # Test core modules
    try:
        from core.tiktok_automation_enhanced import TikTokAutomation
        print("✅ TikTok Enhanced Automation")
    except ImportError:
        try:
            from core.tiktok_automation import TikTokAutomation
            print("⚠️ TikTok Basic Automation (Enhanced not available)")
        except ImportError as e:
            print(f"❌ TikTok Automation: {e}")
            all_good = False
    
    try:
        from gui.main_panel import MainPanel
        print("✅ Main GUI Panel")
    except ImportError as e:
        print(f"❌ Main GUI Panel: {e}")
        all_good = False
    
    return all_good

def test_tiktok_functionality():
    """Test basic TikTok functionality"""
    print("\n🎵 Testing TikTok functionality...")
    
    try:
        # Test simulation authentication
        from core.tiktok_automation_enhanced import TikTokAutomation
        
        test_account = "test_init_account"
        success = TikTokAutomation.authenticate_tiktok_account(test_account, use_real_api=False)
        
        if success:
            print("✅ TikTok simulation authentication works")
            
            # Test account status
            tta = TikTokAutomation(account_name=test_account)
            status = tta.get_account_status()
            print(f"✅ Account status check works: {status['type']}")
            
            # Clean up test
            token_file = f"tiktok_automation/account_tokens/token_{test_account}.json"
            if os.path.exists(token_file):
                os.remove(token_file)
            
            return True
        else:
            print("❌ TikTok simulation authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ TikTok functionality test failed: {e}")
        return False

def show_next_steps():
    """Show what to do next"""
    print("\n🎯 Next Steps:")
    print("=" * 50)
    
    print("\n1. 🚀 Start the application:")
    print("   python main.py")
    
    print("\n2. 🎵 For real TikTok uploads:")
    print("   python setup_tiktok_api.py")
    print("   - Get TikTok Developer credentials")
    print("   - Configure API settings")
    print("   - Test authentication")
    
    print("\n3. 📱 Using the GUI:")
    print("   - Go to TikTok tab")
    print("   - Add account (starts in simulation mode)")
    print("   - Generate clips from video files")
    print("   - Upload clips (simulated by default)")
    
    print("\n4. 🔧 For real API:")
    print("   - Complete TikTok Developer setup")
    print("   - Update tiktok_automation/tiktok_config.json")
    print("   - Re-authenticate accounts with real API")
    
    print("\n5. 📚 Documentation:")
    print("   - Read: tiktok_automation/README.md")
    print("   - Examples and troubleshooting included")

def main():
    """Main initialization function"""
    print("🎵 TikTok Integration Initialization")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        return False
    
    # Create directories
    if not create_directory_structure():
        print("❌ Failed to create directories")
        return False
    
    # Create configs
    if not create_config_files():
        print("❌ Failed to create config files")
        return False
    
    # Test imports
    if not test_imports():
        print("⚠️ Some imports failed - check requirements")
    
    # Test TikTok functionality
    if not test_tiktok_functionality():
        print("⚠️ TikTok functionality test failed")
    
    print("\n🎉 TikTok Integration Setup Complete!")
    print("=" * 50)
    
    show_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup completed with errors")
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")