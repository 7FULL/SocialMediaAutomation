from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import os
import sys
import json
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import asyncio
import threading
from pathlib import Path
from contextlib import asynccontextmanager

# Add the parent directory to the path so we can import from core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.youtube_automation import YouTubeAutomation
except ImportError:
    print("Warning: YouTube automation not available")
    YouTubeAutomation = None

try:
    from core.tiktok_automation_enhanced import TikTokAutomation
    TIKTOK_ENHANCED_AVAILABLE = True
except ImportError:
    try:
        from core.tiktok_automation import TikTokAutomation
        TIKTOK_ENHANCED_AVAILABLE = False
    except ImportError:
        print("Warning: TikTok automation not available")
        TikTokAutomation = None

import json

def load_config():
    """Load configuration from config.json"""
    try:
        config_path = "config/config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default config if not exists
            default_config = {
                "YouTube": {"accounts": {}, "auto_upload": False},
                "TikTok": {"accounts": {}, "auto_upload": False},
                "Instagram": {"accounts": {}, "auto_upload": False},
                "Twitter": {"accounts": {}, "auto_upload": False}
            }
            save_config(default_config)
            return default_config
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def save_config(config):
    """Save configuration to config.json"""
    try:
        config_path = "config/config.json"
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

from models import *
from auth import verify_token, create_access_token
from scheduler import SchedulerService
from settings_manager import SettingsManager, BackupManager, NotificationManager, PerformanceMonitor, SecurityManager

# Platform-specific authentication functions
async def handle_youtube_authentication(account: CreateAccountRequest, use_existing_secrets=False):
    """Handle YouTube authentication with client secrets"""
    try:
        secrets_dir = f"youtube_automation/account_secrets"
        secrets_file = f"{secrets_dir}/client_secrets_{account.name}.json"
        
        if use_existing_secrets:
            # Try to use existing secrets file
            if not os.path.exists(secrets_file):
                return False, "No existing OAuth credentials found for this account. Please upload new credentials."
        else:
            # Require new client secrets content
            if not account.client_secrets_content:
                return False, "Client secrets file content is required for YouTube"
            
            # Create account secrets directory
            os.makedirs(secrets_dir, exist_ok=True)
            
            # Save client secrets file
            with open(secrets_file, 'w') as f:
                f.write(account.client_secrets_content)
        
        # Authenticate with YouTube
        if YouTubeAutomation:
            authenticated = YouTubeAutomation.authenticate_youtube_account(account.name)
            if authenticated:
                return True, "YouTube authentication successful using " + ("existing" if use_existing_secrets else "new") + " credentials"
            else:
                return False, "YouTube authentication failed - check credentials"
        else:
            return False, "YouTube automation not available"
            
    except Exception as e:
        return False, f"YouTube authentication error: {str(e)}"

async def handle_tiktok_authentication(account: CreateAccountRequest):
    """Handle TikTok authentication with API keys"""
    try:
        if not account.client_key or not account.client_secret:
            return False, "Client key and secret are required for TikTok"
        
        # Create account config directory
        config_dir = f"tiktok_automation/account_config"
        os.makedirs(config_dir, exist_ok=True)
        
        # Save TikTok credentials
        config_file = f"{config_dir}/tiktok_config_{account.name}.json"
        tiktok_config = {
            "client_key": account.client_key,
            "client_secret": account.client_secret,
            "account_name": account.name
        }
        
        with open(config_file, 'w') as f:
            json.dump(tiktok_config, f, indent=2)
        
        # Authenticate with TikTok
        if TikTokAutomation:
            authenticated = TikTokAutomation.authenticate_tiktok_account(account.name)
            if authenticated:
                return True, "TikTok authentication successful"
            else:
                return False, "TikTok authentication failed - check credentials"
        else:
            return False, "TikTok automation not available"
            
    except Exception as e:
        return False, f"TikTok authentication error: {str(e)}"

async def handle_instagram_authentication(account: CreateAccountRequest):
    """Handle Instagram authentication with access token"""
    try:
        if not account.access_token:
            return False, "Access token is required for Instagram"
        
        # Create account config directory
        config_dir = f"instagram_automation/account_config"
        os.makedirs(config_dir, exist_ok=True)
        
        # Save Instagram credentials
        config_file = f"{config_dir}/instagram_config_{account.name}.json"
        instagram_config = {
            "access_token": account.access_token,
            "account_name": account.name
        }
        
        with open(config_file, 'w') as f:
            json.dump(instagram_config, f, indent=2)
        
        return True, "Instagram configuration saved (authentication pending implementation)"
        
    except Exception as e:
        return False, f"Instagram authentication error: {str(e)}"

async def handle_twitter_authentication(account: CreateAccountRequest):
    """Handle Twitter authentication with API keys"""
    try:
        if not all([account.api_key, account.api_secret, account.access_token_key, account.access_token_secret]):
            return False, "All API keys are required for Twitter"
        
        # Create account config directory
        config_dir = f"twitter_automation/account_config"
        os.makedirs(config_dir, exist_ok=True)
        
        # Save Twitter credentials
        config_file = f"{config_dir}/twitter_config_{account.name}.json"
        twitter_config = {
            "api_key": account.api_key,
            "api_secret": account.api_secret,
            "access_token_key": account.access_token_key,
            "access_token_secret": account.access_token_secret,
            "account_name": account.name
        }
        
        with open(config_file, 'w') as f:
            json.dump(twitter_config, f, indent=2)
        
        return True, "Twitter configuration saved (authentication pending implementation)"
        
    except Exception as e:
        return False, f"Twitter authentication error: {str(e)}"

# Global variables
config_data = {}
scheduler_service = None
active_tasks = {}

# Settings management
settings_manager = None
backup_manager = None
notification_manager = None
performance_monitor = None
security_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    global config_data, scheduler_service, settings_manager, backup_manager, notification_manager, performance_monitor, security_manager
    
    # Load configuration
    config_data = load_config()
    
    # Initialize settings management
    settings_manager = SettingsManager()
    backup_manager = BackupManager(settings_manager)
    notification_manager = NotificationManager(settings_manager)
    performance_monitor = PerformanceMonitor(settings_manager)
    security_manager = SecurityManager(settings_manager)
    
    # Initialize scheduler service
    scheduler_service = SchedulerService(config_data)
    
    # Create necessary directories
    os.makedirs("web_app/uploads", exist_ok=True)
    os.makedirs("web_app/logs", exist_ok=True)
    os.makedirs("web_app/config", exist_ok=True)
    
    print("🚀 Social Media Automation API started successfully!")
    
    yield
    
    # Shutdown
    if scheduler_service:
        await scheduler_service.stop_all_schedulers()
    print("🛑 Social Media Automation API stopped")

app = FastAPI(
    title="Social Media Automation API",
    description="Professional social media automation suite with multi-platform support",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Mount static files
app.mount("/static", StaticFiles(directory="E:\CODING\Python\SocialMediaAutomation\web_app/frontend/build\static"), name="static")

# Authentication endpoints
@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: LoginCredentials):
    """Authenticate user and return JWT token"""
    # Simple authentication - in production, use proper user management
    if credentials.username == "admin" and credentials.password == "admin123":
        access_token = create_access_token(data={"sub": credentials.username})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/auth/verify")
async def verify_auth(token: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    payload = verify_token(token.credentials)
    return {"valid": True, "user": payload.get("sub")}

# Configuration endpoints
@app.get("/api/config", response_model=Dict)
async def get_config(token: HTTPAuthorizationCredentials = Depends(security)):
    """Get application configuration"""
    verify_token(token.credentials)
    return config_data

@app.post("/api/config")
async def save_config_endpoint(
    config: Dict,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Save application configuration"""
    verify_token(token.credentials)
    global config_data
    config_data = config
    save_config(config_data)
    return {"message": "Configuration saved successfully"}

# Social Media Platform endpoints
@app.get("/api/platforms", response_model=List[PlatformInfo])
async def get_platforms(token: HTTPAuthorizationCredentials = Depends(security)):
    """Get available social media platforms"""
    verify_token(token.credentials)
    
    platforms = [
        PlatformInfo(
            name="YouTube",
            icon="🎥",
            active=config_data.get("YouTube", {}).get("auto_upload", False),
            account_count=len(config_data.get("YouTube", {}).get("accounts", {}))
        ),
        PlatformInfo(
            name="TikTok",
            icon="🎵",
            active=config_data.get("TikTok", {}).get("auto_upload", False),
            account_count=len(config_data.get("TikTok", {}).get("accounts", {}))
        ),
        PlatformInfo(
            name="Instagram",
            icon="📸",
            active=config_data.get("Instagram", {}).get("auto_upload", False),
            account_count=len(config_data.get("Instagram", {}).get("accounts", {}))
        ),
        PlatformInfo(
            name="Twitter",
            icon="🐦",
            active=config_data.get("Twitter", {}).get("auto_upload", False),
            account_count=len(config_data.get("Twitter", {}).get("accounts", {}))
        )
    ]
    
    return platforms

@app.post("/api/platforms/{platform_name}/toggle")
async def toggle_platform_auto_upload(
    platform_name: str,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Toggle auto-upload for a platform"""
    verify_token(token.credentials)
    
    if platform_name not in config_data:
        config_data[platform_name] = {"accounts": {}}
    
    current_status = config_data[platform_name].get("auto_upload", False)
    config_data[platform_name]["auto_upload"] = not current_status
    
    # Update scheduler
    if not current_status:
        await scheduler_service.start_platform_scheduler(platform_name)
    else:
        await scheduler_service.stop_platform_scheduler(platform_name)
    
    save_config(config_data)
    
    return {"message": f"Auto-upload {'enabled' if not current_status else 'disabled'} for {platform_name}"}

def count_clips_in_folder(folder_path: str) -> int:
    """Count video clips in a folder"""
    if not os.path.exists(folder_path):
        return 0
    
    clips_folder = os.path.join(folder_path, "clips")
    if not os.path.exists(clips_folder):
        return 0
    
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'}
    clip_count = 0
    
    try:
        for file in os.listdir(clips_folder):
            if os.path.splitext(file.lower())[1] in video_extensions:
                clip_count += 1
    except Exception as e:
        print(f"Error counting clips in {clips_folder}: {e}")
        return 0
    
    return clip_count

def calculate_clips_needed_per_week(schedule: dict) -> int:
    """Calculate how many clips are needed per week based on schedule"""
    total_uploads_per_week = 0
    
    for day, times in schedule.items():
        if isinstance(times, list):
            total_uploads_per_week += len(times)
    
    return total_uploads_per_week

# Account management endpoints
@app.get("/api/platforms/{platform_name}/accounts", response_model=List[AccountInfo])
async def get_accounts(
    platform_name: str,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Get accounts for a specific platform"""
    verify_token(token.credentials)
    
    platform_config = config_data.get(platform_name, {})
    accounts = platform_config.get("accounts", {})
    
    account_list = []
    for name, data in accounts.items():
        # Count available clips
        clip_folder = data.get("clip_folder", "")
        available_clips = count_clips_in_folder(clip_folder)
        
        # Calculate clips needed per week
        schedule = data.get("schedule", {})
        clips_per_week = calculate_clips_needed_per_week(schedule)
        
        # Calculate how many weeks of content we have
        weeks_of_content = available_clips / clips_per_week if clips_per_week > 0 else 0
        
        # Determine status
        if weeks_of_content >= 2:
            status = "healthy"
        elif weeks_of_content >= 1:
            status = "low"
        else:
            status = "critical"
        
        clips_stats = ClipsStats(
            available_clips=available_clips,
            clips_per_week=clips_per_week,
            weeks_of_content=round(weeks_of_content, 1),
            status=status
        )
        
        account_list.append(AccountInfo(
            name=name,
            active=data.get("active", True),
            authenticated=data.get("authenticated", False),
            clip_folder=clip_folder,
            description=data.get("description", ""),
            tags=data.get("tags", ""),
            title=data.get("title", ""),
            category_id=data.get("category_id", ""),
            clip_duration=data.get("clip_duration", 57),
            schedule=schedule,
            clips_stats=clips_stats
        ))
    
    return account_list

@app.post("/api/platforms/{platform_name}/accounts")
async def create_account(
    platform_name: str,
    account: CreateAccountRequest,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new account for a platform"""
    verify_token(token.credentials)
    
    if platform_name not in config_data:
        config_data[platform_name] = {"accounts": {}, "auto_upload": False}
    
    # Handle platform-specific authentication
    authenticated = False
    auth_message = ""
    
    try:
        if platform_name == "YouTube":
            authenticated, auth_message = await handle_youtube_authentication(account, False)
        elif platform_name == "TikTok":
            authenticated, auth_message = await handle_tiktok_authentication(account)
        elif platform_name == "Instagram":
            authenticated, auth_message = await handle_instagram_authentication(account)
        elif platform_name == "Twitter":
            authenticated, auth_message = await handle_twitter_authentication(account)
        else:
            authenticated = True  # Mock authentication for other platforms
            auth_message = "Platform authentication not implemented"
    except Exception as e:
        authenticated = False
        auth_message = f"Authentication failed: {str(e)}"
    
    # Create clips folder
    clips_folder = f"{platform_name.lower()}_automation/account_clips/{account.name}"
    os.makedirs(clips_folder, exist_ok=True)
    
    # Default schedule
    schedule = {
        "Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [],
        "Friday": [], "Saturday": [], "Sunday": []
    }
    
    # Add account to config
    config_data[platform_name]["accounts"][account.name] = {
        "token_path": "",
        "active": account.active,
        "clip_folder": clips_folder,
        "schedule": schedule,
        "authenticated": authenticated,
        "description": account.description or "",
        "tags": account.tags or "",
        "title": account.title or "",
        "category_id": account.category_id or "",
        "clip_duration": account.clip_duration or 57
    }
    
    save_config(config_data)
    
    return {
        "message": f"Account {account.name} created successfully", 
        "authenticated": authenticated,
        "auth_message": auth_message
    }

@app.put("/api/platforms/{platform_name}/accounts/{account_name}")
async def update_account(
    platform_name: str,
    account_name: str,
    account: UpdateAccountRequest,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Update an existing account"""
    verify_token(token.credentials)
    
    if platform_name not in config_data or account_name not in config_data[platform_name]["accounts"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account_data = config_data[platform_name]["accounts"][account_name]
    
    # Update account data
    if account.active is not None:
        account_data["active"] = account.active
    if account.description is not None:
        account_data["description"] = account.description
    if account.tags is not None:
        account_data["tags"] = account.tags
    if account.title is not None:
        account_data["title"] = account.title
    if account.category_id is not None:
        account_data["category_id"] = account.category_id
    if account.clip_duration is not None:
        account_data["clip_duration"] = account.clip_duration
    if account.schedule is not None:
        account_data["schedule"] = account.schedule
    
    save_config(config_data)
    
    return {"message": f"Account {account_name} updated successfully"}

@app.delete("/api/platforms/{platform_name}/accounts/{account_name}")
async def delete_account(
    platform_name: str,
    account_name: str,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete an account"""
    verify_token(token.credentials)
    
    if platform_name not in config_data or account_name not in config_data[platform_name]["accounts"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account_data = config_data[platform_name]["accounts"][account_name]
    
    # Remove clips folder
    clips_folder = account_data.get("clip_folder", "")
    if clips_folder and os.path.exists(clips_folder):
        import shutil
        shutil.rmtree(clips_folder)
    
    # Remove account from config
    del config_data[platform_name]["accounts"][account_name]
    
    save_config(config_data)
    
    return {"message": f"Account {account_name} deleted successfully"}

# Content generation endpoints
@app.post("/api/platforms/{platform_name}/accounts/{account_name}/generate-from-url")
async def generate_clips_from_url(
    platform_name: str,
    account_name: str,
    request: GenerateClipsFromUrlRequest,
    background_tasks: BackgroundTasks,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate clips from a YouTube URL"""
    verify_token(token.credentials)
    
    if platform_name not in config_data or account_name not in config_data[platform_name]["accounts"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account_data = config_data[platform_name]["accounts"][account_name]
    task_id = f"{platform_name}_{account_name}_{datetime.now().timestamp()}"
    
    # Start background task
    background_tasks.add_task(
        generate_clips_from_url_task,
        task_id,
        request.url,
        account_data["clip_folder"],
        account_data.get("clip_duration", 57),
        request.mobile_format
    )
    
    active_tasks[task_id] = {"status": "processing", "progress": 0, "message": "Starting..."}
    
    return {"task_id": task_id, "message": "Clip generation started"}

@app.post("/api/platforms/{platform_name}/accounts/{account_name}/generate-from-file")
async def generate_clips_from_file(
    platform_name: str,
    account_name: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mobile_format: bool = Form(True),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate clips from an uploaded file"""
    verify_token(token.credentials)
    
    if platform_name not in config_data or account_name not in config_data[platform_name]["accounts"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account_data = config_data[platform_name]["accounts"][account_name]
    task_id = f"{platform_name}_{account_name}_{datetime.now().timestamp()}"
    
    # Save uploaded file
    upload_path = f"web_app/uploads/{file.filename}"
    with open(upload_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Start background task
    background_tasks.add_task(
        generate_clips_from_file_task,
        task_id,
        upload_path,
        account_data["clip_folder"],
        account_data.get("clip_duration", 57),
        mobile_format
    )
    
    active_tasks[task_id] = {"status": "processing", "progress": 0, "message": "Starting..."}
    
    return {"task_id": task_id, "message": "Clip generation started"}

@app.get("/api/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Get task status and progress"""
    verify_token(token.credentials)
    
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return active_tasks[task_id]

# Upload endpoint
@app.post("/api/platforms/{platform_name}/accounts/{account_name}/upload")
async def upload_content(
    platform_name: str,
    account_name: str,
    background_tasks: BackgroundTasks,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload content for an account"""
    verify_token(token.credentials)
    
    if platform_name not in config_data or account_name not in config_data[platform_name]["accounts"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account_data = config_data[platform_name]["accounts"][account_name]
    task_id = f"upload_{platform_name}_{account_name}_{datetime.now().timestamp()}"
    
    # Start background upload task
    background_tasks.add_task(
        upload_content_task,
        task_id,
        platform_name,
        account_name,
        account_data
    )
    
    active_tasks[task_id] = {"status": "processing", "progress": 0, "message": "Starting upload..."}
    
    return {"task_id": task_id, "message": "Upload started"}

# Re-authentication endpoint
@app.post("/api/platforms/{platform_name}/accounts/{account_name}/reauth", response_model=ReauthResponse)
async def reauthenticate_account(
    platform_name: str,
    account_name: str,
    request: CreateAccountRequest,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Re-authenticate an existing account"""
    verify_token(token.credentials)
    
    config_data = load_config()
    
    if platform_name not in config_data:
        raise HTTPException(status_code=404, detail="Platform not found")
    
    if account_name not in config_data[platform_name]["accounts"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Get current account data
    account_data = config_data[platform_name]["accounts"][account_name]
    
    # Update the request with the account name to match existing account
    request.name = account_name
    
    # Handle platform-specific authentication
    authenticated = False
    auth_message = ""
    
    try:
        if platform_name == "YouTube":
            authenticated, auth_message = await handle_youtube_authentication(request, request.use_existing_credentials)
        elif platform_name == "TikTok":
            authenticated, auth_message = await handle_tiktok_authentication(request)
        elif platform_name == "Instagram":
            authenticated, auth_message = await handle_instagram_authentication(request)
        elif platform_name == "Twitter":
            authenticated, auth_message = await handle_twitter_authentication(request)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform_name}")
        
        # Update authentication status in config
        account_data["authenticated"] = authenticated
        
        # Update platform-specific auth data if provided
        if platform_name == "YouTube" and request.client_secrets_content:
            account_data["client_secrets_content"] = request.client_secrets_content
        elif platform_name == "TikTok" and request.client_key and request.client_secret:
            account_data["client_key"] = request.client_key
            account_data["client_secret"] = request.client_secret
        elif platform_name == "Instagram" and request.access_token:
            account_data["access_token"] = request.access_token
        elif platform_name == "Twitter" and all([request.api_key, request.api_secret, request.access_token_key, request.access_token_secret]):
            account_data.update({
                "api_key": request.api_key,
                "api_secret": request.api_secret,
                "access_token_key": request.access_token_key,
                "access_token_secret": request.access_token_secret
            })
        
        save_config(config_data)
        
        return {
            "success": True,
            "authenticated": authenticated,
            "auth_message": auth_message,
            "message": f"Re-authentication {'successful' if authenticated else 'failed'}"
        }
        
    except Exception as e:
        print(f"Re-authentication error for {platform_name}/{account_name}: {str(e)}")
        return {
            "success": False,
            "authenticated": False,
            "auth_message": f"Re-authentication failed: {str(e)}",
            "message": "Re-authentication failed"
        }

# Dashboard endpoints
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(token: HTTPAuthorizationCredentials = Depends(security)):
    """Get dashboard statistics"""
    verify_token(token.credentials)
    
    total_accounts = 0
    active_accounts = 0
    platforms_active = 0
    
    for platform_name, platform_data in config_data.items():
        if isinstance(platform_data, dict) and "accounts" in platform_data:
            accounts = platform_data["accounts"]
            total_accounts += len(accounts)
            active_accounts += sum(1 for acc in accounts.values() if acc.get("active", False))
            
            if platform_data.get("auto_upload", False):
                platforms_active += 1
    
    return {
        "total_accounts": total_accounts,
        "active_accounts": active_accounts,
        "platforms_active": platforms_active,
        "total_platforms": 4
    }

def convert_clip_to_mobile_format(clip, crop_position='center'):
    """
    Converts a clip to mobile format (9:16 aspect ratio)
    Args:
        clip: MoviePy VideoFileClip object
        crop_position: Position of cropping ('center', 'top', 'bottom')
    Returns:
        Converted clip optimized for mobile
    """
    # Target dimensions for mobile (9:16) - YouTube Shorts optimized
    target_width = 1080
    target_height = 1920
    target_ratio = target_height / target_width
    
    # Get current dimensions
    current_width = clip.w
    current_height = clip.h
    current_ratio = current_height / current_width
    
    if current_ratio < target_ratio:
        # Video is wider than mobile format - crop horizontally
        new_width = int(current_height / target_ratio)
        
        if crop_position == 'left':
            x_start = 0
        elif crop_position == 'right':
            x_start = current_width - new_width
        else:  # center
            x_center = current_width / 2
            x_start = int(x_center - new_width / 2)
        
        x_start = max(0, x_start)
        x_end = min(current_width, x_start + new_width)
        
        clip = clip.crop(x1=x_start, x2=x_end)
        
    elif current_ratio > target_ratio:
        # Video is taller than mobile format - crop vertically
        new_height = int(current_width * target_ratio)
        
        if crop_position == 'top':
            y_start = 0
        elif crop_position == 'bottom':
            y_start = current_height - new_height
        else:  # center with slight upward bias
            y_center = current_height / 2
            y_offset = current_height * 0.05  # 5% upward for better composition
            y_start = int(y_center - new_height / 2 - y_offset)
        
        y_start = max(0, y_start)
        y_end = min(current_height, y_start + new_height)
        
        clip = clip.crop(y1=y_start, y2=y_end)
    
    # Resize to exact target dimensions
    clip = clip.resize((target_width, target_height))
    
    return clip

# Background tasks
async def generate_clips_from_url_task(task_id: str, url: str, output_folder: str, clip_duration: int, mobile_format: bool = True):
    """Background task for generating clips from URL"""
    try:
        active_tasks[task_id] = {"status": "processing", "progress": 10, "message": "Downloading video..."}
        
        yta = YouTubeAutomation(url=url, output_path=output_folder)
        yta.download_video()
        
        active_tasks[task_id] = {"status": "processing", "progress": 40, "message": "Downloading audio..."}
        yta.download_audio()
        
        active_tasks[task_id] = {"status": "processing", "progress": 70, "message": "Combining video and audio..."}
        yta.combine_video_audio()
        
        active_tasks[task_id] = {"status": "processing", "progress": 90, "message": "Creating clips..."}
        yta.create_clips(mobile_format=mobile_format, clip_duration=clip_duration)
        
        active_tasks[task_id] = {"status": "completed", "progress": 100, "message": "Clips generated successfully!"}
        
    except Exception as e:
        active_tasks[task_id] = {"status": "failed", "progress": 0, "message": f"Error: {str(e)}"}

async def generate_clips_from_file_task(task_id: str, file_path: str, output_folder: str, clip_duration: int, mobile_format: bool = True):
    """Background task for generating clips from file"""
    try:
        active_tasks[task_id] = {"status": "processing", "progress": 20, "message": "Processing file..."}
        
        import shutil
        from moviepy.editor import VideoFileClip
        
        # Copy file to output folder
        base_name = os.path.basename(file_path)
        final_path = os.path.join(output_folder, f"{os.path.splitext(base_name)[0]}_final.mp4")
        shutil.copy2(file_path, final_path)
        
        active_tasks[task_id] = {"status": "processing", "progress": 60, "message": "Creating clips..."}
        
        # Create clips
        video = VideoFileClip(final_path)
        total_duration = int(video.duration)
        
        clips_folder = os.path.join(output_folder, "clips")
        os.makedirs(clips_folder, exist_ok=True)
        
        number_of_clips = len(os.listdir(clips_folder))
        
        for start in range(clip_duration, total_duration, clip_duration):
            end = min(start + clip_duration, total_duration)
            if (end - start) < clip_duration:
                break
            
            clip = video.subclip(start, end)
            
            # Apply mobile format conversion if enabled
            if mobile_format:
                clip = convert_clip_to_mobile_format(clip)
            
            number = start // clip_duration
            if number_of_clips > 0:
                number += number_of_clips
            
            out_path = os.path.join(clips_folder, f"clip_{number}.mp4")
            clip.write_videofile(out_path, codec='libx264', audio_codec='aac')
        
        video.close()
        
        # Clean up uploaded file
        os.remove(file_path)
        
        active_tasks[task_id] = {"status": "completed", "progress": 100, "message": "Clips generated successfully!"}
        
    except Exception as e:
        active_tasks[task_id] = {"status": "failed", "progress": 0, "message": f"Error: {str(e)}"}

async def upload_content_task(task_id: str, platform_name: str, account_name: str, account_data: dict):
    """Background task for uploading content"""
    try:
        active_tasks[task_id] = {"status": "processing", "progress": 50, "message": "Uploading content..."}
        
        if platform_name == "YouTube":
            yta = YouTubeAutomation(acc_data=account_data, account_name=account_name)
            yta.upload_and_log_short()
        elif platform_name == "TikTok":
            tta = TikTokAutomation(acc_data=account_data, account_name=account_name)
            tta.upload_and_log_short()
        else:
            raise Exception(f"Upload not implemented for {platform_name}")
        
        active_tasks[task_id] = {"status": "completed", "progress": 100, "message": "Content uploaded successfully!"}
        
    except Exception as e:
        active_tasks[task_id] = {"status": "failed", "progress": 0, "message": f"Error: {str(e)}"}

# Settings endpoints
@app.get("/api/settings")
async def get_settings(token: HTTPAuthorizationCredentials = Depends(security)):
    """Get all application settings"""
    verify_token(token.credentials)
    return settings_manager.get_settings()

@app.post("/api/settings")
async def save_settings(
    settings: Dict,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Save application settings"""
    verify_token(token.credentials)
    
    if settings_manager.save_settings(settings):
        # Reinitialize notification manager if email settings changed
        if 'notifications' in settings:
            global notification_manager
            notification_manager = NotificationManager(settings_manager)
        
        return {"message": "Settings saved successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save settings")

@app.put("/api/settings/{section}/{key}")
async def update_setting(
    section: str,
    key: str,
    value: Dict,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Update a specific setting"""
    verify_token(token.credentials)
    
    if settings_manager.update_setting(section, key, value.get('value')):
        return {"message": f"Setting {section}.{key} updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update setting")

# Backup endpoints
@app.post("/api/backup/create")
async def create_backup(
    include_videos: bool = False,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new backup"""
    verify_token(token.credentials)
    
    result = backup_manager.create_backup(include_videos)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["error"])

@app.get("/api/backup/list")
async def list_backups(token: HTTPAuthorizationCredentials = Depends(security)):
    """List all available backups"""
    verify_token(token.credentials)
    return backup_manager.list_backups()

@app.post("/api/backup/restore/{backup_filename}")
async def restore_backup(
    backup_filename: str,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Restore from a backup file"""
    verify_token(token.credentials)
    
    result = backup_manager.restore_backup(backup_filename)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["error"])

@app.delete("/api/backup/{backup_filename}")
async def delete_backup(
    backup_filename: str,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a backup file"""
    verify_token(token.credentials)
    
    try:
        backup_path = os.path.join(backup_manager.backup_dir, backup_filename)
        if os.path.exists(backup_path):
            os.remove(backup_path)
            return {"message": "Backup deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Backup file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Performance monitoring endpoints
@app.get("/api/performance/stats")
async def get_performance_stats(token: HTTPAuthorizationCredentials = Depends(security)):
    """Get current system performance statistics"""
    verify_token(token.credentials)
    return performance_monitor.get_system_stats()

@app.get("/api/performance/warnings")
async def get_performance_warnings(token: HTTPAuthorizationCredentials = Depends(security)):
    """Get performance warnings"""
    verify_token(token.credentials)
    return performance_monitor.check_performance_limits()

# Security endpoints
@app.post("/api/security/whitelist")
async def add_ip_to_whitelist(
    ip_data: Dict,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Add IP to whitelist"""
    verify_token(token.credentials)
    
    ip_address = ip_data.get('ip_address')
    if not ip_address:
        raise HTTPException(status_code=400, detail="IP address is required")
    
    if security_manager.add_to_whitelist(ip_address):
        return {"message": f"IP {ip_address} added to whitelist"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add IP to whitelist")

@app.delete("/api/security/whitelist/{ip_address}")
async def remove_ip_from_whitelist(
    ip_address: str,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Remove IP from whitelist"""
    verify_token(token.credentials)
    
    if security_manager.remove_from_whitelist(ip_address):
        return {"message": f"IP {ip_address} removed from whitelist"}
    else:
        raise HTTPException(status_code=500, detail="Failed to remove IP from whitelist")

@app.post("/api/security/password/check")
async def check_password_strength(
    password_data: Dict,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Check password strength"""
    verify_token(token.credentials)
    
    password = password_data.get('password')
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")
    
    return security_manager.verify_password_strength(password)

# Notification endpoints
@app.post("/api/notifications/test")
async def test_notification(
    test_data: Dict,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Send a test notification"""
    verify_token(token.credentials)
    
    notification_type = test_data.get('type', 'uploadSuccess')
    
    if notification_type == 'uploadSuccess':
        success = notification_manager.send_upload_success(
            "YouTube", "Test Account", "test_video_123"
        )
    elif notification_type == 'uploadFailure':
        success = notification_manager.send_upload_failure(
            "YouTube", "Test Account", "Authentication failed"
        )
    elif notification_type == 'weeklyReport':
        test_stats = {
            "total_uploads": 25,
            "successful_uploads": 23,
            "failed_uploads": 2,
            "success_rate": 92.0,
            "most_active_platform": "YouTube"
        }
        success = notification_manager.send_weekly_report(test_stats)
    else:
        raise HTTPException(status_code=400, detail="Invalid notification type")
    
    if success:
        return {"message": "Test notification sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send test notification")

@app.post("/api/notifications/weekly-report")
async def send_weekly_report(
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Send weekly report manually"""
    verify_token(token.credentials)
    
    # Get actual stats from your system
    # For now, using example data
    stats = {
        "total_uploads": 47,
        "successful_uploads": 44,
        "failed_uploads": 3,
        "success_rate": 93.6,
        "most_active_platform": "YouTube"
    }
    
    success = notification_manager.send_weekly_report(stats)
    
    if success:
        return {"message": "Weekly report sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send weekly report")

# Export/Import settings
@app.get("/api/settings/export")
async def export_settings(token: HTTPAuthorizationCredentials = Depends(security)):
    """Export settings as JSON"""
    verify_token(token.credentials)
    
    settings = settings_manager.get_settings()
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sma_settings_{timestamp}.json"
    
    return {
        "filename": filename,
        "data": settings,
        "timestamp": timestamp
    }

@app.post("/api/settings/import")
async def import_settings(
    settings: Dict,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Import settings from JSON"""
    verify_token(token.credentials)
    
    if settings_manager.save_settings(settings):
        # Reinitialize managers with new settings
        global notification_manager, performance_monitor, security_manager
        notification_manager = NotificationManager(settings_manager)
        performance_monitor = PerformanceMonitor(settings_manager)
        security_manager = SecurityManager(settings_manager)
        
        return {"message": "Settings imported successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to import settings")

# Serve React app
@app.get("/")
async def serve_react_app():
    """Serve the React application"""
    return FileResponse("web_app/frontend/build/index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)