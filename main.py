import customtkinter as ctk

from gui.main_panel import MainPanel

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")  # "Light" / "Dark" / "System"
    ctk.set_default_color_theme("blue")
    app = MainPanel()
    app.mainloop()
