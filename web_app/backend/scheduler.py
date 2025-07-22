import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List
import json
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.youtube_automation import YouTubeAutomation
try:
    from core.tiktok_automation_enhanced import TikTokAutomation
except ImportError:
    from core.tiktok_automation import TikTokAutomation

class SchedulerService:
    def __init__(self, config_data: Dict):
        self.config_data = config_data
        self.stop_events = {}
        self.scheduler_threads = {}
    
    def update_config(self, new_config_data: Dict):
        """Update the configuration data"""
        self.config_data = new_config_data
        
    async def start_platform_scheduler(self, platform_name: str):
        """Start scheduler for a specific platform"""
        print(f"DEBUG: Attempting to start scheduler for {platform_name}")
        print(f"DEBUG: Current scheduler_threads: {list(self.scheduler_threads.keys())}")
        
        if platform_name in self.scheduler_threads:
            print(f"Scheduler already running for {platform_name}")
            return
        
        # Create stop event
        stop_event = threading.Event()
        self.stop_events[platform_name] = stop_event
        
        # Start scheduler thread
        scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            args=(platform_name, stop_event),
            daemon=True
        )
        scheduler_thread.start()
        
        self.scheduler_threads[platform_name] = scheduler_thread
        print(f"Started scheduler for {platform_name}")
        
    async def stop_platform_scheduler(self, platform_name: str):
        """Stop scheduler for a specific platform"""
        if platform_name in self.stop_events:
            self.stop_events[platform_name].set()
            
        if platform_name in self.scheduler_threads:
            self.scheduler_threads[platform_name].join(timeout=5)
            del self.scheduler_threads[platform_name]
            
        if platform_name in self.stop_events:
            del self.stop_events[platform_name]
            
        print(f"Stopped scheduler for {platform_name}")
        
    async def stop_all_schedulers(self):
        """Stop all active schedulers"""
        for platform_name in list(self.stop_events.keys()):
            await self.stop_platform_scheduler(platform_name)
            
    def _scheduler_loop(self, platform_name: str, stop_event: threading.Event):
        """Main scheduler loop for a platform"""
        while not stop_event.is_set():
            try:
                platform_config = self.config_data.get(platform_name, {})
                accounts = platform_config.get("accounts", {})
                
                for account_name, account_data in accounts.items():
                    if stop_event.is_set():
                        break
                        
                    # Check if account is active and authenticated
                    if not account_data.get("active", False):
                        continue
                    if not account_data.get("authenticated", False):
                        continue
                    
                    # Check schedule
                    schedule = account_data.get("schedule", {})
                    next_upload_time = self._get_next_upload_time(schedule)
                    
                    if next_upload_time and datetime.now() >= next_upload_time:
                        print(f"Time to upload for {platform_name} account {account_name}")
                        self._upload_for_account(platform_name, account_name, account_data)
                        
                # Sleep for 60 seconds before checking again
                stop_event.wait(60)
                
            except Exception as e:
                print(f"Error in scheduler loop for {platform_name}: {e}")
                stop_event.wait(60)  # Wait before retrying
                
    def _get_next_upload_time(self, schedule: Dict[str, List[str]]):
        """Get the next upload time from schedule"""
        now = datetime.now()
        today_str = now.strftime("%A")
        
        # Remove seconds and microseconds for comparison
        now = now.replace(second=0, microsecond=0)
        
        # Check today's schedule
        today_times = schedule.get(today_str, [])
        for time_str in sorted(today_times):
            try:
                hour, minute = map(int, time_str.split(":"))
                scheduled_time = now.replace(hour=hour, minute=minute)
                if scheduled_time >= now:
                    return scheduled_time
            except (ValueError, IndexError):
                continue
        
        # Check tomorrow's schedule
        tomorrow = now + timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%A")
        tomorrow_times = schedule.get(tomorrow_str, [])
        
        if tomorrow_times:
            try:
                hour, minute = map(int, tomorrow_times[0].split(":"))
                next_time = tomorrow.replace(hour=hour, minute=minute)
                return next_time
            except (ValueError, IndexError):
                pass
        
        return None
    
    def _upload_for_account(self, platform_name: str, account_name: str, account_data: dict):
        """Upload content for an account"""
        try:
            if platform_name == "YouTube":
                yta = YouTubeAutomation(acc_data=account_data, account_name=account_name)
                yta.upload_and_log_short()
            elif platform_name == "TikTok":
                tta = TikTokAutomation(acc_data=account_data, account_name=account_name)
                tta.upload_and_log_short()
            else:
                print(f"Upload not implemented for {platform_name}")
                
        except Exception as e:
            print(f"Error uploading for {platform_name} account {account_name}: {e}")

    def get_scheduler_status(self, platform_name: str) -> dict:
        """Get scheduler status for a platform"""
        is_running = platform_name in self.scheduler_threads
        auto_upload = self.config_data.get(platform_name, {}).get("auto_upload", False)
        
        print(f"DEBUG: Scheduler status for {platform_name}:")
        print(f"  - scheduler_threads: {list(self.scheduler_threads.keys())}")
        print(f"  - is_running: {is_running}")
        print(f"  - auto_upload: {auto_upload}")
        print(f"  - platform_name in threads: {platform_name in self.scheduler_threads}")
        
        return {
            "platform_name": platform_name,
            "is_running": is_running,
            "auto_upload": auto_upload
        }
    
    def get_next_upload_times(self, platform_name: str) -> dict:
        """Get next upload times for all accounts in a platform"""
        platform_config = self.config_data.get(platform_name, {})
        accounts = platform_config.get("accounts", {})
        
        upload_times = {}
        for account_name, account_data in accounts.items():
            if account_data.get("active", False) and account_data.get("authenticated", False):
                schedule = account_data.get("schedule", {})
                next_time = self._get_next_upload_time(schedule)
                
                upload_times[account_name] = {
                    "next_upload": next_time.isoformat() if next_time else None,
                    "time_remaining": self._get_time_remaining(next_time) if next_time else None,
                    "active": True
                }
            else:
                upload_times[account_name] = {
                    "next_upload": None,
                    "time_remaining": None,
                    "active": False
                }
        
        return upload_times
    
    def _get_time_remaining(self, next_time: datetime) -> str:
        """Get human readable time remaining until next upload"""
        if not next_time:
            return None
        
        now = datetime.now()
        if next_time <= now:
            return "Ready to upload"
        
        diff = next_time - now
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"