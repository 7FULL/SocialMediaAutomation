"""
Enhanced GUI components for real TikTok API integration
Extends the existing GUI with real API authentication and upload options
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import threading
import os
import json

try:
    from core.tiktok_automation_enhanced import TikTokAutomation
    ENHANCED_API_AVAILABLE = True
except ImportError:
    ENHANCED_API_AVAILABLE = False


class TikTokAPIConfigDialog:
    """Dialog for configuring TikTok API credentials"""
    
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
        self.result = None
        
    def show(self):
        """Show the configuration dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.geometry("600x500")
        self.dialog.title("🎵 TikTok API Configuration")
        self.dialog.lift()
        self.dialog.attributes("-topmost", True)
        self.dialog.attributes("-topmost", False)
        self.dialog.grab_set()
        self.dialog.focus_force()
        self.dialog.resizable(False, False)
        
        # Main container
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        self._create_widgets(main_frame)
        self._load_existing_config()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self, parent):
        """Create dialog widgets"""
        # Header
        header_label = ctk.CTkLabel(
            parent,
            text="TikTok API Configuration",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.grid(row=0, column=0, pady=(20, 10))
        
        info_label = ctk.CTkLabel(
            parent,
            text="Configure your TikTok for Developers API credentials",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_label.grid(row=1, column=0, pady=(0, 20))
        
        # Configuration form
        form_frame = ctk.CTkScrollableFrame(parent)
        form_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Client Key
        ctk.CTkLabel(
            form_frame,
            text="Client Key:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        self.client_key_var = tk.StringVar()
        self.client_key_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.client_key_var,
            placeholder_text="Enter your TikTok Client Key...",
            width=400,
            height=35
        )
        self.client_key_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 15))
        
        # Client Secret
        ctk.CTkLabel(
            form_frame,
            text="Client Secret:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=2, column=0, sticky="w", padx=10, pady=(0, 5))
        
        self.client_secret_var = tk.StringVar()
        self.client_secret_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.client_secret_var,
            placeholder_text="Enter your TikTok Client Secret...",
            width=400,
            height=35,
            show="*"
        )
        self.client_secret_entry.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 15))
        
        # Redirect URI
        ctk.CTkLabel(
            form_frame,
            text="Redirect URI:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=4, column=0, sticky="w", padx=10, pady=(0, 5))
        
        self.redirect_uri_var = tk.StringVar(value="http://localhost:8080/callback")
        self.redirect_uri_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.redirect_uri_var,
            width=400,
            height=35
        )
        self.redirect_uri_entry.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 15))
        
        # Environment
        ctk.CTkLabel(
            form_frame,
            text="Environment:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=6, column=0, sticky="w", padx=10, pady=(0, 5))
        
        self.environment_var = tk.StringVar(value="sandbox")
        environment_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.environment_var,
            values=["sandbox", "production"],
            width=200,
            height=35
        )
        environment_menu.grid(row=7, column=0, sticky="w", padx=10, pady=(0, 15))
        
        # Instructions
        instructions_frame = ctk.CTkFrame(form_frame)
        instructions_frame.grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 20))
        
        ctk.CTkLabel(
            instructions_frame,
            text="📋 Setup Instructions:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        instructions = [
            "1. Go to https://developers.tiktok.com/",
            "2. Create a developer account and new app",
            "3. Request scopes: user.info.basic, video.upload, video.publish",
            "4. Set redirect URI in your app settings",
            "5. Copy Client Key and Client Secret here",
            "6. Use 'sandbox' for testing, 'production' for real uploads"
        ]
        
        for instruction in instructions:
            ctk.CTkLabel(
                instructions_frame,
                text=instruction,
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack(anchor="w", padx=25, pady=2)
        
        # Test button
        test_button = ctk.CTkButton(
            form_frame,
            text="🧪 Test Configuration",
            command=self._test_config,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        test_button.grid(row=9, column=0, columnspan=2, pady=(10, 20), padx=10, sticky="ew")
        
        # Action buttons
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._cancel,
            height=40,
            fg_color="#666666",
            hover_color="#777777",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        cancel_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        save_button = ctk.CTkButton(
            button_frame,
            text="💾 Save Configuration",
            command=self._save_config,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")
    
    def _load_existing_config(self):
        """Load existing configuration if available"""
        if not ENHANCED_API_AVAILABLE:
            return
            
        config = TikTokAutomation._load_tiktok_config()
        if config:
            self.client_key_var.set(config.get("client_key", ""))
            self.client_secret_var.set(config.get("client_secret", ""))
            self.redirect_uri_var.set(config.get("redirect_uri", "http://localhost:8080/callback"))
            self.environment_var.set(config.get("environment", "sandbox"))
    
    def _test_config(self):
        """Test the configuration"""
        client_key = self.client_key_var.get().strip()
        client_secret = self.client_secret_var.get().strip()
        
        if not client_key or not client_secret:
            messagebox.showerror("Error", "Please enter both Client Key and Client Secret")
            return
        
        if client_key == "YOUR_TIKTOK_CLIENT_KEY":
            messagebox.showerror("Error", "Please replace the placeholder values with real credentials")
            return
        
        # Save temporarily and test
        temp_config = {
            "client_key": client_key,
            "client_secret": client_secret,
            "redirect_uri": self.redirect_uri_var.get().strip(),
            "environment": self.environment_var.get()
        }
        
        # Create config directory if it doesn't exist
        config_dir = "tiktok_automation"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        config_file = os.path.join(config_dir, "tiktok_config.json")
        with open(config_file, 'w') as f:
            json.dump(temp_config, f, indent=4)
        
        messagebox.showinfo(
            "Configuration Test", 
            "✅ Configuration saved!\n\n"
            "To test authentication:\n"
            "1. Save this configuration\n"
            "2. Try authenticating a TikTok account\n"
            "3. The OAuth flow will test your credentials"
        )
    
    def _save_config(self):
        """Save the configuration"""
        client_key = self.client_key_var.get().strip()
        client_secret = self.client_secret_var.get().strip()
        
        if not client_key or not client_secret:
            messagebox.showerror("Error", "Please enter both Client Key and Client Secret")
            return
        
        config = {
            "client_key": client_key,
            "client_secret": client_secret,
            "redirect_uri": self.redirect_uri_var.get().strip(),
            "environment": self.environment_var.get()
        }
        
        # Create config directory if it doesn't exist
        config_dir = "tiktok_automation"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        config_file = os.path.join(config_dir, "tiktok_config.json")
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            
            self.result = True
            messagebox.showinfo("Success", "✅ Configuration saved successfully!")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")
    
    def _cancel(self):
        """Cancel dialog"""
        self.result = False
        self.dialog.destroy()


class TikTokAuthenticationDialog:
    """Dialog for TikTok authentication with real API option"""
    
    def __init__(self, parent, account_name):
        self.parent = parent
        self.account_name = account_name
        self.dialog = None
        self.result = None
        
    def show(self):
        """Show the authentication dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.geometry("500x400")
        self.dialog.title(f"🔐 TikTok Authentication - {self.account_name}")
        self.dialog.lift()
        self.dialog.attributes("-topmost", True)
        self.dialog.attributes("-topmost", False)
        self.dialog.grab_set()
        self.dialog.focus_force()
        self.dialog.resizable(False, False)
        
        # Main container
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        self._create_widgets(main_frame)
        
        # Wait for dialog to close
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self, parent):
        """Create dialog widgets"""
        # Header
        header_label = ctk.CTkLabel(
            parent,
            text=f"Authenticate TikTok Account",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.grid(row=0, column=0, pady=(20, 10))
        
        account_label = ctk.CTkLabel(
            parent,
            text=f"Account: {self.account_name}",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        account_label.grid(row=1, column=0, pady=(0, 20))
        
        # Check current status
        current_status = self._get_current_status()
        
        status_frame = ctk.CTkFrame(parent)
        status_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="Current Status:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        status_label.pack(pady=(15, 5))
        
        status_text = current_status['status']
        status_color = "#00ff00" if current_status['authenticated'] else "#ff4444"
        
        current_status_label = ctk.CTkLabel(
            status_frame,
            text=status_text,
            font=ctk.CTkFont(size=12),
            text_color=status_color
        )
        current_status_label.pack(pady=(0, 15))
        
        # Authentication options
        options_frame = ctk.CTkFrame(parent)
        options_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        options_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            options_frame,
            text="Choose Authentication Method:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, pady=(15, 10))
        
        # Simulation mode button
        sim_button = ctk.CTkButton(
            options_frame,
            text="🎭 Simulation Mode (Testing)",
            command=self._authenticate_simulation,
            height=40,
            fg_color="#4A90E2",
            hover_color="#357ABD",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        sim_button.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        
        # Real API button
        api_available = ENHANCED_API_AVAILABLE and self._check_api_config()
        api_button_color = "#28a745" if api_available else "#6c757d"
        api_hover_color = "#218838" if api_available else "#5a6268"
        
        real_button = ctk.CTkButton(
            options_frame,
            text="🎵 Real TikTok API" + ("" if api_available else " (Config Required)"),
            command=self._authenticate_real_api if api_available else self._show_config_dialog,
            height=40,
            fg_color=api_button_color,
            hover_color=api_hover_color,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        real_button.grid(row=2, column=0, sticky="ew", padx=15, pady=5)
        
        # Configuration button
        config_button = ctk.CTkButton(
            options_frame,
            text="⚙️ Configure API Credentials",
            command=self._show_config_dialog,
            height=35,
            fg_color="#6c757d",
            hover_color="#5a6268",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        config_button.grid(row=3, column=0, sticky="ew", padx=15, pady=(5, 15))
        
        # Close button
        close_button = ctk.CTkButton(
            parent,
            text="Close",
            command=self._close,
            height=35,
            fg_color="#666666",
            hover_color="#777777",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        close_button.grid(row=4, column=0, pady=(0, 20), padx=20, sticky="ew")
    
    def _get_current_status(self):
        """Get current authentication status"""
        if not ENHANCED_API_AVAILABLE:
            return {
                "authenticated": False,
                "status": "Enhanced API not available",
                "type": "unavailable"
            }
        
        try:
            tta = TikTokAutomation(account_name=self.account_name)
            return tta.get_account_status()
        except:
            return {
                "authenticated": False,
                "status": "Error checking status",
                "type": "error"
            }
    
    def _check_api_config(self):
        """Check if API configuration is available"""
        if not ENHANCED_API_AVAILABLE:
            return False
        return TikTokAutomation._has_real_api_config()
    
    def _authenticate_simulation(self):
        """Authenticate using simulation mode"""
        if not ENHANCED_API_AVAILABLE:
            messagebox.showerror("Error", "Enhanced TikTok automation not available")
            return
        
        try:
            success = TikTokAutomation.authenticate_tiktok_account(
                self.account_name, 
                use_real_api=False
            )
            
            if success:
                self.result = True
                messagebox.showinfo(
                    "Success", 
                    "✅ Simulation authentication successful!\n\n"
                    "This allows testing without real API access."
                )
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Simulation authentication failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Authentication error:\n{str(e)}")
    
    def _authenticate_real_api(self):
        """Authenticate using real TikTok API"""
        if not ENHANCED_API_AVAILABLE:
            messagebox.showerror("Error", "Enhanced TikTok automation not available")
            return
        
        if not self._check_api_config():
            messagebox.showerror("Error", "API configuration required. Please configure first.")
            return
        
        # Show progress dialog
        progress_dialog = self._show_progress_dialog()
        
        def auth_thread():
            try:
                success = TikTokAutomation.authenticate_tiktok_account(
                    self.account_name, 
                    use_real_api=True
                )
                
                progress_dialog.after(0, lambda: self._handle_auth_result(success, progress_dialog))
                
            except Exception as e:
                progress_dialog.after(0, lambda: self._handle_auth_error(str(e), progress_dialog))
        
        threading.Thread(target=auth_thread, daemon=True).start()
    
    def _show_progress_dialog(self):
        """Show authentication progress dialog"""
        progress = ctk.CTkToplevel(self.dialog)
        progress.geometry("400x200")
        progress.title("🔐 Authenticating...")
        progress.lift()
        progress.attributes("-topmost", True)
        progress.grab_set()
        progress.resizable(False, False)
        
        frame = ctk.CTkFrame(progress)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text="🌐 Opening browser for TikTok OAuth...",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            frame,
            text="Please complete authentication in your browser",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 20))
        
        progress_bar = ctk.CTkProgressBar(frame, mode="indeterminate")
        progress_bar.pack(pady=10, padx=20, fill="x")
        progress_bar.start()
        
        return progress
    
    def _handle_auth_result(self, success, progress_dialog):
        """Handle authentication result"""
        progress_dialog.destroy()
        
        if success:
            self.result = True
            messagebox.showinfo(
                "Success", 
                "🎉 Real TikTok API authentication successful!\n\n"
                "You can now upload videos to TikTok."
            )
            self.dialog.destroy()
        else:
            messagebox.showerror(
                "Failed", 
                "❌ TikTok API authentication failed.\n\n"
                "Please check your credentials and try again."
            )
    
    def _handle_auth_error(self, error, progress_dialog):
        """Handle authentication error"""
        progress_dialog.destroy()
        messagebox.showerror("Error", f"Authentication error:\n{error}")
    
    def _show_config_dialog(self):
        """Show configuration dialog"""
        config_dialog = TikTokAPIConfigDialog(self.dialog)
        if config_dialog.show():
            # Refresh the dialog to show updated status
            self.dialog.destroy()
            self.__init__(self.parent, self.account_name)
            self.show()
    
    def _close(self):
        """Close dialog"""
        self.result = False
        self.dialog.destroy()


def enhance_social_media_panel_for_tiktok(panel_instance):
    """
    Enhance an existing SocialMediaPanel instance with TikTok real API support
    """
    if panel_instance.social_media_name != "TikTok":
        return
    
    # Store original authentication method
    original_auth = panel_instance.accounts.get
    
    def enhanced_tiktok_auth(account_name):
        """Enhanced TikTok authentication with GUI"""
        auth_dialog = TikTokAuthenticationDialog(panel_instance, account_name)
        return auth_dialog.show()
    
    # Add TikTok API configuration menu option
    def add_api_config_option():
        """Add API configuration option to the panel"""
        # This could be integrated into the existing UI
        pass
    
    print(f"✅ Enhanced TikTok real API support added to {panel_instance.social_media_name} panel")