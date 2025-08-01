"""
Instagram Automation Module
Handles Instagram content posting and automation using instagrapi
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from moviepy.editor import VideoFileClip
import re

from .instagram_api import InstagramAPI


class InstagramAutomation:
    """
    Instagram automation class for posting content
    Handles video/photo uploads, reel creation, and account management
    """
    
    def __init__(self, account_name: str = "", acc_data: Dict = None):
        if acc_data is None:
            acc_data = {}
            
        self.account_name = account_name
        self.acc_data = acc_data
        self.api = InstagramAPI()
        self.clips_folder = acc_data.get("clip_folder", "")
        
        # Set up directories
        self.setup_directories()
        
        # Load authentication if available
        if account_name:
            self.api.set_account(account_name)
            
        # Configure credentials if provided in acc_data
        self.setup_credentials()
    
    def setup_directories(self):
        """Create necessary directories for Instagram automation"""
        base_dir = "instagram_automation"
        directories = [
            f"{base_dir}/account_sessions",
            f"{base_dir}/logs",
            f"{base_dir}/uploads"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def setup_credentials(self):
        """Setup Instagram credentials from acc_data or saved credentials"""
        # Try to get credentials from acc_data first (for web system)
        if "instagram_username" in self.acc_data and "instagram_password" in self.acc_data:
            print(f"🔑 Setting up Instagram credentials from account data for {self.account_name}")
            self.api.username = self.acc_data["instagram_username"]
            self.api.password = self.acc_data["instagram_password"]
            return
        
        # Try to load saved credentials
        credentials = self.load_account_credentials()
        if credentials and "username" in credentials and "password" in credentials:
            print(f"🔑 Loading saved Instagram credentials for {self.account_name}")
            self.api.username = credentials["username"]
            self.api.password = credentials["password"]
            return
        
        print(f"⚠️ No Instagram credentials found for {self.account_name}")
        print("Please ensure credentials are provided in account data or saved credentials")
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate with Instagram
        
        Args:
            username (str): Instagram username
            password (str): Instagram password
        
        Returns:
            bool: True if authentication successful
        """
        success = self.api.authenticate(username, password)
        
        if success:
            # Save credentials for this account (encrypted/hashed in production)
            self.save_account_credentials(username, password)
            print(f"✅ Instagram account @{username} authenticated successfully")
        else:
            print(f"❌ Failed to authenticate Instagram account @{username}")
        
        return success
    
    def load_account_session(self) -> bool:
        """Load existing session for the account"""
        if not self.account_name:
            return False
        
        return self.api.load_session(self.account_name)
    
    def save_account_credentials(self, username: str, password: str):
        """Save account credentials (in a real app, encrypt these!)"""
        credentials_file = f"instagram_automation/account_sessions/credentials_{self.account_name}.json"
        
        # In production, encrypt these credentials!
        credentials = {
            "username": username,
            "password": password,  # This should be encrypted!
            "saved_at": datetime.now().isoformat()
        }
        
        with open(credentials_file, 'w') as f:
            json.dump(credentials, f, indent=4)
    
    def load_account_credentials(self) -> Optional[Dict[str, str]]:
        """Load saved account credentials"""
        credentials_file = f"instagram_automation/account_sessions/credentials_{self.account_name}.json"
        
        if os.path.exists(credentials_file):
            try:
                with open(credentials_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading credentials: {e}")
        
        return None
    
    def ensure_authenticated(self) -> bool:
        """
        Ensure that we're authenticated, try to re-authenticate if needed
        Uses the same robust authentication logic as the API class
        """
        print(f"🔍 Ensuring authentication for {self.account_name}...")
        
        # Try to load existing session first
        if self.api.load_session(self.account_name):
            if self.api.is_authenticated():
                print(f"✅ Existing session valid for {self.account_name}")
                return True
        
        print(f"🔄 Session expired for {self.account_name}, need fresh authentication...")
        
        # Try to authenticate with saved credentials
        credentials = self.load_account_credentials()
        if credentials and "username" in credentials and "password" in credentials:
            print(f"🔐 Authenticating with saved credentials for {self.account_name}...")
            
            # Set credentials in API instance
            self.api.username = credentials["username"]
            self.api.password = credentials["password"]
            
            # Use the robust authentication method
            success = self.api.ensure_authenticated_for_upload()
            if success:
                print(f"✅ Authentication successful for {self.account_name}")
                return True
        
        print(f"❌ Could not authenticate Instagram account {self.account_name}")
        print("Please check your credentials or re-authenticate manually")
        return False
    
    def post_content(self, media_path: str, caption: str = "", 
                    content_type: str = "auto", location: Optional[Dict] = None) -> bool:
        """
        Post content to Instagram
        
        Args:
            media_path (str): Path to media file
            caption (str): Post caption
            content_type (str): "photo", "video", "reel", "story", or "auto"
            location (dict): Location data (optional)
        
        Returns:
            bool: True if post successful
        """
        if not os.path.exists(media_path):
            print(f"❌ Media file not found: {media_path}")
            return False
        
        # CRITICAL: Ensure authentication before posting
        if not self.ensure_authenticated():
            print(f"❌ Cannot authenticate for posting")
            return False
        
        # Auto-detect content type if needed
        if content_type == "auto":
            content_type = self.detect_content_type(media_path)
        
        print(f"📤 Posting {content_type} to Instagram: {os.path.basename(media_path)}")
        
        try:
            if content_type == "photo":
                return self.api.upload_photo(media_path, caption, location)
            elif content_type == "video":
                return self.api.upload_video(media_path, caption, location=location)
            elif content_type == "reel":
                # For reels, use the robust upload method
                return self.api.upload_reel(media_path, caption, location=location)
            elif content_type == "story":
                return self.api.upload_story(media_path)
            else:
                print(f"❌ Unsupported content type: {content_type}")
                return False
        
        except Exception as e:
            print(f"❌ Error posting content: {e}")
            return False
    
    def detect_content_type(self, media_path: str) -> str:
        """Auto-detect content type based on file"""
        file_extension = Path(media_path).suffix.lower()
        
        if file_extension in ['.jpg', '.jpeg', '.png']:
            return "photo"
        elif file_extension in ['.mp4', '.mov']:
            # Check duration to decide between video and reel
            try:
                clip = VideoFileClip(media_path)
                duration = clip.duration
                clip.close()
                
                # If video is short (under 60 seconds), treat as reel
                if duration <= 60:
                    return "reel"
                else:
                    return "video"
            except:
                return "video"  # Default to video if duration check fails
        
        return "photo"  # Default fallback
    
    def post_next_clip(self) -> bool:
        """
        Post the next available clip from the clips folder
        Similar to YouTube automation workflow
        """
        print(f"🚀 Starting Instagram clip upload for account: {self.account_name}")
        
        if not self.clips_folder or not os.path.exists(self.clips_folder):
            print(f"❌ Clips folder not found: {self.clips_folder}")
            return False
        
        # Ensure we're authenticated first
        print(f"🔐 Verifying authentication for {self.account_name}...")
        if not self.ensure_authenticated():
            print(f"❌ Cannot authenticate Instagram account {self.account_name}")
            return False
        
        # Get next clip to upload
        log_file = f"instagram_automation/logs/{self.account_name}_uploaded_content.json"
        clip_filename, part_number = self.get_next_clip_to_upload(log_file)
        
        if not clip_filename:
            print(f"ℹ️ No clips available to upload for account {self.account_name}")
            return False
        
        file_path = os.path.join(self.clips_folder, "clips", clip_filename)
        print(f"📹 Found clip to upload: {clip_filename} (Part {part_number})")
        
        # Validate the clip before uploading
        validation = self.api.validate_video_for_upload(file_path, "reel")
        if not validation["valid"]:
            print(f"❌ Clip validation failed: {validation['error']}")
            return False
        
        print(f"✅ Clip validation passed: {validation['info']}")
        
        # Generate caption
        caption = self.generate_caption(part_number)
        print(f"📝 Generated caption: {caption[:100]}...")
        
        # Post as reel (ideal for short clips)
        print(f"📤 Uploading to Instagram as reel...")
        success = self.post_content(file_path, caption, "reel")
        
        if success:
            print(f"✅ Clip {part_number} posted successfully to Instagram!")
            self.log_uploaded_content(clip_filename, caption, "reel")
            return True
        else:
            print(f"❌ Failed to post clip {part_number} to Instagram")
            return False
    
    def get_next_clip_to_upload(self, log_file: str) -> tuple:
        """Get the next clip file that hasn't been uploaded yet"""
        # Get list of uploaded clips from log
        uploaded_clips = set()
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
                for content in data.get("content", []):
                    if "clip_file" in content:
                        uploaded_clips.add(content["clip_file"])
        
        # Get available clips in the folder
        clips_folder = os.path.join(self.clips_folder, "clips")
        if not os.path.exists(clips_folder):
            return None, 1
        
        # Get all clip files and sort them numerically
        clip_files = []
        for file in os.listdir(clips_folder):
            if file.startswith("clip_") and file.endswith(".mp4"):
                try:
                    # Extract number from filename like "clip_1.mp4"
                    clip_num = int(file.split("_")[1].split(".")[0])
                    clip_files.append((clip_num, file))
                except (ValueError, IndexError):
                    continue
        
        # Sort by clip number
        clip_files.sort(key=lambda x: x[0])
        
        # Find first clip that hasn't been uploaded
        for clip_num, filename in clip_files:
            if filename not in uploaded_clips:
                return filename, clip_num
        
        # If all clips have been uploaded, return None
        return None, len(uploaded_clips) + 1
    
    def generate_caption(self, part_number: int) -> str:
        """
        Generate caption for Instagram post
        
        Args:
            part_number (int): Part number of the clip
        
        Returns:
            str: Generated caption
        """
        # Use configured title/description from account data
        account_title = self.acc_data.get("title", "").strip()
        account_description = self.acc_data.get("description", "").strip()
        account_tags = self.acc_data.get("tags", "").strip()
        
        caption_parts = []
        
        # Add title
        if account_title:
            caption_parts.append(f"{account_title} - Part {part_number}")
        else:
            caption_parts.append(f"Content Part {part_number}")
        
        # Add description
        if account_description:
            caption_parts.append(f"\n{account_description}")
        
        # Add hashtags (Instagram format)
        if account_tags:
            # Convert comma-separated tags to hashtags
            tags = [tag.strip() for tag in account_tags.split(",")]
            hashtags = [f"#{tag.replace(' ', '').replace('#', '')}" for tag in tags if tag]
            if hashtags:
                caption_parts.append(f"\n\n{' '.join(hashtags)}")
        
        return ''.join(caption_parts)
    
    def log_uploaded_content(self, clip_filename: str, caption: str, content_type: str):
        """Log uploaded content for tracking"""
        log_file = f"instagram_automation/logs/{self.account_name}_uploaded_content.json"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Load existing data
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"content": []}
        
        # Add new content entry
        content_entry = {
            "clip_file": clip_filename,
            "caption": caption,
            "content_type": content_type,
            "upload_time": datetime.now().isoformat(),
            "account": self.account_name
        }
        
        data["content"].append(content_entry)
        
        # Save back to file
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=4)
    
    def get_account_stats(self) -> Optional[Dict[str, Any]]:
        """Get account statistics"""
        try:
            return self.api.get_user_info()
        except Exception as e:
            print(f"Error getting account stats: {e}")
            return None
    
    def get_clips_stats(self) -> Dict[str, Any]:
        """Get clips statistics similar to YouTube automation"""
        clips_folder = os.path.join(self.clips_folder, "clips") if self.clips_folder else ""
        
        if not os.path.exists(clips_folder):
            return {
                "available_clips": 0,
                "total_clips": 0,
                "uploaded_clips": 0,
                "clips_per_week": 0,
                "weeks_of_content": 0,
                "status": "no_folder"
            }
        
        # Count total clips
        total_clips = len([f for f in os.listdir(clips_folder) 
                          if f.startswith("clip_") and f.endswith(".mp4")])
        
        # Count uploaded clips
        log_file = f"instagram_automation/logs/{self.account_name}_uploaded_content.json"
        uploaded_clips = 0
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
                uploaded_clips = len(data.get("content", []))
        
        available_clips = max(0, total_clips - uploaded_clips)
        
        # Calculate weeks of content (assuming 1 post per day)
        clips_per_week = 7  # Daily posting
        weeks_of_content = available_clips / clips_per_week if clips_per_week > 0 else 0
        
        # Determine status
        if available_clips == 0:
            status = "critical"
        elif weeks_of_content < 1:
            status = "low"
        else:
            status = "healthy"
        
        return {
            "available_clips": available_clips,
            "total_clips": total_clips,
            "uploaded_clips": uploaded_clips,
            "clips_per_week": clips_per_week,
            "weeks_of_content": round(weeks_of_content, 1),
            "status": status
        }
    
    def is_authenticated(self) -> bool:
        """Check if account is authenticated"""
        return self.api.is_authenticated()
    
    def test_connection(self) -> bool:
        """Test Instagram connection"""
        try:
            user_info = self.api.get_user_info()
            return user_info is not None
        except:
            return False
    
    @staticmethod
    def get_platform_requirements() -> Dict[str, Any]:
        """Get Instagram platform requirements and limits"""
        api = InstagramAPI()
        return api.get_upload_limits()


# Utility functions for Instagram content optimization
def optimize_video_for_instagram(video_path: str, output_path: str, 
                                content_type: str = "reel") -> bool:
    """
    Optimize video for Instagram posting
    
    Args:
        video_path (str): Input video path
        output_path (str): Output video path
        content_type (str): "reel", "story", or "video"
    
    Returns:
        bool: True if optimization successful
    """
    try:
        clip = VideoFileClip(video_path)
        
        # Get target dimensions based on content type
        if content_type == "reel" or content_type == "story":
            target_width, target_height = 1080, 1920  # 9:16
        else:
            target_width, target_height = 1080, 1080   # 1:1
        
        # Resize video
        clip_resized = clip.resize((target_width, target_height))
        
        # Ensure duration limits
        max_duration = 90 if content_type == "reel" else 60
        if clip_resized.duration > max_duration:
            clip_resized = clip_resized.subclip(0, max_duration)
        
        # Write optimized video
        clip_resized.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            fps=30
        )
        
        clip.close()
        clip_resized.close()
        
        print(f"✅ Video optimized for Instagram {content_type}")
        return True
        
    except Exception as e:
        print(f"❌ Error optimizing video: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    print("Instagram Automation Module")
    print("===========================")
    
    # Test the module
    automation = InstagramAutomation("test_account")
    requirements = automation.get_platform_requirements()
    print(f"Instagram Requirements: {requirements}")