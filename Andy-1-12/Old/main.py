"""
Точка входа и оркестратор Andy-1-3.
Связывает GUI, захват экрана, контроллер мыши и сервис рыбалки.
Окно бота прилипает к левому верхнему углу экрана.
"""
import sys
import os
import time
import threading
import customtkinter as ctk

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import ConfigMixin
from window_utils import find_game_window
from screen_capture import ScreenCapture
from input_controller import InputController
from hotkey_service import HotkeyService
from fishing_service import FishingService
from gui import Andy1GUI

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Andy1App(ConfigMixin):
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Andy-1-3")
        
        # 🆕 Окно прилипает к левому верхнему углу экрана (x=0, y=0)
        self.root.geometry("380x450+0+0")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.config = self._load_config()
        self.bot_running = False
        self._stop_event = threading.Event()
        self._pending_frame = None  # последний помеченный кадр для превью

        # 1. Сначала создаём GUI
        self.gui = Andy1GUI(self)

        # 2. Инициализация сервисов
        self.capture = ScreenCapture(target_fps=self.config.get("capture_fps", 20))
        self.input_ctrl = InputController()
        self.hotkey = HotkeyService()
        self.fishing = FishingService(self.config, self.input_ctrl, log_callback=self.log)

        # Горячая клавиша
        self.hotkey.register(self.config.get("hotkey_toggle", "f1"), self._toggle_bot)
        self.hotkey.start()

    def log(self, msg):
        if hasattr(self, 'gui') and self.gui:
            self.gui.log(msg)
        else:
            print(msg)

    def _toggle_bot(self):
        self.root.after(0, self._toggle_bot_safe)

    def _toggle_bot_safe(self):
        if self.bot_running:
            self.stop_bot()
        else:
            self.start_bot()

    def start_bot(self):
        if self.bot_running:
            return
        self.bot_running = True
        self._stop_event.clear()
        self.fishing.set_active(True)

        threading.Thread(target=self._bot_loop, daemon=True).start()
        self.log("▶️ Бот запущен!")

    def stop_bot(self):
        if not self.bot_running:
            return
        self.bot_running = False
        self._stop_event.set()
        self.fishing.set_active(False)
        self.input_ctrl.cleanup()
        self.capture.stop()
        self.log("⏹ Бот остановлен!")

    def _bot_loop(self):
        # 1. Поиск окна
        self.log("🔍 Поиск окна Albion...")
        geometry = None
        for _ in range(30):
            geometry = find_game_window(self.config.get("window_title_hint"))
            if geometry:
                break
            time.sleep(0.5)

        if not geometry:
            self.log("❌ Окно не найдено! Проверь wmctrl/xdotool.")
            self.bot_running = False
            self.fishing.set_active(False)
            return

        # 2. Настройка захвата и мыши
        self.capture.set_region(geometry["left"], geometry["top"],
                                geometry["width"], geometry["height"])
        self.input_ctrl.set_window(geometry)
        self.capture.start()
        self.log(f"✓ Окно найдено: {geometry['width']}x{geometry['height']}")

        # 3. Главный цикл обработки
        last_preview_update = 0
        while not self._stop_event.is_set():
            frame = self.capture.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            # Логика рыбалки (возвращает помеченный кадр)
            marked_frame = self.fishing.controller(frame)

            # Отправка кадра в превью (не чаще 15 раз в секунду, чтобы не грузить GUI)
            now = time.time()
            if now - last_preview_update > 0.066:
                self._pending_frame = marked_frame
                last_preview_update = now
                # Планируем отрисовку в потоке GUI
                try:
                    self.root.after(0, self._flush_frame_to_gui)
                except Exception:
                    pass

            # Микро-дрожание мыши (анти-AFK)
            if self.config.get("idle_jitter_enabled", True):
                self.input_ctrl.idle_jitter()

            # Контроль FPS бота
            bot_fps = self.config.get("bot_fps", 20)
            time.sleep(1.0 / bot_fps)

    def _flush_frame_to_gui(self):
        """Безопасная отрисовка кадра в потоке GUI."""
        if self._pending_frame is not None and hasattr(self, 'gui'):
            self.gui.send_frame_to_preview(self._pending_frame)
            self._pending_frame = None

    def _on_close(self):
        self.stop_bot()
        self.hotkey.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Andy1App()
    app.run()
