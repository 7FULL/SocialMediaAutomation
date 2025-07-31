import datetime as datetime
import time
import os
import re
import json
import shutil
from moviepy.editor import VideoFileClip

# PIL compatibility fix for newer versions
try:
    from PIL import Image
    # Check if ANTIALIAS exists, if not, use LANCZOS
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass


class TikTokAutomation:
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
        # For now, this is a placeholder since TikTok API is more complex
        # In a real implementation, you would need to use TikTok's API
        log_file = f"tiktok_automation/logs/{self.account_name}_uploaded_videos.json"
        part_number = self.get_next_part_number(log_file)
        
        file_path = f"{self.clips_folder}/clips/clip_{part_number}.mp4"
        
        if not os.path.exists(file_path):
            print(f"No clip found at {file_path}")
            return False
        
        title = self.acc_data.get("title", "TikTok Video") + " pt: " + str(part_number)
        description = self.acc_data.get("description", "") + " pt: " + str(part_number)
        
        # TODO: Implement actual TikTok upload here
        # For now, just simulate successful upload
        print(f"Simulating upload of {file_path} to TikTok...")
        print(f"Title: {title}")
        print(f"Description: {description}")
        
        # Log the video
        self.log_video(log_file, title)
        print(f"TikTok clip {part_number} uploaded successfully (simulated)")
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

    def log_video(self, log_file, title):
        """Log uploaded video information."""
        # Load existing data
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"videos": []}
        
        # Add new video
        data["videos"].append({
            "title": title,
            "upload_date": datetime.datetime.now().isoformat(),
            "account": self.account_name
        })
        
        # Save back to file
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def authenticate_tiktok_account(account_name):
        """
        Placeholder for TikTok authentication.
        In a real implementation, this would handle TikTok OAuth.
        """
        # For now, just return True to simulate successful authentication
        print(f"Simulating TikTok authentication for account: {account_name}")
        
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
                "auth_date": datetime.datetime.now().isoformat()
            }, f, indent=4)
        
        return True

    def process_and_create_clips(self, clip_duration=15):
        """Process video file and create clips in one step."""
        if self.process_video_file():
            return self.create_clips(clip_duration)
        return False