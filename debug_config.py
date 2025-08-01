#!/usr/bin/env python3
"""
Debug script to check config data for Instagram credentials
"""

import json
import os

def check_config():
    """Check config data for Instagram credentials"""
    
    config_path = "web_app/backend/config/config.json"
    
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("📋 Current Config Structure:")
        print("=" * 50)
        
        if "Instagram" in config:
            instagram_config = config["Instagram"]
            print(f"Instagram platform exists: ✅")
            print(f"Auto upload enabled: {instagram_config.get('auto_upload', False)}")
            
            accounts = instagram_config.get("accounts", {})
            print(f"Number of accounts: {len(accounts)}")
            
            for account_name, account_data in accounts.items():
                print(f"\n📱 Account: {account_name}")
                print(f"   Active: {account_data.get('active', False)}")
                print(f"   Authenticated: {account_data.get('authenticated', False)}")
                print(f"   Clip folder: {account_data.get('clip_folder', 'Not set')}")
                
                # Check for credentials
                has_username = 'instagram_username' in account_data
                has_password = 'instagram_password' in account_data
                
                print(f"   Has username: {'✅' if has_username else '❌'}")
                print(f"   Has password: {'✅' if has_password else '❌'}")
                
                if has_username:
                    print(f"   Username: {account_data['instagram_username']}")
                else:
                    print("   ⚠️ USERNAME MISSING!")
                
                if has_password:
                    print(f"   Password: {'*' * len(account_data['instagram_password'])}")
                else:
                    print("   ⚠️ PASSWORD MISSING!")
        else:
            print("❌ Instagram platform not found in config")
        
        print("\n" + "=" * 50)
        print("Full config structure:")
        print(json.dumps(config, indent=2))
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")

if __name__ == "__main__":
    check_config()