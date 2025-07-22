from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class LoginCredentials(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class PlatformInfo(BaseModel):
    name: str
    icon: str
    active: bool
    account_count: int

class ClipsStats(BaseModel):
    available_clips: int
    clips_per_week: int
    weeks_of_content: float
    status: str  # "healthy", "low", "critical"

class AccountInfo(BaseModel):
    name: str
    active: bool
    authenticated: bool
    clip_folder: str
    description: str
    tags: str
    title: str
    category_id: str
    clip_duration: int
    schedule: Dict[str, List[str]]
    clips_stats: ClipsStats

class CreateAccountRequest(BaseModel):
    name: str
    active: bool = True
    description: Optional[str] = None
    tags: Optional[str] = None
    title: Optional[str] = None
    category_id: Optional[str] = None
    clip_duration: Optional[int] = 57
    # Re-authentication options
    use_existing_credentials: bool = False
    # YouTube specific
    client_secrets_content: Optional[str] = None
    # TikTok specific
    client_key: Optional[str] = None
    client_secret: Optional[str] = None
    # Instagram specific
    access_token: Optional[str] = None
    # Twitter specific
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token_key: Optional[str] = None
    access_token_secret: Optional[str] = None

class UpdateAccountRequest(BaseModel):
    active: Optional[bool] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    title: Optional[str] = None
    category_id: Optional[str] = None
    clip_duration: Optional[int] = None
    schedule: Optional[Dict[str, List[str]]] = None

class GenerateClipsFromUrlRequest(BaseModel):
    url: str
    mobile_format: bool = True

class TaskStatus(BaseModel):
    task_id: str
    status: str  # "processing", "completed", "failed"
    progress: int  # 0-100
    message: str

class DashboardStats(BaseModel):
    total_accounts: int
    active_accounts: int
    platforms_active: int
    total_platforms: int

class ReauthResponse(BaseModel):
    success: bool
    authenticated: bool
    auth_message: str
    message: str