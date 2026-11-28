import customtkinter as ctk
import cv2
from PIL import Image, ImageTk

class VideoWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Зрение бота")
        self.geometry("320x240+0+600")
        self.resizable(True, True)
        self.parent_ref = parent
        self.video_label = ctk.CTkLabel(self, text="Ожидание видеопотока...")
        self.video_label.pack(fill="both", expand=True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Configure>", self.on_resize)
        self.current_size = (320, 240)

    def on_resize(self, event):
        if event.widget == self:
            self.current_size = (event.width, event.height)

    def update_frame(self, frame):
        if frame is None:
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, self.current_size, interpolation=cv2.INTER_AREA)
        img = Image.fromarray(rgb)
        self.photo = ImageTk.PhotoImage(image=img)
        self.video_label.configure(image=self.photo, text="")

    def on_close(self):
        self.parent_ref.video_window = None
        self.destroy()
