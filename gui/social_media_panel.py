import time
import tkinter as tk
import datetime

import shutil
import customtkinter as ctk
import tkinter.filedialog as fd
import threading
import os
from core.youtube_automation import YouTubeAutomation

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class SocialMediaPanel(ctk.CTkFrame):
    def __init__(self, master, social_media_name, config_data, *args, **kwargs):
        """
        This frame represents the panel for a specific social media platform.
        """
        super().__init__(master, *args, **kwargs)

        self.social_media_name = social_media_name
        self.config_data = config_data  # Global config dict

        # A single Boolean for enabling auto-upload for the entire social media
        self.auto_upload_var = tk.BooleanVar(value=False)

        # Dictionary holding accounts. Each account has:
        # "token_path", "active", "clip_folder", "schedule", "authenticated" etc.
        self.accounts = {}

        self.scheduler_thread = None
        self.stop_event = threading.Event()

        # Build the UI
        self.create_widgets()
        self.load_panel_config()

    # -------------------------------------------------------------------------
    # UI Setup
    # -------------------------------------------------------------------------
    def create_widgets(self):
        """
        Build the UI elements for this social media panel.
        """
        # Title label
        title_label = ctk.CTkLabel(
            self,
            text=f"{self.social_media_name} Panel",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=10)

        # Section: Enable/Disable auto-upload
        auto_upload_checkbox = ctk.CTkCheckBox(
            self,
            text="Enable Auto-Upload",
            variable=self.auto_upload_var,
            command=self.on_auto_upload_toggle
        )
        auto_upload_checkbox.pack(anchor="w", padx=20, pady=5)

        # Section: Accounts
        accounts_frame = ctk.CTkFrame(self)
        accounts_frame.pack(padx=20, pady=10, fill="x")

        accounts_label = ctk.CTkLabel(accounts_frame, text="Accounts:")
        accounts_label.pack(anchor="w")

        # A scrollable container for all accounts
        self.accounts_container = ctk.CTkScrollableFrame(accounts_frame, width=700, height=180)
        self.accounts_container.pack(pady=5, fill="both")

        # Button to add a new account
        add_account_button = ctk.CTkButton(
            accounts_frame,
            text="Add Account",
            command=self.add_account_dialog
        )
        add_account_button.pack(anchor="w", pady=5)

    # -------------------------------------------------------------------------
    # Load/Save configuration
    # -------------------------------------------------------------------------
    def load_panel_config(self):
        """
        Load this social media's configuration from the global config dict.
        """
        social_config = self.config_data.get(self.social_media_name, {})
        self.auto_upload_var.set(social_config.get("auto_upload", False))

        # Load or create accounts
        self.accounts = social_config.get("accounts", {})

        # Ensure each account has 'clip_folder' and 'schedule' etc.
        for acc_name, acc_data in self.accounts.items():
            acc_data.setdefault("clip_folder", "")
            acc_data.setdefault("schedule", {day: [] for day in DAYS_OF_WEEK})
            acc_data.setdefault("token_path", "")
            acc_data.setdefault("active", True)
            acc_data.setdefault("authenticated", False)
            acc_data.setdefault("description", None)
            acc_data.setdefault("tags", None)
            acc_data.setdefault("title", None)
            acc_data.setdefault("category_id", None)

            # Optional: We can also do a quick check if their token is still valid
            # but that would require loading the token here. For now, we skip.

        if self.auto_upload_var.get():
            self.start_scheduler()
        else:
            # Ensure it's not running
            self.stop_scheduler()

        self.update_accounts_display()

    def save_panel_config(self):
        """
        Save this social media's configuration into the global config dict.
        """
        self.config_data[self.social_media_name] = {
            "auto_upload": self.auto_upload_var.get(),
            "accounts": self.accounts,
        }

    # -------------------------------------------------------------------------
    # Panel Callbacks
    # -------------------------------------------------------------------------
    def on_auto_upload_toggle(self):
        """
        Triggered when the auto-upload checkbox is toggled.
        """
        status = "enabled" if self.auto_upload_var.get() else "disabled"
        print(f"[{self.social_media_name}] Auto-upload {status}")

        if self.auto_upload_var.get():
            self.start_scheduler()
        else:
            self.stop_scheduler()

    def add_account_dialog(self):
        """
        Open a dialog to add a new account with minimal info (name/token).
        Then immediately authenticate YouTube for that account.
        """
        dialog = ctk.CTkToplevel(self)
        dialog.geometry("200x200")
        dialog.title(f"Add {self.social_media_name} Account")
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.attributes("-topmost", False)
        dialog.grab_set()
        dialog.focus_force()

        # acc_data.setdefault("description", None)
        # acc_data.setdefault("tags", None)
        # acc_data.setdefault("title", None)
        # acc_data.setdefault("category_id", None)

        account_name_var = tk.StringVar()
        token_path_var = tk.StringVar()

        is_active_var = tk.BooleanVar(value=True)

        ctk.CTkLabel(dialog, text="Account Name:").pack(padx=10, pady=(10, 5))
        ctk.CTkEntry(dialog, textvariable=account_name_var).pack(padx=10, pady=5)

        active_checkbox = ctk.CTkCheckBox(dialog, text="Active", variable=is_active_var)
        active_checkbox.pack(pady=5)

        def save_new_account():
            name = account_name_var.get().strip()
            token = token_path_var.get().strip()
            if not name:
                print("Please enter an account name.")
                return

            # Create a default schedule
            schedule_dict = {day: [] for day in DAYS_OF_WEEK}

            # We'll authenticate right now:
            authenticated = YouTubeAutomation.authenticate_youtube_account(name)
            if not authenticated:
                print(f"User did not authenticate for account '{name}'. Setting account as not authenticated.")
                # Optionally set active=False if user didn't authenticate
                is_active_var.set(False)

            clips_folder = f"youtube_automation/account_clips/{name}"

            if not os.path.exists(clips_folder):
                os.makedirs(clips_folder)

            self.accounts[name] = {
                "token_path": token,
                "active": is_active_var.get(),
                "clip_folder": clips_folder,
                "schedule": schedule_dict,
                "authenticated": authenticated
            }

            self.update_accounts_display()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Save & Authenticate", command=save_new_account).pack(pady=10)

    # -------------------------------------------------------------------------
    # SCHEDULER LOGIC
    # -------------------------------------------------------------------------
    def start_scheduler(self):
        """Starts a background thread that checks schedules for all active+auth accounts."""
        # If a scheduler thread is already running, no need to start another
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            print("Scheduler already running.")
            return

        # Clear the stop event (in case it was set before)
        self.stop_event.clear()

        print("Starting scheduler...")

        self.scheduler_thread = threading.Thread(target=self.scheduler_loop, daemon=True)
        self.scheduler_thread.start()

    def stop_scheduler(self):
        """Signals the scheduler thread to stop."""
        self.stop_event.set()
        if self.scheduler_thread:
            self.scheduler_thread = None
            print("Scheduler stopped.")

    def scheduler_loop(self):
        """
        Runs in a background thread, checking each account’s schedule periodically.
        """
        while not self.stop_event.is_set():
            now = datetime.datetime.now()

            for account_name, acc_data in self.accounts.items():
                # Only proceed if account is active AND authenticated
                if not acc_data.get("active"):
                    continue
                if not acc_data.get("authenticated"):
                    continue

                # Retrieve the schedule
                schedule_data = acc_data.get("schedule", {})
                # Find the next upload time for this account
                next_time = self.get_next_upload_time_for_account(schedule_data)

                if next_time and now >= next_time:
                    print(f"Account {account_name}: Time to upload! ({now})")
                    # Perform the upload
                    # Example: self.upload_for_account(account_name)
                    self.upload_for_account(account_name)

                    # Typically we'd either remove that time from the schedule
                    # or find the next time in the future.
                    # For daily repeated schedules, we might do nothing
                    # and next time around we'll parse again.
                else:
                    print(f"Account {account_name}: Next upload at {next_time}")

            # Sleep a bit before checking again
            time.sleep(60)  # check every 30 seconds or as you prefer

    def get_next_upload_time_for_account(self, schedule_data):
        """
        Finds the earliest future time (today or next day) from the account’s schedule
        that’s after 'now'.
        Returns a datetime or None if no future times are found.
        """
        now = datetime.datetime.now()
        today_str = now.strftime("%A")  # e.g. "Monday"
        today_times = schedule_data.get(today_str, [])

        # Remove seconds and microseconds
        now = now.replace(second=0, microsecond=0)

        # First, see if there's a time left today
        for time_str in sorted(today_times):
            # "HH:MM"
            hh, mm = time_str.split(":")
            scheduled_dt = now.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
            if scheduled_dt >= now:
                return scheduled_dt

        # If none left today, check subsequent days
        # For simplicity, we only look 1 day ahead.
        # If you have advanced logic for multiple days, handle that here.
        tomorrow = now + datetime.timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%A")
        tmrw_times = schedule_data.get(tomorrow_str, [])
        if tmrw_times:
            # We pick the earliest time from tomorrow
            hh, mm = tmrw_times[0].split(":")
            # Combine that time with "tomorrow" date
            next_dt = tomorrow.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
            return next_dt

        return None  # No future times found

    def upload_for_account(self, account_name):
        """
        Example method that uses your YouTubeAutomation to upload something
        for this account.
        """
        acc_data = self.accounts[account_name]

        # Here you'd do something like:
        # 1) Set up YouTubeAutomation with that account’s token file (token_{account_name}.pickle)
        # 2) Decide which clip to upload
        # 3) Call your "upload_and_log_short" or similar
        print(f"Uploading for account: {account_name}. Using the account's schedule, clip folder, etc.")

        yta = YouTubeAutomation(acc_data=acc_data, account_name=account_name)
        yta.upload_and_log_short()

    # -------------------------------------------------------------------------
    # Accounts Table: minimal columns (Active, Auth, Name, Edit, Delete)
    # -------------------------------------------------------------------------
    def update_accounts_display(self):
        for widget in self.accounts_container.winfo_children():
            widget.destroy()

        for acc_name, acc_data in self.accounts.items():
            row_frame = ctk.CTkFrame(self.accounts_container)
            row_frame.pack(fill="x", pady=5, padx=5)

            # 1) Active CheckBox
            active_var = tk.BooleanVar(value=acc_data.get("active", False))

            def on_toggle(state_var, account=acc_name):
                self.accounts[account]["active"] = state_var.get()
                # If not authenticated, forcing active might not make sense,
                # but we'll leave that up to the user. Or we can auto-disable if not authed.
                if not self.accounts[account].get("authenticated", False):
                    print(f"WARNING: Account '{account}' is not authenticated. Activation might fail.")
                print(f"Account '{account}' active={state_var.get()}")
                self.update_accounts_display()  # Refresh row

            active_checkbox = ctk.CTkCheckBox(
                row_frame,
                text="Activa",
                variable=active_var,
                command=lambda var=active_var, name=acc_name: on_toggle(var, name)
            )
            active_checkbox.pack(side="left", padx=5)

            # 2) Auth label
            auth_label_str = "Auth OK" if acc_data.get("authenticated", False) else "No Auth"
            auth_label_color = "green" if acc_data.get("authenticated", False) else "red"
            auth_label = ctk.CTkLabel(row_frame, text=auth_label_str, text_color=auth_label_color)
            auth_label.pack(side="left", padx=5)

            # 3) Account Name
            account_label = ctk.CTkLabel(row_frame, text=acc_name)
            account_label.pack(side="left", padx=5)

            # 4) Edit button
            edit_btn = ctk.CTkButton(
                row_frame,
                text="Edit",
                command=lambda a=acc_name: self.open_account_editor(a)
            )
            edit_btn.pack(side="left", padx=5)

            # 5) Delete button
            delete_btn = ctk.CTkButton(
                row_frame,
                text="Delete",
                fg_color="red",
                command=lambda a=acc_name: self.delete_account(a)
            )
            delete_btn.pack(side="left", padx=5)

    def delete_account(self, account_name):
        if account_name in self.accounts:
            del self.accounts[account_name]
            print(f"Deleted account: {account_name}")

            # Delete the folder with the clips
            folder = f"youtube_automation/account_clips/{account_name}"
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    os.remove(f"{folder}/{file}")
                os.rmdir(folder)

            self.update_accounts_display()

    # -------------------------------------------------------------------------
    # Account Editor Window
    # -------------------------------------------------------------------------
    def open_account_editor(self, account_name):
        """
        Opens a Toplevel window to edit account details, such as:
        - Token Path
        - Clip Folder
        - Generate Clips (From URL / From File)
        - Schedule
        - Re-authenticate button
        - Active checkbox (optional)
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit Account: {account_name}")
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.attributes("-topmost", False)
        dialog.grab_set()
        dialog.focus_force()

        acc_data = self.accounts[account_name]

        top_frame = ctk.CTkFrame(dialog)
        top_frame.pack(fill="x", padx=10, pady=10)

        mid_frame = ctk.CTkFrame(dialog)
        mid_frame.pack(fill="x", padx=10, pady=10)

        bottom_frame = ctk.CTkFrame(dialog)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        # -- Basic Info
        # ctk.CTkLabel(top_frame, text=f"Account Name: {account_name}").grid(row=0, column=0, sticky="w", padx=5, pady=5)

        before_name = account_name

        account_name = tk.StringVar(value=account_name)
        ctk.CTkLabel(top_frame, text="Account name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)

        description_var = tk.StringVar(value=acc_data.get("description", ""))
        ctk.CTkLabel(top_frame, text="Description:").grid(row=1, column=0, sticky="w", padx=5, pady=2)

        tags_var = tk.StringVar(value=acc_data.get("tags", ""))
        ctk.CTkLabel(top_frame, text="Tags:").grid(row=2, column=0, sticky="w", padx=5, pady=2)

        title_var = tk.StringVar(value=acc_data.get("title", ""))
        ctk.CTkLabel(top_frame, text="Title:").grid(row=3, column=0, sticky="w", padx=5, pady=2)

        category_id_var = tk.StringVar(value=acc_data.get("category_id", ""))
        ctk.CTkLabel(top_frame, text="Category ID:").grid(row=4, column=0, sticky="w", padx=5, pady=2)

        clip_duration_var = tk.IntVar(value=acc_data.get("clip_duration", 57))
        ctk.CTkLabel(top_frame, text="Clip Duration (seconds):").grid(row=5, column=0, sticky="w", padx=5, pady=2)

        token_entry = ctk.CTkEntry(top_frame, textvariable=account_name, width=300)
        token_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        description_entry = ctk.CTkEntry(top_frame, textvariable=description_var, width=300)
        description_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        tags_entry = ctk.CTkEntry(top_frame, textvariable=tags_var, width=300)
        tags_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        title_entry = ctk.CTkEntry(top_frame, textvariable=title_var, width=300)
        title_entry.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        category_id_entry = ctk.CTkEntry(top_frame, textvariable=category_id_var, width=300)
        category_id_entry.grid(row=4, column=1, sticky="w", padx=5, pady=2)

        clip_duration_entry = ctk.CTkEntry(top_frame, textvariable=clip_duration_var, width=300)
        clip_duration_entry.grid(row=5, column=1, sticky="w", padx=5, pady=2)

        active_var = tk.BooleanVar(value=acc_data.get("active", True))
        active_check = ctk.CTkCheckBox(
            top_frame,
            text="Account Active",
            variable=active_var
        )
        active_check.grid(row=6, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        auth_label_str = "Authenticated" if acc_data.get("authenticated", False) else "Not Authenticated"
        auth_label_color = "green" if acc_data.get("authenticated", False) else "red"
        auth_label = ctk.CTkLabel(top_frame, text=auth_label_str, text_color=auth_label_color)
        auth_label.grid(row=7, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        def reauthenticate():
            """
            Allows re-authenticating if token is invalid or user wants to refresh.
            """
            success = YouTubeAutomation.authenticate_youtube_account(account_name.get())
            if success:
                acc_data["authenticated"] = True
                auth_label.configure(text="Authenticated", text_color="green")
                print(f"Re-authenticated account '{account_name.get()}'")
            else:
                acc_data["authenticated"] = False
                auth_label.configure(text="Not Authenticated", text_color="red")
                print(f"Failed or canceled re-auth for '{account_name.get()}'")

        def deleteToken():
            """
            Deletes the token file for the account, forcing a re-authentication.
            """
            token_file = f"youtube_automation/account_tokens/token_{account_name.get()}.pickle"
            if os.path.exists(token_file):
                os.remove(token_file)
                print(f"Deleted token for account '{account_name.get()}'")
                acc_data["authenticated"] = False
                auth_label.configure(text="Not Authenticated", text_color="red")
            else:
                print(f"No token found for account '{account_name.get()}'")

        reauth_btn = ctk.CTkButton(top_frame, text="Re-Authenticate", command=reauthenticate)
        reauth_btn.grid(row=8, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        delete_token_btn = ctk.CTkButton(top_frame, text="Delete Token", fg_color="red", command=deleteToken)
        delete_token_btn.grid(row=8, column=2, columnspan=2, sticky="w", padx=5, pady=5)

        # -- Clip Folder / Generate Clips / Schedule
        folder_var = tk.StringVar(value=acc_data.get("clip_folder", ""))

        ctk.CTkLabel(mid_frame, text="Clip Folder:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        folder_entry = ctk.CTkEntry(mid_frame, textvariable=folder_var, width=300)
        folder_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        def browse_folder():
            chosen = fd.askdirectory()
            if chosen:
                folder_var.set(chosen)

        browse_btn = ctk.CTkButton(mid_frame, text="...", width=30, command=browse_folder)
        browse_btn.grid(row=0, column=2, padx=5, pady=5)

        from_url_btn = ctk.CTkButton(mid_frame, text="Generate Clips (URL)",
                                     command=lambda: self.generate_clips_url_dialog(account_name.get()))
        from_url_btn.grid(row=1, column=0, padx=5, pady=5)

        from_file_btn = ctk.CTkButton(mid_frame, text="Generate Clips (File)",
                                      command=lambda: self.generate_clips_file_dialog(account_name.get()))
        from_file_btn.grid(row=1, column=1, padx=5, pady=5)

        schedule_btn = ctk.CTkButton(mid_frame, text="Edit Schedule",
                                     command=lambda: self.open_schedule_manager_for_account(account_name.get()))
        schedule_btn.grid(row=1, column=2, padx=5, pady=5)

        # -- Bottom: Save / Close
        def save_and_close():
            acc_data["active"] = active_var.get()
            acc_data["clip_folder"] = folder_var.get().strip()
            acc_data["description"] = description_var.get().strip()
            acc_data["tags"] = tags_var.get().strip()
            acc_data["title"] = title_var.get().strip()
            acc_data["category_id"] = category_id_var.get().strip()
            acc_data["clip_duration"] = clip_duration_var.get()

            # If the account name changed, update the key in the dictionary
            if before_name != account_name.get():
                self.accounts[account_name.get()] = self.accounts.pop(before_name)

                if not os.path.exists(f"youtube_automation/account_clips/{account_name.get()}"):
                    os.makedirs(f"youtube_automation/account_clips/{account_name.get()}")

                # Copy all the clips from the old folder to the new folder
                old_folder = f"youtube_automation/account_clips/{before_name}"
                new_folder = f"youtube_automation/account_clips/{account_name.get()}"

                for file in os.listdir(old_folder):
                    os.rename(f"{old_folder}/{file}", f"{new_folder}/{file}")

                # Update the clip folder path
                acc_data["clip_folder"] = new_folder

                # Delete the old folder
                os.rmdir(old_folder)
                os.rmdir(old_folder)

            # Overwrite the dictionary
            self.accounts[account_name.get()] = acc_data
            self.update_accounts_display()
            dialog.destroy()

        save_btn = ctk.CTkButton(bottom_frame, text="Save", command=save_and_close)
        save_btn.pack(side="left", padx=5)

        def close_without_save():
            dialog.destroy()

        close_btn = ctk.CTkButton(bottom_frame, text="Close", command=close_without_save)
        close_btn.pack(side="left", padx=5)

    # -------------------------------------------------------------------------
    #  Generate Clips (from within the Editor)
    # -------------------------------------------------------------------------
    def generate_clips_url_dialog(self, account_name):
        """
        Opens a small dialog to ask for a YouTube URL, then uses that account's
        clip folder to generate clips via YouTubeAutomation.
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Generate Clips (URL) - {account_name}")
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.attributes("-topmost", False)
        dialog.grab_set()
        dialog.focus_force()

        url_var = tk.StringVar()

        ctk.CTkLabel(dialog, text="Enter YouTube URL:").pack(padx=10, pady=(10, 5))
        url_entry = ctk.CTkEntry(dialog, textvariable=url_var, width=300)
        url_entry.pack(padx=10, pady=5)

        progress_bar = ctk.CTkProgressBar(dialog, orientation="horizontal", mode="determinate", width=300)
        progress_bar.set(0.0)
        progress_bar.pack(padx=10, pady=5)

        progress_label = ctk.CTkLabel(dialog, text="Waiting to start...")
        progress_label.pack(padx=10, pady=5)

        account_data = self.accounts[account_name]
        output_folder = account_data.get("clip_folder", "")

        stop_event = threading.Event()

        def update_progress(msg, val):
            def _update():
                progress_label.configure(text=msg)
                progress_bar.set(val)

            progress_label.after(0, _update)

        def run_thread():
            y_url = url_var.get().strip()
            if not y_url:
                update_progress("Please enter a valid URL.", 0)
                return
            if not output_folder:
                update_progress("No clip folder set.", 0)
                return

            try:
                yta = YouTubeAutomation(url=y_url, output_path=output_folder)

                if stop_event.is_set():
                    update_progress("Stopped.", 0)
                    return
                update_progress("Downloading video (1/4)...", 0.1)
                yta.download_video()

                if stop_event.is_set():
                    update_progress("Stopped.", 0)
                    return
                update_progress("Downloading audio (2/4)...", 0.3)
                yta.download_audio()

                if stop_event.is_set():
                    update_progress("Stopped.", 0)
                    return
                update_progress("Combining video (3/4)...", 0.6)
                yta.combine_video_audio()

                if stop_event.is_set():
                    update_progress("Stopped.", 0)
                    return
                update_progress("Creating clips (4/4)...", 0.9)
                yta.create_clips()

                update_progress("Clips generated successfully!", 1.0)

            except Exception as e:
                update_progress(f"Error: {e}", 0)

        def start_generation():
            progress_label.configure(text="Starting generation...")
            progress_bar.set(0.0)
            stop_event.clear()
            t = threading.Thread(target=run_thread, daemon=True)
            t.start()

        generate_btn = ctk.CTkButton(dialog, text="Generate", command=start_generation)
        generate_btn.pack(pady=5)

        ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack(pady=(0, 10))

    def generate_clips_file_dialog(self, account_name):
        """
        Asks for a local .mp4 file, then uses that account's folder to
        copy the file, and create subclips.
        """
        file_path = fd.askopenfilename(
            title=f"Select local video for {account_name}",
            filetypes=[("MP4 files", "*.mp4"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Generate Clips (File) - {account_name}")
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.attributes("-topmost", False)
        dialog.grab_set()
        dialog.focus_force()

        progress_bar = ctk.CTkProgressBar(dialog, orientation="horizontal", mode="determinate", width=300)
        progress_bar.set(0.0)
        progress_bar.pack(padx=10, pady=5)

        progress_label = ctk.CTkLabel(dialog, text="Waiting to start...")
        progress_label.pack(padx=10, pady=5)

        account_data = self.accounts[account_name]
        output_folder = account_data.get("clip_folder", "")

        stop_event = threading.Event()

        def update_progress(msg, val):
            def _update():
                progress_label.configure(text=msg)
                progress_bar.set(val)

            progress_label.after(0, _update)

        def run_thread():
            if not os.path.exists(file_path):
                update_progress("File does not exist.", 0)
                return
            if not output_folder:
                update_progress("No clip folder set.", 0)
                return
            try:
                update_progress("Copying file (1/2)...", 0.3)

                base_name = os.path.basename(file_path)
                final_path = os.path.join(output_folder, f"{os.path.splitext(base_name)[0]}_final.mp4")
                shutil.copy2(file_path, final_path)

                update_progress("Creating clips (2/2)...", 0.6)

                from moviepy.editor import VideoFileClip
                video = VideoFileClip(final_path)
                clip_duration = account_data.get("clip_duration", 57)
                total_duration = int(video.duration)

                # Put subclips in a "clips" subfolder
                clips_folder = os.path.join(output_folder, "clips")
                if not os.path.exists(clips_folder):
                    os.makedirs(clips_folder)

                number_of_clips = len(os.listdir(clips_folder))

                for start in range(clip_duration, total_duration, clip_duration):
                    if stop_event.is_set():
                        update_progress("Stopped.", 0)
                        video.close()
                        return

                    end = min(start + clip_duration, total_duration)
                    if (end - start) < clip_duration:
                        break

                    clip = video.subclip(start, end)

                    number = start // clip_duration
                    if number_of_clips > 0:
                        number += number_of_clips

                    out_path = os.path.join(clips_folder, f"clip_{number}.mp4")
                    clip.write_videofile(out_path, codec='libx264')

                video.close()
                update_progress("Clips generated successfully!", 1.0)

            except Exception as e:
                update_progress(f"Error: {e}", 0)

        def start_generation():
            progress_label.configure(text="Starting generation...")
            progress_bar.set(0.0)
            stop_event.clear()
            t = threading.Thread(target=run_thread, daemon=True)
            t.start()

        generate_btn = ctk.CTkButton(dialog, text="Generate", command=start_generation)
        generate_btn.pack(pady=5)

        ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack(pady=(0, 10))

    # -------------------------------------------------------------------------
    # Account-Specific Schedule Manager
    # -------------------------------------------------------------------------
    def open_schedule_manager_for_account(self, account_name):
        """
        Manage the weekly schedule for a specific account.
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"{account_name}'s Weekly Schedule")

        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.attributes("-topmost", False)
        dialog.grab_set()
        dialog.focus_force()

        schedule_data = self.accounts[account_name].get("schedule", {})
        for day in DAYS_OF_WEEK:
            schedule_data.setdefault(day, [])

        control_frame = ctk.CTkFrame(dialog, width=400)
        control_frame.pack(padx=10, pady=10)

        day_var = tk.StringVar(value=DAYS_OF_WEEK[0])
        day_menu = ctk.CTkOptionMenu(control_frame, variable=day_var, values=DAYS_OF_WEEK)
        day_menu.pack(side="left", padx=5)

        time_var = tk.StringVar(value="08:00")
        time_entry = ctk.CTkEntry(control_frame, textvariable=time_var, width=70)
        time_entry.pack(side="left", padx=5)

        def add_time():
            d = day_var.get()
            t = time_var.get()
            if d and t:
                schedule_data[d].append(t)
                update_schedule_display()

        add_button = ctk.CTkButton(control_frame, text="Add Time", command=add_time)
        add_button.pack(side="left", padx=5)

        schedule_display = ctk.CTkScrollableFrame(dialog, width=400, height=200)
        schedule_display.pack(padx=10, pady=5, fill="both")

        def remove_time(d, t):
            if t in schedule_data[d]:
                schedule_data[d].remove(t)
                update_schedule_display()

        def update_schedule_display():
            for widget in schedule_display.winfo_children():
                widget.destroy()

            for day_name in DAYS_OF_WEEK:
                times = schedule_data[day_name]
                if times:
                    day_label = ctk.CTkLabel(schedule_display, text=day_name)
                    day_label.pack(anchor="w", padx=5, pady=(5, 2))

                    for tm in times:
                        row = ctk.CTkFrame(schedule_display)
                        row.pack(anchor="w", fill="x", padx=15, pady=2)

                        time_label = ctk.CTkLabel(row, text=tm)
                        time_label.pack(side="left")

                        remove_btn = ctk.CTkButton(
                            row,
                            text="X",
                            width=30,
                            command=lambda dd=day_name, tt=tm: remove_time(dd, tt)
                        )
                        remove_btn.pack(side="right")

        update_schedule_display()

        def close_dialog():
            # Save changes back to the account
            self.accounts[account_name]["schedule"] = schedule_data
            dialog.destroy()

        ctk.CTkButton(dialog, text="Save & Close", command=close_dialog).pack(pady=10, padx=10)
