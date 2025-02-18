import customtkinter as ctk

from gui.social_media_panel import SocialMediaPanel
from utils import load_config, save_config


class MainPanel(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Panel de Control - Social Media Automation")
        self.geometry("600x525")

        # Load config data
        self.config_data = load_config()

        # Create tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        # Create tabs
        self.create_tabs(["YouTube", "TikTok", "Instagram", "Twitter"])

        # Save button
        save_button = ctk.CTkButton(self, text="Guardar Configuración", command=self.save_all_config)
        save_button.pack(pady=10)

    def create_tabs(self, social_medias):
        """Create a tab for each social media."""
        for media in social_medias:
            tab = self.tabview.add(media)

            panel = SocialMediaPanel(tab, social_media_name=media, config_data=self.config_data)
            panel.pack(expand=True, fill="both")

    def save_all_config(self):
        """Save the configuration of all tabs."""
        for media in self.tabview._tab_dict:
            child_widgets = self.tabview.tab(media).winfo_children()
            for widget in child_widgets:
                if isinstance(widget, SocialMediaPanel):
                    widget.save_panel_config()

        # Save global configuration
        save_config(self.config_data)
        print("[INFO] Configuración guardada en config/config.json")