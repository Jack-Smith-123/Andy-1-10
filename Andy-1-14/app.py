"""
Основное приложение Andy-1.
"""
import customtkinter as ctk
from core.runtime import AppCore
from gui.main_panel import MainView
from gui.config_panel import OptionsView
from system.display import DisplayReader
from system.interact import Interactor
from system.shortcuts import ShortcutManager
from system.app_find import AppLocator
from gui.widgets.fonts import FontManager


class ConfigMixin:
    def load_config(self):
        import json, os
        config_path = os.path.join(os.path.dirname(__file__), "settings.dat")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = {}


class App(ConfigMixin):
    def __init__(self):
        self.load_config()
        self.root = ctk.CTk()
        self.root.title("Andy-1")
        # Окно в левом верхнем углу, размер 420x520
        self.root.geometry("420x520+0+0")
        self.root.resizable(False, False)
        self.font_manager = FontManager(self.config)
        self.active = False
        self.display = DisplayReader()
        self.interactor = Interactor()
        self.app_locator = AppLocator()
        if self.app_locator.find_window():
            monitor = self.app_locator.get_monitor()
            if monitor:
                self.display.set_monitor(monitor)
                self.display.set_window_id(self.app_locator.window_id)
                print(f"Окно найдено: {self.app_locator.get_rect()}")
        self.engine = AppCore(
            config=self.config,
            display=self.display,
            interactor=self.interactor,
            app_locator=self.app_locator,
            on_log=self._log,
            on_status=self._status,
            on_frame=self._frame,
        )
        self.shortcuts = ShortcutManager(on_toggle=self.toggle_task)
        self.ui = MainView(self)

    def _log(self, msg, category="Система"):
        self.ui.log(msg, category)

    def _status(self, state, active, phase=True):
        self.ui.update_status(state, active, phase)

    def _frame(self, frame):
        self.ui.send_frame_to_video(frame)

    def start_task(self):
        if self.active: return
        self.active = True
        self.engine.start()

    def stop_task(self):
        if not self.active: return
        self.active = False
        self.engine.stop()

    def toggle_task(self):
        if self.active: self.stop_task()
        else: self.start_task()

    def run(self):
        self.shortcuts.start()
        self.root.mainloop()
        self.stop_task()
        self.shortcuts.stop()
        self.display.close()


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
