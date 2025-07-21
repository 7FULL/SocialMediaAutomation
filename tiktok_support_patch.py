"""
Patch to add TikTok support to social media panel
This file contains the enhanced dialog functions for TikTok clip generation
"""

import tkinter as tk
import customtkinter as ctk
import tkinter.filedialog as fd
import threading
import os
import shutil
from tkinter import messagebox
from moviepy.editor import VideoFileClip
try:
    from core.tiktok_automation_enhanced import TikTokAutomation
    ENHANCED_AVAILABLE = True
except ImportError:
    from core.tiktok_automation import TikTokAutomation
    ENHANCED_AVAILABLE = False


def enhanced_generate_clips_file_dialog(panel_instance, account_name):
    """
    Enhanced dialog for file-based clip generation with duration selection
    """
    # First, ask for clip duration
    duration_dialog = ctk.CTkToplevel(panel_instance)
    duration_dialog.geometry("400x400")
    duration_dialog.title(f"🎵 Set TikTok Clip Duration - {account_name}")
    duration_dialog.lift()
    duration_dialog.attributes("-topmost", True)
    duration_dialog.attributes("-topmost", False)
    duration_dialog.grab_set()
    duration_dialog.focus_force()
    duration_dialog.resizable(False, False)
    
    # Store the clip duration
    selected_duration = tk.IntVar(value=15)  # TikTok default
    
    # Main container
    main_frame = ctk.CTkFrame(duration_dialog, corner_radius=10)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    main_frame.grid_columnconfigure(0, weight=1)
    
    # Header
    header_label = ctk.CTkLabel(
        main_frame,
        text="Set Clip Duration for TikTok",
        font=ctk.CTkFont(size=18, weight="bold")
    )
    header_label.grid(row=0, column=0, pady=(20, 10))
    
    info_label = ctk.CTkLabel(
        main_frame,
        text="Recommended: 15-60 seconds for TikTok",
        font=ctk.CTkFont(size=12),
        text_color="gray"
    )
    info_label.grid(row=1, column=0, pady=(0, 20))
    
    # Duration input
    ctk.CTkLabel(
        main_frame,
        text="Clip Duration (seconds):",
        font=ctk.CTkFont(size=14, weight="bold")
    ).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 5))
    
    duration_frame = ctk.CTkFrame(main_frame)
    duration_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
    duration_frame.grid_columnconfigure(0, weight=1)
    
    duration_entry = ctk.CTkEntry(
        duration_frame,
        textvariable=selected_duration,
        height=35,
        width=100,
        font=ctk.CTkFont(size=14)
    )
    duration_entry.pack(side="left", padx=10, pady=10)
    
    # Preset buttons
    preset_frame = ctk.CTkFrame(main_frame)
    preset_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
    preset_frame.grid_columnconfigure(0, weight=1)
    preset_frame.grid_columnconfigure(1, weight=1)
    preset_frame.grid_columnconfigure(2, weight=1)
    preset_frame.grid_columnconfigure(3, weight=1)
    
    ctk.CTkLabel(
        preset_frame,
        text="Quick presets:",
        font=ctk.CTkFont(size=12, weight="bold")
    ).grid(row=0, column=0, columnspan=4, pady=(10, 5))
    
    def set_duration(duration):
        selected_duration.set(duration)
        
    preset_durations = [15, 30, 45, 60]
    for i, duration in enumerate(preset_durations):
        ctk.CTkButton(
            preset_frame,
            text=f"{duration}s",
            command=lambda d=duration: set_duration(d),
            width=70,
            height=30
        ).grid(row=1, column=i, padx=2, pady=5)
    
    def proceed_to_file_selection():
        """Proceed to file selection with the chosen duration."""
        clip_duration = selected_duration.get()
        if clip_duration < 5 or clip_duration > 300:
            messagebox.showerror("Invalid Duration", "Please enter a duration between 5 and 300 seconds.")
            return
            
        duration_dialog.destroy()
        
        # Now select the file
        file_path = fd.askopenfilename(
            title=f"Select video file for {account_name}",
            filetypes=[
                ("Video files", "*.mp4 *.mov *.avi *.mkv *.wmv *.flv"),
                ("MP4 files", "*.mp4"),
                ("All Files", "*.*")
            ]
        )
        if not file_path:
            return
        
        # Open the processing dialog
        process_tiktok_file(panel_instance, account_name, file_path, clip_duration)
    
    # Action buttons
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    
    ctk.CTkButton(
        button_frame,
        text="Cancel",
        command=duration_dialog.destroy,
        height=35,
        fg_color="#666666",
        hover_color="#777777",
        font=ctk.CTkFont(size=12, weight="bold")
    ).grid(row=0, column=0, padx=(0, 10), sticky="ew")
    
    ctk.CTkButton(
        button_frame,
        text="📁 Select File",
        command=proceed_to_file_selection,
        height=35,
        font=ctk.CTkFont(size=12, weight="bold")
    ).grid(row=0, column=1, padx=(10, 0), sticky="ew")


def process_tiktok_file(panel_instance, account_name, file_path, clip_duration):
    """Process the selected file for TikTok with the specified clip duration."""
    dialog = ctk.CTkToplevel(panel_instance)
    dialog.geometry("500x350")
    dialog.title(f"🎵 Processing TikTok Video - {account_name}")
    dialog.lift()
    dialog.attributes("-topmost", True)
    dialog.attributes("-topmost", False)
    dialog.grab_set()
    dialog.focus_force()
    dialog.resizable(False, False)
    
    # Main container
    main_frame = ctk.CTkFrame(dialog, corner_radius=10)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    main_frame.grid_columnconfigure(0, weight=1)
    
    # Header
    header_label = ctk.CTkLabel(
        main_frame,
        text=f"Processing: {os.path.basename(file_path)}",
        font=ctk.CTkFont(size=16, weight="bold")
    )
    header_label.grid(row=0, column=0, pady=(20, 10))
    
    info_label = ctk.CTkLabel(
        main_frame,
        text=f"Creating {clip_duration}-second clips for TikTok",
        font=ctk.CTkFont(size=12),
        text_color="gray"
    )
    info_label.grid(row=1, column=0, pady=(0, 20))
    
    # Progress bar and status
    progress_bar = ctk.CTkProgressBar(main_frame, orientation="horizontal", mode="determinate")
    progress_bar.set(0.0)
    progress_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
    
    progress_label = ctk.CTkLabel(main_frame, text="Ready to start...")
    progress_label.grid(row=3, column=0, pady=(0, 20))
    
    # File info
    try:
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        info_text = f"File size: {file_size:.1f} MB"
        
        # Try to get video duration
        try:
            with VideoFileClip(file_path) as temp_video:
                duration = int(temp_video.duration)
                estimated_clips = max(1, duration // clip_duration)
                info_text += f" • Duration: {duration}s • Est. clips: {estimated_clips}"
        except:
            info_text += " • Duration: Unknown"
            
        file_info_label = ctk.CTkLabel(
            main_frame,
            text=info_text,
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        file_info_label.grid(row=4, column=0, pady=(0, 20))
    except:
        pass
    
    account_data = panel_instance.accounts[account_name]
    output_folder = account_data.get("clip_folder", "")
    
    stop_event = threading.Event()
    
    def update_progress(msg, val):
        def _update():
            progress_label.configure(text=msg)
            progress_bar.set(val)
        progress_label.after(0, _update)
    
    def run_thread():
        if not os.path.exists(file_path):
            update_progress("❌ File does not exist.", 0)
            return
        if not output_folder:
            update_progress("❌ No clip folder set.", 0)
            return
        
        try:
            update_progress("🔄 Initializing TikTok automation...", 0.1)
            
            # Use TikTok automation
            tta = TikTokAutomation(file_path=file_path, output_path=output_folder)
            
            if stop_event.is_set():
                update_progress("⏹️ Stopped.", 0)
                return
            
            update_progress("📁 Processing video file...", 0.3)
            success = tta.process_video_file()
            
            if not success:
                update_progress("❌ Failed to process video file.", 0)
                return
                
            if stop_event.is_set():
                update_progress("⏹️ Stopped.", 0)
                return
            
            update_progress("✂️ Creating TikTok clips...", 0.7)
            success = tta.create_clips(clip_duration)
            
            if success:
                clips_dir = os.path.join(output_folder, "clips")
                if os.path.exists(clips_dir):
                    clip_count = len([f for f in os.listdir(clips_dir) if f.startswith("clip_")])
                    update_progress(f"✅ Successfully created {clip_count} clips!", 1.0)
                else:
                    update_progress("✅ Clips generated successfully!", 1.0)
            else:
                update_progress("❌ Failed to generate clips.", 0)
                
        except Exception as e:
            update_progress(f"❌ Error: {str(e)[:50]}...", 0)
            print(f"TikTok processing error: {e}")
    
    def start_generation():
        progress_label.configure(text="🚀 Starting generation...")
        progress_bar.set(0.0)
        stop_event.clear()
        t = threading.Thread(target=run_thread, daemon=True)
        t.start()
    
    def stop_generation():
        stop_event.set()
        update_progress("⏹️ Stopping...", 0)
    
    # Action buttons
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)
    
    ctk.CTkButton(
        button_frame,
        text="🚀 Start",
        command=start_generation,
        height=35,
        font=ctk.CTkFont(size=12, weight="bold")
    ).grid(row=0, column=0, padx=(0, 5), sticky="ew")
    
    ctk.CTkButton(
        button_frame,
        text="⏹️ Stop",
        command=stop_generation,
        height=35,
        fg_color="#ff6b6b",
        hover_color="#ff5252",
        font=ctk.CTkFont(size=12, weight="bold")
    ).grid(row=0, column=1, padx=5, sticky="ew")
    
    ctk.CTkButton(
        button_frame,
        text="Close",
        command=dialog.destroy,
        height=35,
        fg_color="#666666",
        hover_color="#777777",
        font=ctk.CTkFont(size=12, weight="bold")
    ).grid(row=0, column=2, padx=(5, 0), sticky="ew")


# Function to patch the existing social media panel
def apply_tiktok_patch(social_media_panel_instance):
    """Apply TikTok support patch to an existing SocialMediaPanel instance"""
    
    # Override the generate_clips_file_dialog method for TikTok
    original_method = social_media_panel_instance.generate_clips_file_dialog
    
    def patched_generate_clips_file_dialog(account_name):
        if social_media_panel_instance.social_media_name == "TikTok":
            return enhanced_generate_clips_file_dialog(social_media_panel_instance, account_name)
        else:
            return original_method(account_name)
    
    social_media_panel_instance.generate_clips_file_dialog = patched_generate_clips_file_dialog
    
    print(f"✅ TikTok support patch applied to {social_media_panel_instance.social_media_name} panel")