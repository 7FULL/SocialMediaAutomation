# 🎵 TikTok API Integration Guide

This guide explains how to set up and use real TikTok API integration for video uploads.

## 📋 Prerequisites

1. **TikTok for Developers Account**
   - Go to [TikTok for Developers](https://developers.tiktok.com/)
   - Create a developer account
   - Create a new app

2. **Required Information**
   - Client Key (App ID)
   - Client Secret
   - Redirect URI: `http://localhost:8080/callback`

## 🚀 Quick Setup

### 1. Run Setup Script
```bash
python setup_tiktok_api.py
```

### 2. Configure API Credentials
Edit `tiktok_automation/tiktok_config.json`:
```json
{
    "client_key": "your_actual_client_key_here",
    "client_secret": "your_actual_client_secret_here",
    "redirect_uri": "http://localhost:8080/callback",
    "environment": "sandbox"
}
```

### 3. Test Configuration
```bash
python setup_tiktok_api.py
# Choose option 3: Test configuration
```

## 📱 TikTok App Setup

### Step 1: Create App
1. Go to [TikTok for Developers](https://developers.tiktok.com/)
2. Click "Manage apps" → "Create an app"
3. Fill in app details:
   - **App name**: Your app name
   - **App description**: Description of your automation tool
   - **Category**: Developer Tools / Utilities

### Step 2: Configure Permissions
Request these scopes:
- `user.info.basic` - Basic user information
- `video.upload` - Upload videos
- `video.publish` - Publish videos

### Step 3: Set Redirect URI
In your app settings, add:
```
http://localhost:8080/callback
```

### Step 4: Get Credentials
- **Client Key**: Found in app dashboard
- **Client Secret**: Found in app dashboard (keep this secret!)

## 🔐 Authentication Flow

### Simulation Mode (Default)
```python
from core.tiktok_automation_enhanced import TikTokAutomation

# This works without real API credentials
TikTokAutomation.authenticate_tiktok_account("my_account")
```

### Real API Mode
```python
# Requires proper configuration
TikTokAutomation.authenticate_tiktok_account("my_account", use_real_api=True)
```

The real API authentication:
1. Opens your browser
2. Redirects to TikTok OAuth
3. You log in and authorize
4. Returns with access tokens
5. Tokens are saved for future use

## 📤 Upload Process

### Basic Upload (Simulation)
```python
from core.tiktok_automation_enhanced import TikTokAutomation

tta = TikTokAutomation(
    file_path="video.mp4",
    output_path="output",
    account_name="my_account",
    acc_data={
        "title": "My TikTok Video",
        "description": "Description here",
        "tags": "tag1,tag2,tag3"
    }
)

# Process video and create clips
tta.process_and_create_clips(clip_duration=15)

# Upload (simulation by default)
tta.upload_and_log_short()
```

### Real API Upload
```python
# Same as above, but with real API
tta.upload_and_log_short(use_real_api=True)
```

## 📁 File Structure

```
tiktok_automation/
├── account_clips/          # Video clips by account
│   └── account_name/
│       ├── video_final.mp4
│       └── clips/
│           ├── clip_1.mp4
│           ├── clip_2.mp4
│           └── ...
├── account_tokens/         # Authentication tokens
│   └── token_account_name.json
├── logs/                   # Upload logs
│   └── account_name_uploaded_videos.json
├── tiktok_config.json      # API configuration
└── README.md              # This file
```

## 🔧 Configuration Options

### Environment Settings
- **sandbox**: For testing (if available)
- **production**: For real uploads

### Upload Settings
```python
# Privacy levels
"PUBLIC_TO_EVERYONE"        # Public video
"MUTUAL_FOLLOW_FRIENDS"     # Friends only
"SELF_ONLY"                 # Private

# Content settings
disable_duet=False          # Allow duets
disable_comment=False       # Allow comments
disable_stitch=False        # Allow stitches
```

## 🛠️ Troubleshooting

### Common Issues

1. **"TikTok API not available"**
   - Check if `tiktok_api.py` is in the `core/` directory
   - Ensure all dependencies are installed

2. **"Authentication failed"**
   - Check your Client Key and Client Secret
   - Verify redirect URI matches exactly
   - Ensure your app has the correct scopes

3. **"Upload failed"**
   - Check video format (MP4 recommended)
   - Verify file size limits
   - Ensure account is properly authenticated

4. **"Browser doesn't open"**
   - Try copying the auth URL manually
   - Check firewall settings for localhost:8080

### Debug Mode
Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Monitoring

### Check Account Status
```python
tta = TikTokAutomation(account_name="my_account")
status = tta.get_account_status()
print(f"Status: {status['status']}")
print(f"Type: {status['type']}")  # 'simulation' or 'real'
```

### View Upload Logs
```bash
cat tiktok_automation/logs/my_account_uploaded_videos.json
```

## 🔄 Switching Modes

### From Simulation to Real API
1. Complete TikTok app setup
2. Configure `tiktok_config.json`
3. Re-authenticate with `use_real_api=True`
4. Update upload calls to use `use_real_api=True`

### Back to Simulation
Simply omit `use_real_api=True` or set it to `False`.

## 🚨 Important Notes

### Rate Limits
- TikTok has strict rate limits
- Don't upload too frequently
- Respect TikTok's terms of service

### Content Policy
- Ensure your content follows TikTok guidelines
- No copyrighted material without permission
- Appropriate content only

### Security
- Keep your Client Secret secure
- Don't commit credentials to version control
- Regenerate tokens if compromised

## 📞 Support

If you encounter issues:
1. Check the [TikTok for Developers Documentation](https://developers.tiktok.com/doc/)
2. Review error logs in the console
3. Test with simulation mode first
4. Verify all configuration steps

## 📝 Example Complete Workflow

```python
from core.tiktok_automation_enhanced import TikTokAutomation

# 1. Setup
account_name = "my_tiktok_account"
video_file = "my_video.mp4"

# 2. Authenticate (choose one)
# Simulation:
TikTokAutomation.authenticate_tiktok_account(account_name)
# Real API:
# TikTokAutomation.authenticate_tiktok_account(account_name, use_real_api=True)

# 3. Create automation instance
tta = TikTokAutomation(
    file_path=video_file,
    output_path=f"tiktok_automation/account_clips/{account_name}",
    account_name=account_name,
    acc_data={
        "title": "My Amazing TikTok",
        "description": "Check out this cool video!",
        "tags": "viral,funny,trending"
    }
)

# 4. Process video
success = tta.process_and_create_clips(clip_duration=15)
if success:
    print("✅ Clips created successfully")
    
    # 5. Upload
    upload_success = tta.upload_and_log_short()  # or use_real_api=True
    if upload_success:
        print("🎉 Upload completed!")
    else:
        print("❌ Upload failed")
else:
    print("❌ Clip creation failed")
```

---

*Happy TikToking! 🎵*