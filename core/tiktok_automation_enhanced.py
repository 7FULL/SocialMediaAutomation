"""
Enhanced TikTok Automation with Real API Support
Combines the existing functionality with real TikTok API integration
"""

import datetime as datetime
import time
import os
import re
import json
import shutil
from moviepy.editor import VideoFileClip

from core.tiktok_api import TikTokAPI, authenticate_with_browser

# PIL compatibility fix for newer versions
try:
    from PIL import Image
    # Check if ANTIALIAS exists, if not, use LANCZOS
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass

# Import TikTok uploader
try:
    from tiktok_uploader.upload import upload_video
    UPLOADER_AVAILABLE = True
    print("✅ TikTok uploader available")
except ImportError:
    print("⚠️ TikTok uploader not available - running in simulation mode")
    UPLOADER_AVAILABLE = False


class TikTokAutomation:
    """
    Enhanced TikTok Automation class for video processing and upload
    
    Supports both real TikTok API integration and simulation mode
    for development and testing without API access.
    """
    
    def __init__(self, file_path="", output_path='output', account_name="", acc_data=None):
        if acc_data is None:
            acc_data = {}
        self.file_path = file_path
        self.output_path = output_path
        self.final_output_path = None
        self.account_name = account_name
        self.clips_folder = acc_data.get("clip_folder")
        self.acc_data = acc_data

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[\\/*?:"<>|]', "", filename)

    def process_video_file(self):
        """Copy the video file to the output path and prepare for processing."""
        if not os.path.exists(self.file_path):
            print(f"Error: File {self.file_path} does not exist.")
            return False
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        
        # Get the filename and create the final output path
        filename = os.path.basename(self.file_path)
        name, ext = os.path.splitext(filename)
        sanitized_name = self.sanitize_filename(name)
        
        self.final_output_path = os.path.join(self.output_path, f"{sanitized_name}_final.mp4")
        
        # Copy the file to the output path
        shutil.copy2(self.file_path, self.final_output_path)
        print(f"Video file copied to {self.final_output_path}")
        return True

    def create_clips(self, clip_duration=15):
        """Create clips from the processed video file."""
        if not self.final_output_path or not os.path.exists(self.final_output_path):
            print("No video file to process. Please process a video file first.")
            return False

        try:
            # Load the video
            video = VideoFileClip(self.final_output_path)
            total_duration = int(video.duration)
            
            # Create clips directory if it doesn't exist
            clips_dir = os.path.join(self.output_path, "clips")
            if not os.path.exists(clips_dir):
                os.makedirs(clips_dir)
            
            # Count existing clips to continue numbering
            existing_clips = [f for f in os.listdir(clips_dir) if f.startswith("clip_")]
            next_clip_number = len(existing_clips) + 1
            
            clips_created = 0
            
            # Create clips
            for start in range(0, total_duration, clip_duration):
                end = min(start + clip_duration, total_duration)
                
                # Skip if the remaining time is less than the desired clip duration
                if end - start < clip_duration:
                    break
                
                clip = video.subclip(start, end)
                clip_path = os.path.join(clips_dir, f"clip_{next_clip_number}.mp4")
                
                # Write the clip
                clip.write_videofile(clip_path, codec='libx264', audio_codec='aac')
                print(f"Created clip: {clip_path}")
                
                clips_created += 1
                next_clip_number += 1
            
            # Clean up
            video.close()
            print(f"Successfully created {clips_created} clips of {clip_duration} seconds each.")
            return True
            
        except Exception as e:
            print(f"Error creating clips: {e}")
            return False

    def upload_and_log_short(self):
        """Upload the next available clip to TikTok and log it."""
        log_file = f"tiktok_automation/logs/{self.account_name}_uploaded_videos.json"
        
        # Get next clip to upload
        clip_filename, part_number = self.get_next_clip_to_upload(log_file)
        if not clip_filename:
            print(f"❌ No clips available to upload for {self.account_name}")
            return False
        
        file_path = os.path.join(self.clips_folder, "clips", clip_filename)
        
        if not os.path.exists(file_path):
            print(f"❌ No clip found at {file_path}")
            return False
        
        title = self.acc_data.get("title", "TikTok Video") + " pt: " + str(part_number)
        description = self.acc_data.get("description", "") + " pt: " + str(part_number)
        tags = self.acc_data.get("tags", "")
        
        # Add hashtags to description if tags are provided
        if tags:
            hashtags = " ".join([f"#{tag.strip()}" for tag in tags.split(",") if tag.strip()])
            description = f"{description} {hashtags}"
        
        # Upload with tiktok-uploader
        success = self._upload_with_tiktok_uploader(file_path, title, description)
        
        if success:
            # Log the video
            self.log_video(log_file, title, clip_filename, part_number)
            print(f"🎉 TikTok clip {part_number} uploaded successfully!")
            return True
        else:
            print(f"❌ Failed to upload TikTok clip {part_number}")
            return False
    
    def _upload_with_tiktok_uploader(self, file_path, title, description):
        """Upload video using tiktok-uploader library"""
        if not UPLOADER_AVAILABLE:
            print("⚠️ TikTok uploader not available - simulating upload")
            return self._simulate_tiktok_upload(file_path, title, description)
        
        try:
            print(f"🚀 Uploading {file_path} to TikTok...")
            
            # Load cookies file
            cookies_file = self._get_cookies_file()
            if not cookies_file or not os.path.exists(cookies_file):
                print("❌ TikTok cookies file not found")
                return False
            
            # Upload video
            result = upload_video(
                filename=file_path,
                description=description,
                cookies=cookies_file
            )
            
            if result:
                print(f"✅ Video uploaded successfully to TikTok!")
                print(f"📝 Description: {description}")
                return True
            else:
                print(f"❌ TikTok upload failed")
                return False
                
        except Exception as e:
            print(f"❌ TikTok upload error: {e}")
            return False
    
    def _simulate_tiktok_upload(self, file_path, title, description):
        """Simulate TikTok upload for testing"""
        print(f"🎭 Simulating upload of {file_path} to TikTok...")
        print(f"📱 Title: {title}")
        print(f"📝 Description: {description}")
        
        # Simulate upload time
        import time
        time.sleep(2)
        print("✅ Simulated upload completed!")
        return True
    
    def _get_cookies_file(self):
        """Get the cookies file path for this account"""
        config_dir = f"tiktok_automation/account_config"
        config_file = f"{config_dir}/tiktok_config_{self.account_name}.json"
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get("cookies_file")
        return None
    
    def get_next_clip_to_upload(self, log_file):
        """Get the next clip file that hasn't been uploaded yet"""
        # Get list of uploaded clips from log
        uploaded_clips = set()
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
                for video in data.get("videos", []):
                    if "clip_file" in video:
                        uploaded_clips.add(video["clip_file"])
        
        # Get available clips in the folder and find first unuploaded one
        clips_folder = os.path.join(self.clips_folder, "clips")
        if not os.path.exists(clips_folder):
            return None, 1
            
        clip_files = []
        for file in os.listdir(clips_folder):
            if file.startswith("clip_") and file.endswith(".mp4"):
                try:
                    clip_num = int(file.split("_")[1].split(".")[0])
                    clip_files.append((clip_num, file))
                except (ValueError, IndexError):
                    continue
        
        clip_files.sort(key=lambda x: x[0])
        for clip_num, filename in clip_files:
            if filename not in uploaded_clips:
                return filename, clip_num
        return None, len(uploaded_clips) + 1
    
    def log_video(self, log_file, title, clip_file, part_number):
        """Log uploaded video to JSON file"""
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Load existing data
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"videos": []}
        
        # Add new video entry
        video_entry = {
            "title": title,
            "upload_date": datetime.datetime.now().isoformat(),
            "platform": "TikTok",
            "account": self.account_name,
            "part_number": part_number,
            "clip_file": clip_file
        }
        
        data["videos"].append(video_entry)
        
        # Save updated data
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"📝 Video logged: {title}")
    
    def _real_tiktok_upload(self, file_path, title, description):
        """Upload video using real TikTok API"""
        if not REAL_API_AVAILABLE:
            print("❌ Real TikTok API not available")
            return False
            
        try:
            print(f"🚀 Uploading {file_path} to TikTok (Real API)...")
            
            # Load TikTok API credentials
            config = self._load_tiktok_config()
            if not config:
                print("❌ TikTok API credentials not configured")
                return False
            
            # Initialize TikTok API
            api = TikTokAPI(
                client_key=config["client_key"],
                client_secret=config["client_secret"]
            )
            
            # Load tokens for this account
            if not api.load_tokens(self.account_name):
                print(f"❌ No authentication tokens found for {self.account_name}")
                return False
            
            # Upload video
            success = api.upload_video(
                video_path=file_path,
                title=title,
                description=description,
                privacy_level="PUBLIC_TO_EVERYONE",
                disable_duet=False,
                disable_comment=False,
                disable_stitch=False
            )
            
            if success:
                print(f"✅ Video uploaded successfully to TikTok!")
                print(f"📱 Title: {title}")
                print(f"📝 Description: {description}")
                return True
            else:
                print(f"❌ TikTok upload failed")
                return False
                
        except Exception as e:
            print(f"❌ TikTok upload error: {e}")
            return False
    
    def _simulate_tiktok_upload(self, file_path, title, description):
        """Simulate TikTok upload for testing"""
        print(f"🎭 Simulating upload of {file_path} to TikTok...")
        print(f"📱 Title: {title}")
        print(f"📝 Description: {description}")
        
        # Simulate upload time
        import time
        time.sleep(2)
        
        print(f"✅ TikTok upload simulated successfully!")
        return True

    @staticmethod
    def get_next_part_number(log_file):
        """Get the next part number for video uploads."""
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
                return len(data.get("videos", [])) + 1
        else:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        return 1


    @staticmethod
    def authenticate_tiktok_account(account_name, use_real_api=None):
        """
        Authenticate TikTok account using real API or simulation
        
        Args:
            account_name (str): Account name for token storage
            use_real_api (bool): Whether to use real TikTok API or simulation
        """
        # Auto-detect if real API should be used
        if use_real_api is None:
            use_real_api = REAL_API_AVAILABLE and TikTokAutomation._has_real_api_config()
        
        if use_real_api:
            # Real TikTok API authentication
            return TikTokAutomation._real_tiktok_authentication(account_name)
        else:
            # Simulation mode (default)
            return TikTokAutomation._simulate_tiktok_authentication(account_name)
    
    @staticmethod
    def _real_tiktok_authentication(account_name):
        """
        Real TikTok authentication using TikTok API
        """
        if not REAL_API_AVAILABLE:
            print("❌ Real TikTok API not available")
            return False
            
        print(f"🎵 Starting real TikTok authentication for account: {account_name}")
        
        # Load TikTok API credentials
        config = TikTokAutomation._load_tiktok_config()
        if not config:
            print("❌ TikTok API credentials not configured")
            return False
        
        try:
            # Initialize TikTok API
            api = TikTokAPI(
                client_key=config["client_key"],
                client_secret=config["client_secret"],
                redirect_uri=config.get("redirect_uri", "http://localhost:8080/callback")
            )
            api.account_name = account_name
            
            # Try to load existing tokens
            if api.load_tokens(account_name):
                print(f"✅ Found existing tokens for {account_name}")
                
                # Verify tokens by getting user info
                user_info = api.get_user_info()
                if user_info:
                    print(f"✅ TikTok authentication verified for {account_name}")
                    return True
                else:
                    print("🔄 Tokens expired, refreshing...")
                    if api.refresh_access_token():
                        print(f"✅ Tokens refreshed for {account_name}")
                        return True
                    else:
                        print("❌ Failed to refresh tokens, re-authentication needed")
            
            # Perform new authentication
            print(f"🔐 Starting OAuth flow for {account_name}")
            success = authenticate_with_browser(api)
            
            if success:
                print(f"🎉 TikTok authentication successful for {account_name}")
                return True
            else:
                print(f"❌ TikTok authentication failed for {account_name}")
                return False
                
        except Exception as e:
            print(f"❌ TikTok authentication error: {e}")
            return False
    
    @staticmethod
    def _simulate_tiktok_authentication(account_name):
        """
        Simulate TikTok authentication (for testing without API access)
        """
        print(f"🎭 Simulating TikTok authentication for account: {account_name}")
        
        # Create directories for TikTok automation
        token_dir = "tiktok_automation/account_tokens"
        if not os.path.exists(token_dir):
            os.makedirs(token_dir)
        
        # Create a dummy token file to simulate authentication
        token_file = os.path.join(token_dir, f"token_{account_name}.json")
        with open(token_file, 'w') as f:
            json.dump({
                "account_name": account_name,
                "authenticated": True,
                "auth_date": datetime.datetime.now().isoformat(),
                "simulation": True,
                "access_token": "simulated_token_" + account_name,
                "user_id": "sim_" + account_name
            }, f, indent=4)
        
        print(f"✅ TikTok authentication simulated successfully for {account_name}")
        return True
    
    @staticmethod
    def _load_tiktok_config():
        """
        Load TikTok API configuration
        """
        config_file = "tiktok_automation/tiktok_config.json"
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading TikTok config: {e}")
                return None
        else:
            return None
    
    @staticmethod
    def _has_real_api_config():
        """Check if real API configuration is available"""
        config = TikTokAutomation._load_tiktok_config()
        return config and "client_key" in config and "client_secret" in config

    def process_and_create_clips(self, clip_duration=15):
        """Process video file and create clips in one step."""
        if self.process_video_file():
            return self.create_clips(clip_duration)
        return False
    
    def get_account_status(self):
        """Get detailed account authentication status"""
        token_file = f"tiktok_automation/account_tokens/token_{self.account_name}.json"
        
        if not os.path.exists(token_file):
            return {
                "authenticated": False,
                "status": "Not authenticated",
                "type": "none"
            }
        
        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            
            if token_data.get("simulation", False):
                return {
                    "authenticated": True,
                    "status": "Simulated (for testing)",
                    "type": "simulation",
                    "auth_date": token_data.get("auth_date")
                }
            else:
                return {
                    "authenticated": True,
                    "status": "Real API authenticated",
                    "type": "real",
                    "auth_date": token_data.get("auth_date"),
                    "user_id": token_data.get("user_id")
                }
                
        except Exception as e:
            return {
                "authenticated": False,
                "status": f"Error reading token: {e}",
                "type": "error"
            }
    
    @staticmethod
    def create_config_template():
        """Create a configuration template for TikTok API"""
        config_dir = "tiktok_automation"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        config_file = os.path.join(config_dir, "tiktok_config.json")
        
        if not os.path.exists(config_file):
            template = {
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
            
            with open(config_file, 'w') as f:
                json.dump(template, f, indent=4)
            
            print(f"✅ TikTok configuration template created at: {config_file}")
            print("📝 Please edit this file with your TikTok API credentials")
            return config_file
        else:
            print(f"⚠️ TikTok config already exists at: {config_file}")
            return config_file