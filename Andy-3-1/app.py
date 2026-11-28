import customtkinter as ctk
import threading
import time
import cv2
import numpy as np
from capture import find_albion_window, grab_frame, get_cursor_position
from config import load_config
from logger import log_manager
from gui_video import VideoWindow
from gui_settings import SettingsWindow
from gui_log import LogWindow

class MinimalBotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Andy-3 App")
        self.geometry("320x400+0+0")
        self.resizable(False, False)
        self.window_data = None
        self.bot_enabled = False  # Включен ли бот вообще
        self.bot_acting = False   # Действует ли бот
        self.video_window = None
        self.settings_window = None
        self.log_window = None
        self.video_thread = None
        self.video_running = False
        self.config = load_config()
        self.fps = self.config.get("bot", {}).get("fps", 20)
        self.font_size = self.config.get("app", {}).get("font_size", 12)
        self.setup_ui()
        log_manager.log("Приложение запущено", "Система")

    def setup_ui(self):
        self.label_title = ctk.CTkLabel(self, text="Панель управления", font=("Arial", self.font_size, "bold"))
        self.label_title.pack(pady=(15, 5))
        
        self.label_status = ctk.CTkLabel(self, text="Статус: Выключен", text_color="gray", font=("Arial", self.font_size))
        self.label_status.pack(pady=5)
        
        self.btn_find = ctk.CTkButton(self, text="🔍 Найти окно игры", command=self.find_window, font=("Arial", self.font_size))
        self.btn_find.pack(pady=8)
        
        # Кнопка 1: Включить/Выключить бота
        self.btn_enable = ctk.CTkButton(self, text="🟢 Включить бота", state="disabled", command=self.toggle_enable, font=("Arial", self.font_size))
        self.btn_enable.pack(pady=5)
        
        # Кнопка 2: Действовать/Пауза
        self.btn_act = ctk.CTkButton(self, text="▶️ Начать действовать", state="disabled", command=self.toggle_acting, font=("Arial", self.font_size))
        self.btn_act.pack(pady=5)
        
        self.btn_video = ctk.CTkButton(self, text="📹 Видео", command=self.open_video, font=("Arial", self.font_size))
        self.btn_video.pack(pady=5)
        
        self.btn_settings = ctk.CTkButton(self, text="⚙️ Настройки", command=self.open_settings, font=("Arial", self.font_size))
        self.btn_settings.pack(pady=5)
        
        self.btn_log = ctk.CTkButton(self, text="📝 Лог", command=self.open_log, font=("Arial", self.font_size))
        self.btn_log.pack(pady=5)

    def apply_font_size(self, size):
        self.font_size = size
        font = ("Arial", size)
        font_bold = ("Arial", size, "bold")
        self.label_title.configure(font=font_bold)
        self.label_status.configure(font=font)
        self.btn_find.configure(font=font)
        self.btn_enable.configure(font=font)
        self.btn_act.configure(font=font)
        self.btn_video.configure(font=font)
        self.btn_settings.configure(font=font)
        self.btn_log.configure(font=font)

    def update_fps(self, fps):
        self.fps = fps
        log_manager.log(f"FPS изменен на: {fps}", "Система")

    def find_window(self):
        self.label_status.configure(text="Статус: Поиск...", text_color="yellow")
        self.update()
        result = find_albion_window()
        if isinstance(result, dict):
            self.window_data = result
            coords = f"X:{result['left']}, Y:{result['top']}, W:{result['width']}, H:{result['height']}"
            self.label_status.configure(text=f"✅ Окно найдено!\n{coords}", text_color="green")
            self.btn_enable.configure(state="normal")  # Разблокируем кнопку включения
            log_manager.log(f"Окно найдено: {coords}", "Система")
        else:
            self.label_status.configure(text=f"❌ Ошибка: {result}", text_color="red")
            self.window_data = None
            self.btn_enable.configure(state="disabled")
            log_manager.log(f"Ошибка поиска окна: {result}", "Система")

    def toggle_enable(self):
        """Включает/выключает весь функционал бота."""
        self.bot_enabled = not self.bot_enabled
        if self.bot_enabled:
            self.btn_enable.configure(text="🔴 Выключить бота")
            self.label_status.configure(text="Статус: Включен (ожидание)", text_color="green")
            self.btn_act.configure(state="normal")  # Разблокируем кнопку действий
            self.start_video_capture()
            log_manager.log("Бот включен", "Система")
        else:
            self.btn_enable.configure(text="🟢 Включить бота")
            self.label_status.configure(text="Статус: Выключен", text_color="gray")
            self.btn_act.configure(state="disabled")  # Блокируем кнопку действий
            self.bot_acting = False
            self.btn_act.configure(text="▶️ Начать действовать")
            self.stop_video_capture()
            log_manager.log("Бот выключен", "Система")

    def toggle_acting(self):
        """Запускает/останавливает активные действия бота."""
        self.bot_acting = not self.bot_acting
        if self.bot_acting:
            self.btn_act.configure(text="⏸️ Пауза")
            self.label_status.configure(text="Статус: Действует", text_color="green")
            log_manager.log("Бот начал действовать", "Система")
        else:
            self.btn_act.configure(text="▶️ Начать действовать")
            self.label_status.configure(text="Статус: Включен (ожидание)", text_color="yellow")
            log_manager.log("Бот на паузе", "Система")

    def start_video_capture(self):
        if not self.window_data:
            return
        self.video_running = True
        self.video_thread = threading.Thread(target=self._video_loop, daemon=True)
        self.video_thread.start()

    def stop_video_capture(self):
        self.video_running = False

    def _video_loop(self):
        monitor = {
            "left": self.window_data["left"],
            "top": self.window_data["top"],
            "width": self.window_data["width"],
            "height": self.window_data["height"]
        }
        frame_count = 0
        while self.video_running:
            try:
                sleep_time = 1.0 / max(1, self.fps)
                self.config = load_config()
                frame = grab_frame(monitor)
                
                # Рисуем зоны только если бот включен
                if self.bot_enabled:
                    frame = self.draw_zones(frame)
                
                if self.video_window and self.video_window.winfo_exists():
                    self.video_window.after(0, lambda f=frame: self.video_window.update_frame(f))
                
                frame_count += 1
                if frame_count % 100 == 0:
                    log_manager.log(f"Захвачено кадров: {frame_count}", "Захват")
            except Exception as e:
                log_manager.log(f"Ошибка захвата: {e}", "Захват")
            time.sleep(sleep_time)

    def draw_zones(self, frame):
        if not self.config["zone"]["show"]:
            return frame
        
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        zone = self.config["zone"]
        color = (zone["color_b"], zone["color_g"], zone["color_r"])
        size = zone["square_size"]
        distance = zone["distance"]
        
        cursor = get_cursor_position(self.window_data)
        
        if cursor:
            cx, cy = cursor
            
            # Рисуем голубой крестик
            cross_size = 10
            cross_color = (255, 200, 100)
            cv2.line(frame, (cx - cross_size, cy), (cx + cross_size, cy), cross_color, 2)
            cv2.line(frame, (cx, cy - cross_size), (cx, cy + cross_size), cross_color, 2)
            
            dx = cx - center_x
            dy = cy - center_y
            length = np.sqrt(dx**2 + dy**2)
            
            if length > 0:
                dx_norm = dx / length
                dy_norm = dy / length
                max_length = max(w, h)
                end_x = int(center_x + dx_norm * max_length)
                end_y = int(center_y + dy_norm * max_length)
                
                cv2.line(frame, (center_x, center_y), (end_x, end_y), color, 2)
                
                for i in range(5):
                    sq_x = int(center_x + dx_norm * (i * distance))
                    sq_y = int(center_y + dy_norm * (i * distance))
                    half = size // 2
                    cv2.rectangle(frame, 
                                 (sq_x - half, sq_y - half),
                                 (sq_x + half, sq_y + half), 
                                 color, 2)
        else:
            end_x = w
            end_y = center_y
            cv2.line(frame, (center_x, center_y), (end_x, end_y), color, 2)
            
            for i in range(5):
                sq_x = center_x + (i * distance)
                sq_y = center_y
                half = size // 2
                cv2.rectangle(frame, 
                             (sq_x - half, sq_y - half),
                             (sq_x + half, sq_y + half), 
                             color, 2)
        
        return frame

    def open_video(self):
        if self.video_window and self.video_window.winfo_exists():
            self.video_window.focus()
            return
        if not self.window_data:
            self.label_status.configure(text="❌ Сначала найдите окно игры", text_color="red")
            return
        self.video_window = VideoWindow(self)

    def open_settings(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.focus()
            return
        self.settings_window = SettingsWindow(self)

    def open_log(self):
        if self.log_window and self.log_window.winfo_exists():
            self.log_window.focus()
            return
        self.log_window = LogWindow(self)
