import os
import json
import shutil
import zipfile
import smtplib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import psutil
import hashlib
from mailjet_rest import Client

class SettingsManager:
    def __init__(self, config_file="config/app_settings.json"):
        self.config_file = config_file
        self.config_dir = os.path.dirname(config_file)
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.default_settings = {
            "general": {
                "appName": "Social Media Automation Suite",
                "timezone": "UTC-5",
                "language": "en",
                "theme": "light",
                "autoSave": True,
                "maxConcurrentUploads": 3,
                "defaultClipDuration": 57,
                "retryAttempts": 3
            },
            "notifications": {
                "emailNotifications": True,
                "uploadSuccess": True,
                "uploadFailure": True,
                "systemUpdates": False,
                "maintenanceAlerts": True,
                "weeklyReports": True,
                "emailAddress": "admin@example.com",
                "mailjetApiKey": "",
                "mailjetSecretKey": ""
            },
            "security": {
                "sessionTimeout": 30,
                "requireStrongPasswords": True,
                "twoFactorAuth": False,
                "loginAttempts": 5,
                "ipWhitelist": [],
                "auditLogs": True,
                "encryptionEnabled": True,
                "allowedIPs": []
            },
            "performance": {
                "uploadBandwidth": 10,
                "downloadBandwidth": 50,
                "maxFileSize": 1024,
                "compressionQuality": 85,
                "parallelProcessing": True,
                "cacheSize": 2048,
                "cleanupInterval": 24,
                "monitorSystem": True
            },
            "backup": {
                "autoBackup": True,
                "backupInterval": "daily",
                "retentionDays": 30,
                "includeVideos": False,
                "backupLocation": "web_app/backups",
                "lastBackup": None
            }
        }
        
        self.settings = self.load_settings()
        
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create default if not exists"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_settings(self.default_settings, loaded_settings)
            else:
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def _merge_settings(self, defaults: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded settings with defaults"""
        result = defaults.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save settings to file"""
        try:
            self.settings = settings
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return self.settings
    
    def update_setting(self, section: str, key: str, value: Any) -> bool:
        """Update a specific setting"""
        try:
            if section in self.settings:
                self.settings[section][key] = value
                return self.save_settings(self.settings)
            return False
        except Exception as e:
            print(f"Error updating setting: {e}")
            return False
    
    def get_setting(self, section: str, key: str, default=None):
        """Get a specific setting value"""
        return self.settings.get(section, {}).get(key, default)

class BackupManager:
    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
        self.backup_dir = self.settings.get_setting('backup', 'backupLocation', 'web_app/backups')
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, include_videos: bool = None) -> Dict[str, Any]:
        """Create a backup of the application data"""
        try:
            if include_videos is None:
                include_videos = self.settings.get_setting('backup', 'includeVideos', False)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"sma_backup_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Backup configuration files
                self._add_to_zip(zipf, "config/", ["*.json"])
                
                # Backup account credentials
                self._add_to_zip(zipf, "youtube_automation/account_secrets/", ["*.json"])
                self._add_to_zip(zipf, "youtube_automation/account_tokens/", ["*.pickle"])
                self._add_to_zip(zipf, "tiktok_automation/account_config/", ["*.json"])
                
                # Backup logs
                self._add_to_zip(zipf, "youtube_automation/logs/", ["*.json"])
                self._add_to_zip(zipf, "web_app/logs/", ["*.log", "*.json"])
                
                # Backup video clips if requested
                if include_videos:
                    self._add_to_zip(zipf, "youtube_automation/account_clips/", ["*.mp4"])
                    self._add_to_zip(zipf, "tiktok_automation/account_clips/", ["*.mp4"])
            
            # Update last backup time
            self.settings.update_setting('backup', 'lastBackup', datetime.now().isoformat())
            
            backup_info = {
                "filename": backup_name,
                "path": backup_path,
                "size": os.path.getsize(backup_path),
                "timestamp": timestamp,
                "includes_videos": include_videos
            }
            
            # Clean old backups
            self._cleanup_old_backups()
            
            return {"success": True, "backup": backup_info}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _add_to_zip(self, zipf: zipfile.ZipFile, directory: str, patterns: List[str]):
        """Add files matching patterns from directory to zip"""
        try:
            if not os.path.exists(directory):
                return
                
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if any(file.endswith(pattern.replace('*', '')) for pattern in patterns):
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path)
                        zipf.write(file_path, arc_path)
        except Exception as e:
            print(f"Error adding {directory} to backup: {e}")
    
    def _cleanup_old_backups(self):
        """Remove backups older than retention period"""
        try:
            retention_days = self.settings.get_setting('backup', 'retentionDays', 30)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            for file in os.listdir(self.backup_dir):
                if file.startswith("sma_backup_") and file.endswith(".zip"):
                    file_path = os.path.join(self.backup_dir, file)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        print(f"Removed old backup: {file}")
        except Exception as e:
            print(f"Error cleaning old backups: {e}")
    
    def restore_backup(self, backup_file: str) -> Dict[str, Any]:
        """Restore from a backup file"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_file)
            if not os.path.exists(backup_path):
                return {"success": False, "error": "Backup file not found"}
            
            # Create restore point
            restore_point = self.create_backup(include_videos=False)
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall("./")
            
            return {
                "success": True, 
                "message": "Backup restored successfully",
                "restore_point": restore_point
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups"""
        backups = []
        try:
            for file in os.listdir(self.backup_dir):
                if file.startswith("sma_backup_") and file.endswith(".zip"):
                    file_path = os.path.join(self.backup_dir, file)
                    stat = os.stat(file_path)
                    backups.append({
                        "filename": file,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "path": file_path
                    })
        except Exception as e:
            print(f"Error listing backups: {e}")
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)

class NotificationManager:
    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
        self._setup_mailjet()
    
    def _setup_mailjet(self):
        """Setup Mailjet client"""
        api_key = self.settings.get_setting('notifications', 'mailjetApiKey', '')
        secret_key = self.settings.get_setting('notifications', 'mailjetSecretKey', '')
        
        if api_key and secret_key:
            self.mailjet = Client(auth=(api_key, secret_key), version='v3.1')
        else:
            self.mailjet = None
    
    def send_notification(self, notification_type: str, subject: str, message: str, data: Dict = None) -> bool:
        """Send notification based on type and settings"""
        try:
            # Check if this notification type is enabled
            if not self.settings.get_setting('notifications', notification_type, False):
                return True  # Notification disabled, consider as success
            
            # Check if email notifications are enabled
            if not self.settings.get_setting('notifications', 'emailNotifications', False):
                return True
            
            email = self.settings.get_setting('notifications', 'emailAddress', '')
            if not email:
                return False
            
            return self._send_email(email, subject, message, data)
            
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False
    
    def _send_email(self, to_email: str, subject: str, message: str, data: Dict = None) -> bool:
        """Send email using Mailjet"""
        try:
            if not self.mailjet:
                print("Mailjet not configured")
                return False
            
            # Create HTML version of the message
            html_message = self._create_html_email(subject, message, data)
            
            email_data = {
                'Messages': [
                    {
                        "From": {
                            "Email": "phgfull@gmail.com",
                            "Name": "Social Media Automation"
                        },
                        "To": [
                            {
                                "Email": to_email,
                                "Name": "Administrator"
                            }
                        ],
                        "Subject": subject,
                        "TextPart": message,
                        "HTMLPart": html_message
                    }
                ]
            }
            
            result = self.mailjet.send.create(data=email_data)
            return result.status_code == 200
            
        except Exception as e:
            print(f"Error sending email via Mailjet: {e}")
            return False
    
    def _create_html_email(self, subject: str, message: str, data: Dict = None) -> str:
        """Create HTML email template"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f8f9fa; padding: 20px; }}
                .footer {{ background-color: #6b7280; color: white; padding: 10px; text-align: center; font-size: 12px; }}
                .data-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .data-table th {{ background-color: #e5e7eb; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Social Media Automation</h1>
                    <h2>{subject}</h2>
                </div>
                <div class="content">
                    <p>{message.replace('\n', '<br>')}</p>
        """
        
        if data:
            html += """
                    <table class="data-table">
                        <tr><th>Property</th><th>Value</th></tr>
            """
            for key, value in data.items():
                html += f"<tr><td>{key}</td><td>{value}</td></tr>"
            html += "</table>"
        
        html += f"""
                    <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="footer">
                    <p>Social Media Automation Suite - Automated Notification</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_upload_success(self, platform: str, account: str, video_id: str = None):
        """Send upload success notification"""
        subject = f"Upload Successful - {platform}"
        message = f"Video uploaded successfully to {platform} account '{account}'"
        data = {
            "Platform": platform,
            "Account": account,
            "Video ID": video_id or "N/A",
            "Status": "Success"
        }
        return self.send_notification('uploadSuccess', subject, message, data)
    
    def send_upload_failure(self, platform: str, account: str, error: str):
        """Send upload failure notification"""
        subject = f"Upload Failed - {platform}"
        message = f"Failed to upload video to {platform} account '{account}'. Error: {error}"
        data = {
            "Platform": platform,
            "Account": account,
            "Error": error,
            "Status": "Failed"
        }
        return self.send_notification('uploadFailure', subject, message, data)
    
    def send_weekly_report(self, stats: Dict):
        """Send weekly activity report"""
        subject = "Weekly Activity Report"
        message = f"""
        Here's your weekly social media automation summary:
        
        Total Uploads: {stats.get('total_uploads', 0)}
        Successful Uploads: {stats.get('successful_uploads', 0)}
        Failed Uploads: {stats.get('failed_uploads', 0)}
        Success Rate: {stats.get('success_rate', 0)}%
        
        Most Active Platform: {stats.get('most_active_platform', 'N/A')}
        """
        return self.send_notification('weeklyReports', subject, message, stats)

class PerformanceMonitor:
    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system performance statistics"""
        try:
            return {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_io": self._get_network_io(),
                "active_processes": len(psutil.pids()),
                "uptime": self._get_uptime()
            }
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return {}
    
    def _get_network_io(self) -> Dict[str, int]:
        """Get network I/O statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except:
            return {}
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_hours = uptime_seconds / 3600
            return f"{uptime_hours:.1f} hours"
        except:
            return "Unknown"
    
    def check_performance_limits(self) -> List[Dict[str, Any]]:
        """Check if system is within performance limits"""
        warnings = []
        stats = self.get_system_stats()
        
        # Check CPU usage
        if stats.get('cpu_usage', 0) > 90:
            warnings.append({
                "type": "cpu",
                "message": f"High CPU usage: {stats['cpu_usage']}%",
                "severity": "high"
            })
        
        # Check memory usage
        if stats.get('memory_usage', 0) > 85:
            warnings.append({
                "type": "memory",
                "message": f"High memory usage: {stats['memory_usage']}%",
                "severity": "high"
            })
        
        # Check disk usage
        if stats.get('disk_usage', 0) > 90:
            warnings.append({
                "type": "disk",
                "message": f"High disk usage: {stats['disk_usage']}%",
                "severity": "critical"
            })
        
        return warnings

class SecurityManager:
    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
        self.failed_logins = {}  # IP -> count
        self.blocked_ips = set()
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        # Check if IP is blocked
        if ip_address in self.blocked_ips:
            return False
        
        # Check whitelist
        whitelist = self.settings.get_setting('security', 'ipWhitelist', [])
        if whitelist and ip_address not in whitelist:
            return False
        
        return True
    
    def record_failed_login(self, ip_address: str) -> bool:
        """Record failed login attempt and check if IP should be blocked"""
        max_attempts = self.settings.get_setting('security', 'loginAttempts', 5)
        
        self.failed_logins[ip_address] = self.failed_logins.get(ip_address, 0) + 1
        
        if self.failed_logins[ip_address] >= max_attempts:
            self.blocked_ips.add(ip_address)
            return True  # IP was blocked
        
        return False
    
    def reset_failed_logins(self, ip_address: str):
        """Reset failed login count for IP (successful login)"""
        if ip_address in self.failed_logins:
            del self.failed_logins[ip_address]
    
    def add_to_whitelist(self, ip_address: str) -> bool:
        """Add IP to whitelist"""
        try:
            whitelist = self.settings.get_setting('security', 'ipWhitelist', [])
            if ip_address not in whitelist:
                whitelist.append(ip_address)
                return self.settings.update_setting('security', 'ipWhitelist', whitelist)
            return True
        except Exception as e:
            print(f"Error adding IP to whitelist: {e}")
            return False
    
    def remove_from_whitelist(self, ip_address: str) -> bool:
        """Remove IP from whitelist"""
        try:
            whitelist = self.settings.get_setting('security', 'ipWhitelist', [])
            if ip_address in whitelist:
                whitelist.remove(ip_address)
                return self.settings.update_setting('security', 'ipWhitelist', whitelist)
            return True
        except Exception as e:
            print(f"Error removing IP from whitelist: {e}")
            return False
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password_strength(self, password: str) -> Dict[str, Any]:
        """Verify password meets strength requirements"""
        if not self.settings.get_setting('security', 'requireStrongPasswords', True):
            return {"valid": True, "message": "Password strength checking disabled"}
        
        issues = []
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one digit")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("Password must contain at least one special character")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "message": "Password meets requirements" if len(issues) == 0 else "Password is too weak"
        }