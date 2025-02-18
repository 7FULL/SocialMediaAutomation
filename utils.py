import customtkinter as ctk
import tkinter as tk
import json
import os


def load_config(config_path="config/config.json"):
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config_data, config_path="config/config.json"):
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)
