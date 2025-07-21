"""
TikTok API Integration Module
Real TikTok upload functionality using TikTok for Developers API
"""

import requests
import json
import os
import time
import hashlib
import hmac
from urllib.parse import urlencode, quote
from datetime import datetime
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.parse


class TikTokAPI:
    """
    TikTok API wrapper for content creation and upload
    Based on TikTok for Developers API v1.3
    """
    
    def __init__(self, client_key, client_secret, redirect_uri="http://localhost:8080/callback"):
        self.client_key = client_key
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        
        # TikTok API endpoints
        self.base_url = "https://open-api.tiktok.com"
        self.auth_url = "https://www.tiktok.com/auth/authorize/"
        self.token_url = f"{self.base_url}/oauth/access_token/"
        self.refresh_url = f"{self.base_url}/oauth/refresh_token/"
        self.upload_url = f"{self.base_url}/share/video/upload/"
        self.user_info_url = f"{self.base_url}/user/info/"
        
        # Scopes needed for video upload
        self.scopes = [
            "user.info.basic",
            "video.upload",
            "video.publish"
        ]
    
    def get_authorization_url(self):
        """
        Generate authorization URL for OAuth2 flow
        """
        params = {
            "client_key": self.client_key,
            "scope": ",".join(self.scopes),
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "state": self._generate_state()
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        return auth_url
    
    def _generate_state(self):
        """Generate random state for OAuth2 security"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def authenticate(self, authorization_code):
        """
        Exchange authorization code for access token
        """
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            if "data" in token_data:
                self.access_token = token_data["data"]["access_token"]
                self.refresh_token = token_data["data"]["refresh_token"]
                self.user_id = token_data["data"]["open_id"]
                
                # Save tokens
                self._save_tokens()
                return True
            else:
                print(f"Authentication failed: {token_data}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Authentication error: {e}")
            return False
    
    def refresh_access_token(self):
        """
        Refresh the access token using refresh token
        """
        if not self.refresh_token:
            return False
        
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        
        try:
            response = requests.post(self.refresh_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            if "data" in token_data:
                self.access_token = token_data["data"]["access_token"]
                self.refresh_token = token_data["data"]["refresh_token"]
                self._save_tokens()
                return True
            else:
                print(f"Token refresh failed: {token_data}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Token refresh error: {e}")
            return False
    
    def _save_tokens(self):
        """Save tokens to file"""
        if not hasattr(self, 'account_name'):
            self.account_name = "default"
            
        token_dir = "tiktok_automation/account_tokens"
        os.makedirs(token_dir, exist_ok=True)
        
        token_file = os.path.join(token_dir, f"token_{self.account_name}.json")
        
        token_data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "user_id": self.user_id,
            "client_key": self.client_key,
            "saved_at": datetime.now().isoformat()
        }
        
        with open(token_file, 'w') as f:
            json.dump(token_data, f, indent=4)
    
    def load_tokens(self, account_name):
        """Load saved tokens"""
        self.account_name = account_name
        token_file = f"tiktok_automation/account_tokens/token_{account_name}.json"
        
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r') as f:
                    token_data = json.load(f)
                
                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                self.user_id = token_data.get("user_id")
                
                return True
            except Exception as e:
                print(f"Error loading tokens: {e}")
                return False
        
        return False
    
    def get_user_info(self):
        """
        Get user information
        """
        if not self.access_token:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "fields": "open_id,union_id,avatar_url,display_name"
        }
        
        try:
            response = requests.get(self.user_info_url, headers=headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"User info error: {e}")
            return None
    
    def upload_video(self, video_path, title, description="", privacy_level="PUBLIC_TO_EVERYONE", 
                    disable_duet=False, disable_comment=False, disable_stitch=False):
        """
        Upload video to TikTok
        
        Args:
            video_path (str): Path to video file
            title (str): Video title
            description (str): Video description
            privacy_level (str): Privacy setting
            disable_duet (bool): Disable duet feature
            disable_comment (bool): Disable comments
            disable_stitch (bool): Disable stitch feature
        """
        if not self.access_token:
            print("No access token available")
            return False
        
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            return False
        
        # Step 1: Initialize upload
        upload_init = self._initialize_upload()
        if not upload_init:
            return False
        
        upload_id = upload_init.get("upload_id")
        upload_url = upload_init.get("upload_url")
        
        # Step 2: Upload video file
        upload_success = self._upload_video_file(upload_url, video_path)
        if not upload_success:
            return False
        
        # Step 3: Publish video
        publish_success = self._publish_video(
            upload_id, title, description, privacy_level,
            disable_duet, disable_comment, disable_stitch
        )
        
        return publish_success
    
    def _initialize_upload(self):
        """Initialize video upload"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        init_url = f"{self.base_url}/share/video/init/"
        
        try:
            response = requests.post(init_url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("data"):
                return result["data"]
            else:
                print(f"Upload initialization failed: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Upload initialization error: {e}")
            return None
    
    def _upload_video_file(self, upload_url, video_path):
        """Upload video file to TikTok servers"""
        try:
            with open(video_path, 'rb') as video_file:
                files = {'video': video_file}
                
                response = requests.post(upload_url, files=files)
                response.raise_for_status()
                
                return True
                
        except requests.exceptions.RequestException as e:
            print(f"Video file upload error: {e}")
            return False
        except Exception as e:
            print(f"File handling error: {e}")
            return False
    
    def _publish_video(self, upload_id, title, description, privacy_level,
                      disable_duet, disable_comment, disable_stitch):
        """Publish the uploaded video"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        publish_url = f"{self.base_url}/share/video/publish/"
        
        data = {
            "upload_id": upload_id,
            "post_info": {
                "title": title,
                "description": description,
                "privacy_level": privacy_level,
                "disable_duet": disable_duet,
                "disable_comment": disable_comment,
                "disable_stitch": disable_stitch
            }
        }
        
        try:
            response = requests.post(publish_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("data"):
                publish_id = result["data"].get("publish_id")
                print(f"Video published successfully! Publish ID: {publish_id}")
                return True
            else:
                print(f"Video publish failed: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Video publish error: {e}")
            return False
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.access_token is not None
    
    def revoke_access(self):
        """Revoke access token"""
        self.access_token = None
        self.refresh_token = None
        self.user_id = None


class TikTokOAuthHandler(BaseHTTPRequestHandler):
    """HTTP server handler for OAuth callback"""
    
    def do_GET(self):
        """Handle GET request for OAuth callback"""
        if self.path.startswith('/callback'):
            # Parse the authorization code from the callback
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            if 'code' in query_params:
                self.server.auth_code = query_params['code'][0]
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                success_html = """
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #25f4ee;">✅ TikTok Authentication Successful!</h1>
                    <p>You can now close this window and return to the application.</p>
                    <script>
                        setTimeout(function() { window.close(); }, 3000);
                    </script>
                </body>
                </html>
                """
                self.wfile.write(success_html.encode())
            else:
                # Send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                error_html = """
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #ff0050;">❌ Authentication Failed</h1>
                    <p>Please try again.</p>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        return


def start_oauth_server(port=8080):
    """Start OAuth callback server"""
    server = HTTPServer(('localhost', port), TikTokOAuthHandler)
    server.auth_code = None
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    return server


def authenticate_with_browser(api_instance):
    """
    Complete OAuth flow with browser
    """
    print("🚀 Starting TikTok authentication...")
    
    # Start OAuth server
    server = start_oauth_server()
    
    try:
        # Get authorization URL and open browser
        auth_url = api_instance.get_authorization_url()
        print(f"📱 Opening browser for TikTok authentication...")
        print(f"🔗 Auth URL: {auth_url}")
        
        webbrowser.open(auth_url)
        
        # Wait for authorization code
        print("⏳ Waiting for authorization...")
        timeout = 120  # 2 minutes timeout
        elapsed = 0
        
        while server.auth_code is None and elapsed < timeout:
            time.sleep(1)
            elapsed += 1
        
        if server.auth_code:
            print("✅ Authorization code received!")
            
            # Exchange code for tokens
            success = api_instance.authenticate(server.auth_code)
            
            if success:
                print("🎉 TikTok authentication successful!")
                user_info = api_instance.get_user_info()
                if user_info and "data" in user_info:
                    username = user_info["data"].get("display_name", "Unknown")
                    print(f"👤 Authenticated as: {username}")
                return True
            else:
                print("❌ Failed to exchange authorization code for tokens")
                return False
        else:
            print("⏰ Authentication timeout - please try again")
            return False
            
    finally:
        server.shutdown()
        print("🔒 OAuth server stopped")
    
    return False