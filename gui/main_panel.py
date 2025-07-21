import customtkinter as ctk
from tkinter import messagebox

from gui.social_media_panel import SocialMediaPanel
from utils import load_config, save_config
from tiktok_support_patch import apply_tiktok_patch


class MainPanel(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("📱 Social Media Automation Control Panel")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Load config data
        self.config_data = load_config()

        # Create main container
        self.main_container = ctk.CTkFrame(self, corner_radius=10)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        # Create header
        self.create_header()

        # Create tabview
        self.tabview = ctk.CTkTabview(self.main_container, corner_radius=10)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))

        # Create tabs
        self.create_tabs(["YouTube", "TikTok", "Instagram", "Twitter"])

        # Create footer with save button
        self.create_footer()

    def create_header(self):
        """Create the header section with title and status."""
        header_frame = ctk.CTkFrame(self.main_container, corner_radius=10, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Social Media Automation Suite",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Status indicator
        status_frame = ctk.CTkFrame(header_frame, corner_radius=8)
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="🟢 System Ready",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00ff00"
        )
        status_label.pack(pady=8)

    def create_tabs(self, social_medias):
        """Create a tab for each social media with professional styling."""
        # Define icons for each platform
        icons = {
            "YouTube": "🎥",
            "TikTok": "🎵",
            "Instagram": "📸",
            "Twitter": "🐦"
        }
        
        for media in social_medias:
            tab_name = f"{icons.get(media, '📱')} {media}"
            tab = self.tabview.add(tab_name)

            panel = SocialMediaPanel(tab, social_media_name=media, config_data=self.config_data)
            panel.pack(expand=True, fill="both", padx=10, pady=10)
            
            # Apply TikTok patch if this is a TikTok panel
            if media == "TikTok":
                apply_tiktok_patch(panel)
            
    def create_footer(self):
        """Create the footer with action buttons."""
        footer_frame = ctk.CTkFrame(self.main_container, corner_radius=10, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        footer_frame.grid_columnconfigure(1, weight=1)
        
        # Save button with better styling
        save_button = ctk.CTkButton(
            footer_frame,
            text="💾 Save Configuration",
            command=self.save_all_config,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=8
        )
        save_button.grid(row=0, column=0, padx=(0, 10), pady=10)
        
        # About button
        about_button = ctk.CTkButton(
            footer_frame,
            text="ℹ️ About",
            command=self.show_about,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=8,
            fg_color="#4A4A4A",
            hover_color="#5A5A5A"
        )
        about_button.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="e")

    def save_all_config(self):
        """Save the configuration of all tabs with user feedback."""
        try:
            for media in self.tabview._tab_dict:
                child_widgets = self.tabview.tab(media).winfo_children()
                for widget in child_widgets:
                    if isinstance(widget, SocialMediaPanel):
                        widget.save_panel_config()

            # Save global configuration
            save_config(self.config_data)
            
            # Show success message
            messagebox.showinfo(
                "Success",
                "✅ Configuration saved successfully!"
            )
            print("[INFO] Configuration saved to config/config.json")
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"❌ Failed to save configuration:\n{str(e)}"
            )
            print(f"[ERROR] Failed to save configuration: {e}")
            
    def show_about(self):
        """Show about dialog."""
        about_text = (
            "Social Media Automation Suite\n\n"
            "Version: 1.0\n"
            "A professional tool for automating social media content\n\n"
            "Features:\n"
            "• Multi-platform support\n"
            "• Automated scheduling\n"
            "• Content generation\n"
            "• Account management\n\n"
            "Developed with ❤️ using CustomTkinter"
        )
        messagebox.showinfo("About", about_text)