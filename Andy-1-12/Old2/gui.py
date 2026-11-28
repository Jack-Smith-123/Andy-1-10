import tkinter as tk
from tkinter import ttk
import threading
import asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fishingService import FishingService
from cameraStream import CameraStream

class AlbionBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Andy-1")
        self.root.geometry("380x400")
        self.root.resizable(False, False)
        self.root.configure(bg='#2b2b2b')

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background='#2b2b2b', foreground='#ffffff', fieldbackground='#3c3c3c')
        self.style.configure('TFrame', background='#2b2b2b')
        self.style.configure('TLabel', background='#2b2b2b', foreground='#ffffff', font=('Segoe UI', 10))
        self.style.configure('TButton', background='#4a4a4a', foreground='#ffffff', font=('Segoe UI', 10))
        self.style.map('TButton',
                       background=[('active', '#4a4a4a'), ('pressed', '#3a3a3a')],
                       foreground=[('active', '#ffffff')])
        self.style.configure('Title.TLabel', background='#2b2b2b', foreground='#ffffff', font=('Segoe UI', 13, 'bold'))
        self.style.configure('Status.TLabel', background='#2b2b2b', foreground='#ffffff', font=('Segoe UI', 11, 'bold'))
        self.style.configure('Section.TLabel', background='#2b2b2b', foreground='#ffffff', font=('Segoe UI', 9))

        self.fishing_service = FishingService()
        self.camera_thread = None
        self.cam = None
        self.is_running = False
        self.last_state = None
        self.log_visible = False
        self.show_feed_var = tk.BooleanVar(value=False)
        self.show_state_var = tk.BooleanVar(value=False)

        self._create_widgets()

    def _create_widgets(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill='x', padx=10, pady=4)
        ttk.Label(top_frame, text="Settings", style='Title.TLabel').pack(anchor='w', pady=(0, 4))

        cam_row = ttk.Frame(top_frame)
        cam_row.pack(anchor='w', pady=1)
        ttk.Label(cam_row, text="Camera:").pack(side=tk.LEFT)
        self.cam_index_var = tk.StringVar(value="0")
        ttk.Spinbox(cam_row, from_=0, to=10, textvariable=self.cam_index_var, width=5).pack(side=tk.LEFT, padx=5)

        ttk.Label(top_frame, text="Match threshold (0.30 – 0.95):", style='Section.TLabel').pack(anchor='w', pady=(4, 0))
        self.threshold_var = tk.DoubleVar(value=self.fishing_service.BOBBERT_MATCH_THRESHOLD)
        thr_row = ttk.Frame(top_frame)
        thr_row.pack(anchor='w', pady=1)
        tk.Scale(thr_row, from_=0.30, to=0.95, resolution=0.01, orient=tk.HORIZONTAL,
                 variable=self.threshold_var, length=230, showvalue=0,
                 bg='#3c3c3c', fg='#ffffff', troughcolor='#555555',
                 highlightthickness=0).pack(side=tk.LEFT)
        tk.Spinbox(thr_row, from_=0.30, to=0.95, increment=0.01, textvariable=self.threshold_var,
                   width=6, format="%.2f", bg='#3c3c3c', fg='#ffffff',
                   buttonbackground='#4a4a4a').pack(side=tk.LEFT, padx=5)

        ttk.Label(top_frame, text="Y threshold (1 – 100):", style='Section.TLabel').pack(anchor='w', pady=(4, 0))
        self.bite_var = tk.IntVar(value=self.fishing_service.BITE_Y_THRESHOLD)
        bite_row = ttk.Frame(top_frame)
        bite_row.pack(anchor='w', pady=1)
        tk.Scale(bite_row, from_=1, to=100, resolution=1, orient=tk.HORIZONTAL,
                 variable=self.bite_var, length=230, showvalue=0,
                 bg='#3c3c3c', fg='#ffffff', troughcolor='#555555',
                 highlightthickness=0).pack(side=tk.LEFT)
        tk.Spinbox(bite_row, from_=1, to=100, increment=1, textvariable=self.bite_var,
                   width=5, bg='#3c3c3c', fg='#ffffff',
                   buttonbackground='#4a4a4a').pack(side=tk.LEFT, padx=5)

        apply_btn = tk.Button(top_frame, text="Apply",
                              font=("Segoe UI", 10, "bold"),
                              bg="#5a7d9a", fg="#ffffff", relief=tk.FLAT, cursor="hand2",
                              activebackground="#4a6d8a", activeforeground="#ffffff",
                              width=22, height=2,
                              command=self.apply_settings)
        apply_btn.pack(anchor='w', pady=5)

        self.toggle_btn = tk.Button(top_frame, text="App Inactive",
                                    font=("Segoe UI", 10, "bold"),
                                    bg="#999999", fg="#ffffff", relief=tk.FLAT, cursor="hand2",
                                    activebackground="#888888", activeforeground="#ffffff",
                                    width=22, height=2,
                                    command=self.toggle_bot)
        self.toggle_btn.pack(anchor='w', pady=5)

        status_frame = ttk.Frame(top_frame)
        status_frame.pack(anchor='w', pady=2)
        self.f1_indicator = tk.Label(status_frame, text="F1",
                                     font=("Segoe UI", 10, "bold"),
                                     bg="#999999", fg="#ffffff",
                                     width=4, height=2,
                                     relief=tk.FLAT)
        self.f1_indicator.pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="Stopped")
        ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel').pack(side=tk.LEFT, padx=(10, 0))

        self.show_log_btn = tk.Button(top_frame, text="Show Log & Debug",
                                      font=("Segoe UI", 10, "bold"),
                                      bg="#5a7d9a", fg="#ffffff", relief=tk.FLAT, cursor="hand2",
                                      activebackground="#4a6d8a", activeforeground="#ffffff",
                                      width=22, height=2,
                                      command=self.toggle_log)
        self.show_log_btn.pack(anchor='w', pady=5)

        self.log_frame = ttk.Frame(self.root)
        ttk.Label(self.log_frame, text="Debug Options:", style='Section.TLabel').pack(anchor='w', pady=(5, 0))
        tk.Checkbutton(self.log_frame, text="Show OBS Feed", variable=self.show_feed_var,
                       bg='#2b2b2b', fg='#ffffff', selectcolor='#3c3c3c',
                       activebackground='#2b2b2b', activeforeground='#ffffff',
                       highlightthickness=0,
                       command=self.toggle_debug_windows).pack(anchor='w')
        tk.Checkbutton(self.log_frame, text="Show State Change", variable=self.show_state_var,
                       bg='#2b2b2b', fg='#ffffff', selectcolor='#3c3c3c',
                       activebackground='#2b2b2b', activeforeground='#ffffff',
                       highlightthickness=0,
                       command=self.toggle_debug_windows).pack(anchor='w')

        ttk.Separator(self.log_frame, orient='horizontal').pack(fill='x', pady=8)
        ttk.Label(self.log_frame, text="Log:", style='Title.TLabel').pack(anchor='w')
        self.log_text = tk.Text(self.log_frame, height=14, font=("Consolas", 9),
                                bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff",
                                selectbackground="#264f78", selectforeground="#ffffff",
                                wrap=tk.WORD, state=tk.DISABLED, relief=tk.FLAT)
        self.log_text.pack(fill='both', expand=True, pady=3)
        scrollbar = ttk.Scrollbar(self.log_text, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        btn_frame = ttk.Frame(self.log_frame)
        btn_frame.pack(anchor='w', pady=2)
        ttk.Button(btn_frame, text="Clear", command=self.clear_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Copy all", command=self.copy_log).pack(side=tk.LEFT, padx=2)

        self.log("Ready. Configure and click Apply.")
        self.root.after(100, self.update_status)

    def toggle_log(self):
        if not self.log_visible:
            self.log_frame.pack(fill='both', expand=True, padx=10, pady=4)
            self.show_log_btn.config(text="Hide Log & Debug")
            self.root.geometry("380x700")
            self.log_visible = True
        else:
            self.log_frame.pack_forget()
            self.show_log_btn.config(text="Show Log & Debug")
            self.root.geometry("380x400")
            self.log_visible = False

    def apply_settings(self):
        self.fishing_service.BOBBERT_MATCH_THRESHOLD = self.threshold_var.get()
        self.fishing_service.BITE_Y_THRESHOLD = self.bite_var.get()
        self.log(f"Applied: threshold={self.threshold_var.get():.2f}, Y={self.bite_var.get()}")

    def toggle_debug_windows(self):
        self.fishing_service.show_obs_feed = self.show_feed_var.get()
        self.fishing_service.show_state_change = self.show_state_var.get()

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def copy_log(self):
        self.log_text.config(state=tk.NORMAL)
        content = self.log_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()
        self.log("Log copied to clipboard")

    def toggle_bot(self):
        if not self.is_running:
            self.is_running = True
            self.toggle_btn.config(text="App Active", bg="#6a9a6a", activebackground="#5a8a5a")
            self.status_var.set("Starting...")
            self.log("Starting...")
            self.camera_thread = threading.Thread(target=self.run_bot_loop, daemon=True)
            self.camera_thread.start()
        else:
            self.is_running = False
            self.fishing_service.fishing_active = False
            if self.cam is not None:
                self.cam.running = False
            self.toggle_btn.config(text="App Inactive", bg="#999999", activebackground="#888888")
            self.status_var.set("Stopping...")
            self.log("Stopping...")

    def run_bot_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            try:
                cam_index = int(self.cam_index_var.get())
            except ValueError:
                cam_index = 0
            self.cam = CameraStream(camera_index=cam_index, fishing_service=self.fishing_service)
            loop.run_until_complete(self.cam.run_camera_feed())
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Error: {e}"))
        finally:
            loop.close()
            self.is_running = False
            self.root.after(0, self.reset_ui)

    def reset_ui(self):
        self.toggle_btn.config(text="App Inactive", bg="#999999", activebackground="#888888")
        self.f1_indicator.config(bg="#999999")
        self.status_var.set("Stopped")
        self.log("Stopped")

    def update_status(self):
        if self.is_running:
            state = self.fishing_service.state
            is_active = self.fishing_service.fishing_active
            if is_active:
                self.f1_indicator.config(bg="#6a9a6a")
            else:
                self.f1_indicator.config(bg="#999999")
            if is_active:
                status_map = {
                    "STARTING": "Casting...",
                    "HOOK": "Waiting...",
                    "MINI_GAME": "Mini-game!",
                    "RESTART": "Restarting..."
                }
                current_status = status_map.get(state, "Unknown")
                self.status_var.set(f"Active: {current_status}")
                if self.last_state != state:
                    self.log(f"State: {current_status}")
                    self.last_state = state
            else:
                self.status_var.set("Paused")
        self.root.after(200, self.update_status)


if __name__ == "__main__":
    root = tk.Tk()
    app = AlbionBotGUI(root)
    root.mainloop()
