import customtkinter as ctk
from app import MinimalBotGUI

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = MinimalBotGUI()
    app.mainloop()
