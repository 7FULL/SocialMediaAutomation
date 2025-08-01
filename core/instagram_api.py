"""
Instagram API Integration Module
Instagram upload functionality using instagrapi library
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

try:
    from instagrapi import Client
    from instagrapi.exceptions import (
        LoginRequired, 
        ChallengeRequired, 
        FeedbackRequired,
        PleaseWaitFewMinutes,
        RecaptchaChallengeForm,
        SelectContactPointRecoveryForm,
        ClientError
    )
except ImportError:
    raise ImportError("instagrapi library is required. Install it with: pip install instagrapi")


class InstagramAPI:
    """
    Instagram API wrapper for content creation and upload
    Based on instagrapi library
    """
    
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
        self.client = Client()
        self.account_name = None
        self.session_file = None
        
        # Configure logging to reduce noise
        logging.getLogger("instagrapi").setLevel(logging.WARNING)
        
        # Set up client settings for better success rate
        self.client.delay_range = [1, 3]  # Delay between requests
        
        # Configure client for better authentication success
        self.client.request_timeout = 10
        self.client.country_code = 1  # US country code
        self.client.locale = "en_US"
        
        # Set user agent to mobile for better compatibility
        from instagrapi.mixins.challenge import ChallengeChoice
        self.client.challenge_code_handler = self.challenge_code_handler
        self.client.change_password_handler = self.change_password_handler
        
    def set_account(self, account_name: str):
        """Set the account name for session management"""
        self.account_name = account_name
        self.session_file = f"instagram_automation/account_sessions/session_{account_name}.json"
    
    def challenge_code_handler(self, username, choice):
        """Handle challenge codes during authentication"""
        print(f"⚠️ Instagram challenge required for {username}")
        print(f"Challenge type: {choice}")
        print("Please log in to Instagram manually to resolve the challenge")
        return False  # Cannot handle automatically
    
    def change_password_handler(self, username):
        """Handle password change requests"""
        print(f"⚠️ Instagram requesting password change for {username}")
        print("Please change your password through Instagram's website")
        return False  # Cannot handle automatically
        
    def authenticate(self, username: str = None, password: str = None) -> bool:
        """
        Authenticate with Instagram using username/password
        Supports session persistence and 2FA
        """
        if username:
            self.username = username
        if password:
            self.password = password
            
        if not self.username or not self.password:
            print("Username and password are required")
            return False
        
        try:
            # Try to load existing session first
            if self.session_file and os.path.exists(self.session_file):
                try:
                    print(f"🔄 Loading existing session for @{self.username}...")
                    self.client.load_settings(self.session_file)
                    
                    # Try to verify session without re-login first
                    try:
                        user_info = self.client.account_info()
                        username = getattr(user_info, 'username', None)
                        if user_info and username == self.username:
                            print(f"✅ Existing session valid for @{self.username}")
                            return True
                    except (LoginRequired, ClientError):
                        print(f"🔄 Session expired, attempting re-login...")
                        pass
                    
                    # Session expired, try to re-login with existing settings
                    self.client.login(self.username, self.password, relogin=True)
                    
                    # Verify the session is now valid
                    user_info = self.client.account_info()
                    if user_info:
                        print(f"✅ Successfully re-authenticated @{self.username}")
                        return True
                        
                except Exception as e:
                    print(f"⚠️ Could not reuse session, creating new one: {e}")
                    # Reset client for fresh login
                    self.client = Client()
                    self.client.delay_range = [1, 3]
            
            # Create new login
            print(f"🔐 Performing fresh login to Instagram as @{self.username}...")
            
            # Add small delay to avoid being flagged
            import time
            time.sleep(2)
            
            success = self.client.login(self.username, self.password)
            
            if not success:
                print("❌ Login returned False")
                return False
            
            # Save session for future use
            if self.session_file:
                os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
                self.client.dump_settings(self.session_file)
                print(f"💾 Session saved to {self.session_file}")
            
            # Get account info to verify login
            user_info = self.client.account_info()
            if user_info:
                username = getattr(user_info, 'username', 'Unknown')
                full_name = getattr(user_info, 'full_name', 'Unknown')
                print(f"🎉 Successfully logged in as @{username}")
                print(f"👤 Full Name: {full_name}")
                
                # Try to get follower count
                follower_count = 0
                for attr in ['follower_count', 'followers_count', 'followers']:
                    if hasattr(user_info, attr):
                        follower_count = getattr(user_info, attr)
                        break
                
                print(f"📊 Followers: {follower_count}")
                return True
            
        except ChallengeRequired:
            print("❌ Challenge required - Instagram needs additional verification")
            print("Try logging in from the Instagram app or website first")
            return False
        except LoginRequired:
            print("❌ Login failed - check username and password")
            return False
        # except AccountBanned:
        #     print("❌ Account is banned")
        #     return False
        except PleaseWaitFewMinutes:
            print("❌ Rate limited - please wait a few minutes before trying again")
            return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
        
        return False
    
    def load_session(self, account_name: str) -> bool:
        """Load saved session"""
        self.set_account(account_name)
        
        if os.path.exists(self.session_file):
            try:
                print(f"🔄 Loading session for account {account_name}...")
                self.client.load_settings(self.session_file)
                
                # Try to get account info to verify session is valid
                user_info = self.client.account_info()
                if user_info:
                    self.username = getattr(user_info, 'username', 'Unknown')
                    print(f"✅ Session loaded for @{self.username}")
                    return True
                    
            except (LoginRequired, ClientError) as e:
                print(f"⚠️ Session expired for {account_name}: {e}")
                return False
            except Exception as e:
                print(f"⚠️ Error loading session for {account_name}: {e}")
                return False
        else:
            print(f"⚠️ No session file found for {account_name}")
        
        return False
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get user information"""
        try:
            user_info = self.client.account_info()
            if user_info:
                # Handle different attribute names in different instagrapi versions
                result = {
                    "username": getattr(user_info, 'username', 'Unknown'),
                    "full_name": getattr(user_info, 'full_name', 'Unknown'),
                    "is_private": getattr(user_info, 'is_private', False),
                    "is_verified": getattr(user_info, 'is_verified', False),
                }
                
                # Try different attribute names for follower count
                for attr in ['follower_count', 'followers_count', 'followers']:
                    if hasattr(user_info, attr):
                        result["follower_count"] = getattr(user_info, attr)
                        break
                else:
                    result["follower_count"] = 0
                
                # Try different attribute names for following count
                for attr in ['following_count', 'followings_count', 'following']:
                    if hasattr(user_info, attr):
                        result["following_count"] = getattr(user_info, attr)
                        break
                else:
                    result["following_count"] = 0
                
                # Try different attribute names for media count
                for attr in ['media_count', 'medias_count', 'posts_count', 'posts']:
                    if hasattr(user_info, attr):
                        result["media_count"] = getattr(user_info, attr)
                        break
                else:
                    result["media_count"] = 0
                
                # Optional attributes
                result["biography"] = getattr(user_info, 'biography', '')
                result["external_url"] = getattr(user_info, 'external_url', '')
                
                return result
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def upload_photo(self, image_path: str, caption: str = "", 
                    location: Optional[Dict] = None) -> bool:
        """
        Upload photo to Instagram
        
        Args:
            image_path (str): Path to image file
            caption (str): Photo caption
            location (dict): Location data (optional)
        """
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return False
        
        try:
            print(f"📷 Uploading photo: {os.path.basename(image_path)}")
            
            # Upload photo
            media = self.client.photo_upload(
                path=image_path,
                caption=caption,
                location=location
            )
            
            if media:
                print(f"✅ Photo uploaded successfully!")
                print(f"📱 Post ID: {media.id}")
                print(f"🔗 URL: https://www.instagram.com/p/{media.code}/")
                return True
            else:
                print("❌ Photo upload failed")
                return False
                
        except FeedbackRequired as e:
            print(f"❌ Upload blocked by Instagram: {e}")
            return False
        except Exception as e:
            print(f"❌ Photo upload error: {e}")
            return False
    
    def upload_video(self, video_path: str, caption: str = "", 
                    thumbnail_path: Optional[str] = None,
                    location: Optional[Dict] = None) -> bool:
        """
        Upload video to Instagram (Reels)
        
        Args:
            video_path (str): Path to video file
            caption (str): Video caption
            thumbnail_path (str): Path to custom thumbnail (optional)
            location (dict): Location data (optional)
        """
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return False
        
        try:
            print(f"🎥 Uploading video: {os.path.basename(video_path)}")
            
            # Upload video as reel
            media = self.client.video_upload(
                path=video_path,
                caption=caption,
                thumbnail=thumbnail_path,
                location=location
            )
            
            if media:
                print(f"✅ Video uploaded successfully!")
                print(f"📱 Post ID: {media.id}")
                print(f"🔗 URL: https://www.instagram.com/p/{media.code}/")
                return True
            else:
                print("❌ Video upload failed")
                return False
                
        except LoginRequired as e:
            print(f"❌ Not authenticated - login required: {e}")
            return False
        except FeedbackRequired as e:
            print(f"❌ Upload blocked by Instagram: {e}")
            print("This may be due to content policy or rate limiting")
            return False
        except ClientError as e:
            print(f"❌ Instagram API error: {e}")
            return False
        except Exception as e:
            print(f"❌ Video upload error: {e}")
            return False
    
    def upload_reel(self, video_path: str, caption: str = "",
                   thumbnail_path: Optional[str] = None,
                   location: Optional[Dict] = None) -> bool:
        """
        Upload video as Instagram Reel
        
        Args:
            video_path (str): Path to video file
            caption (str): Reel caption
            thumbnail_path (str): Path to custom thumbnail (optional)
            location (dict): Location data (optional)
        """
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return False
        
        # Validate video before upload
        validation_result = self.validate_video_for_upload(video_path, "reel")
        if not validation_result["valid"]:
            print(f"❌ Video validation failed: {validation_result['error']}")
            return False
        
        # CRITICAL: Ensure we're authenticated before upload
        if not self.ensure_authenticated_for_upload():
            print(f"❌ Cannot authenticate before upload")
            return False
        
        try:
            print(f"🎬 Uploading reel: {os.path.basename(video_path)}")
            print(f"📊 Video info: {validation_result['info']}")
            
            # Add small delay to avoid rate limiting
            import time
            time.sleep(2)
            
            # Upload as clip/reel (recommended for reels)
            print(f"🔄 Using clip_upload for reel...")
            media = self.client.clip_upload(
                path=video_path,
                caption=caption,
                thumbnail=thumbnail_path,
                location=location
            )
            
            if media:
                print(f"✅ Reel uploaded successfully!")
                print(f"📱 Post ID: {media.id}")
                print(f"🔗 URL: https://www.instagram.com/reel/{media.code}/")
                return True
            else:
                print("❌ Reel upload failed - no media returned")
                return False
                
        except LoginRequired as e:
            print(f"❌ Not authenticated - login required: {e}")
            print("🔄 Attempting re-authentication...")
            
            # Try to re-authenticate and retry once
            if self.re_authenticate_and_retry():
                print("🔄 Retrying upload after re-authentication...")
                try:
                    media = self.client.clip_upload(
                        path=video_path,
                        caption=caption,
                        thumbnail=thumbnail_path,
                        location=location
                    )
                    if media:
                        print(f"✅ Reel uploaded successfully after re-auth!")
                        print(f"📱 Post ID: {media.id}")
                        return True
                except Exception as retry_error:
                    print(f"❌ Retry failed: {retry_error}")
            
            return False
        except FeedbackRequired as e:
            print(f"❌ Upload blocked by Instagram: {e}")
            print("This may be due to content policy or rate limiting")
            return False
        except ClientError as e:
            print(f"❌ Instagram API error: {e}")
            print(f"Error details: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Reel upload error: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False
    
    def upload_story(self, media_path: str, story_type: str = "auto") -> bool:
        """
        Upload story to Instagram
        
        Args:
            media_path (str): Path to image or video file
            story_type (str): "photo", "video", or "auto" to detect
        """
        if not os.path.exists(media_path):
            print(f"❌ Media file not found: {media_path}")
            return False
        
        try:
            print(f"📱 Uploading story: {os.path.basename(media_path)}")
            
            # Detect media type if auto
            if story_type == "auto":
                file_extension = Path(media_path).suffix.lower()
                if file_extension in ['.jpg', '.jpeg', '.png']:
                    story_type = "photo"
                elif file_extension in ['.mp4', '.mov']:
                    story_type = "video"
                else:
                    print(f"❌ Unsupported file type: {file_extension}")
                    return False
            
            # Upload story
            if story_type == "photo":
                media = self.client.photo_upload_to_story(media_path)
            elif story_type == "video":
                media = self.client.video_upload_to_story(media_path)
            else:
                print(f"❌ Invalid story type: {story_type}")
                return False
            
            if media:
                print(f"✅ Story uploaded successfully!")
                print(f"📱 Story ID: {media.id}")
                return True
            else:
                print("❌ Story upload failed")
                return False
                
        except Exception as e:
            print(f"❌ Story upload error: {e}")
            return False
    
    def get_media_info(self, media_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a media post"""
        try:
            media = self.client.media_info(media_id)
            if media:
                return {
                    "id": media.id,
                    "code": media.code,
                    "caption": media.caption_text,
                    "like_count": media.like_count,
                    "comment_count": media.comment_count,
                    "media_type": media.media_type,
                    "taken_at": media.taken_at,
                    "url": f"https://www.instagram.com/p/{media.code}/"
                }
        except Exception as e:
            print(f"Error getting media info: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        try:
            user_info = self.client.account_info()
            return user_info is not None
        except:
            return False
    
    def ensure_authenticated_for_upload(self) -> bool:
        """
        Ensure client is properly authenticated for upload operations
        Following instagrapi documentation pattern
        """
        print("🔍 Verifying authentication before upload...")
        
        # First check if we have basic credentials
        if not self.username or not self.password:
            print("❌ No credentials available")
            return False
        
        try:
            # Test authentication by getting account info
            user_info = self.client.account_info()
            if user_info and getattr(user_info, 'username', None) == self.username:
                print(f"✅ Already authenticated as @{self.username}")
                return True
        except (LoginRequired, ClientError):
            print("⚠️ Session expired or not authenticated")
        except Exception as e:
            print(f"⚠️ Auth check failed: {e}")
        
        # Need to re-authenticate
        print(f"🔐 Performing fresh login for upload...")
        try:
            # Fresh login following instagrapi pattern
            success = self.client.login(self.username, self.password)
            
            if success:
                # Verify login worked
                user_info = self.client.account_info()
                if user_info:
                    print(f"✅ Fresh login successful for @{self.username}")
                    
                    # Save session
                    if self.session_file:
                        self.client.dump_settings(self.session_file)
                        print(f"💾 Session updated")
                    
                    return True
                else:
                    print("❌ Login succeeded but cannot get account info")
                    return False
            else:
                print("❌ Login failed")
                return False
                
        except Exception as e:
            print(f"❌ Fresh login error: {e}")
            return False
    
    def re_authenticate_and_retry(self) -> bool:
        """Re-authenticate for retry attempts"""
        print("🔄 Re-authenticating for retry...")
        
        # Reset client to clear any bad state
        self.client = Client()
        self.client.delay_range = [1, 3]
        
        # Configure client settings
        self.client.request_timeout = 10
        self.client.country_code = 1
        self.client.locale = "en_US"
        
        # Attempt fresh login
        try:
            success = self.client.login(self.username, self.password)
            if success:
                user_info = self.client.account_info()
                if user_info:
                    print(f"✅ Re-authentication successful")
                    return True
            
            print("❌ Re-authentication failed")
            return False
            
        except Exception as e:
            print(f"❌ Re-authentication error: {e}")
            return False
    
    def logout(self):
        """Logout from Instagram"""
        try:
            self.client.logout()
            print("✅ Logged out successfully")
        except Exception as e:
            print(f"⚠️ Logout error: {e}")
    
    def validate_video_for_upload(self, video_path: str, content_type: str = "reel") -> Dict[str, Any]:
        """
        Validate video file for Instagram upload
        
        Args:
            video_path (str): Path to video file
            content_type (str): Type of content (reel, video, story)
        
        Returns:
            Dict with validation results
        """
        try:
            # Check file exists and get basic info
            if not os.path.exists(video_path):
                return {"valid": False, "error": "File not found"}
            
            file_size = os.path.getsize(video_path)
            file_size_mb = file_size / (1024 * 1024)
            
            # Check file extension
            file_ext = Path(video_path).suffix.lower()
            if file_ext not in ['.mp4', '.mov']:
                return {"valid": False, "error": f"Unsupported format {file_ext}. Use .mp4 or .mov"}
            
            # Get upload limits
            limits = self.get_upload_limits()
            content_limits = limits.get(content_type, limits["reel"])
            
            # Check file size
            if file_size_mb > content_limits["max_size_mb"]:
                return {
                    "valid": False, 
                    "error": f"File too large: {file_size_mb:.1f}MB > {content_limits['max_size_mb']}MB"
                }
            
            # Try to get video info using moviepy if available
            try:
                from moviepy.editor import VideoFileClip
                with VideoFileClip(video_path) as clip:
                    duration = clip.duration
                    width, height = clip.size
                    fps = clip.fps
                    
                    # Check duration
                    if duration > content_limits["max_duration_seconds"]:
                        return {
                            "valid": False,
                            "error": f"Video too long: {duration:.1f}s > {content_limits['max_duration_seconds']}s"
                        }
                    
                    video_info = f"{width}x{height}, {duration:.1f}s, {fps:.1f}fps, {file_size_mb:.1f}MB"
                    
            except ImportError:
                # MoviePy not available, basic validation only
                video_info = f"{file_size_mb:.1f}MB"
            except Exception as e:
                # Video file might be corrupted
                return {"valid": False, "error": f"Cannot read video file: {e}"}
            
            return {
                "valid": True,
                "info": video_info,
                "size_mb": file_size_mb
            }
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {e}"}

    def get_upload_limits(self) -> Dict[str, Any]:
        """Get Instagram upload limits and recommendations"""
        return {
            "photo": {
                "max_size_mb": 8,
                "recommended_resolution": "1080x1080",
                "aspect_ratios": ["1:1", "4:5", "16:9"],
                "formats": [".jpg", ".jpeg", ".png"]
            },
            "video": {
                "max_size_mb": 100,
                "max_duration_seconds": 60,
                "recommended_resolution": "1080x1920",
                "aspect_ratios": ["9:16", "1:1", "4:5"],
                "formats": [".mp4", ".mov"]
            },
            "reel": {
                "max_size_mb": 100,
                "max_duration_seconds": 90,
                "recommended_resolution": "1080x1920",
                "aspect_ratios": ["9:16"],
                "formats": [".mp4", ".mov"]
            },
            "story": {
                "max_size_mb": 100,
                "max_duration_seconds": 15,
                "recommended_resolution": "1080x1920",
                "aspect_ratios": ["9:16"],
                "formats": [".jpg", ".jpeg", ".png", ".mp4", ".mov"]
            }
        }


def test_instagram_connection(username: str, password: str) -> bool:
    """Test Instagram connection and authentication"""
    try:
        api = InstagramAPI(username, password)
        if api.authenticate():
            user_info = api.get_user_info()
            if user_info:
                print(f"✅ Connection test successful!")
                print(f"Account: @{user_info['username']}")
                print(f"Followers: {user_info['follower_count']}")
                return True
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    print("Instagram API Module")
    print("====================")
    
    # You can test the connection here
    # username = "your_username"
    # password = "your_password"
    # test_instagram_connection(username, password)