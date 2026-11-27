"""
Andy — Assistant. Точка входа.
"""
import sys
import os
import signal
import customtkinter as ctk

from tools.config import ConfigMixin
from engine.core import TaskEngine
from system.display import DisplayReader
from system.interact import Interactor
from system.app_find import AppLocator
from system.shortcuts import ShortcutManager
from ui.main_view import MainView
from ui.widgets.fonts import FontManager


class App(ConfigMixin):
    """Главный класс приложения."""

    def __init__(self):
        self.load_config()

        # GUI
        self.root = ctk.CTk()
        self.root.title("Andy")
        self.root.geometry("420x520")
        self.root.resizable(False, False)

        self.font_manager = FontManager(self.config)
        self.active = False

        # Системные модули
        self.display = DisplayReader()
        self.interactor = Interactor()
        self.app_locator = AppLocator()

        # Ищем окно приложения
        if self.app_locator.find_window():
            monitor = self.app_locator.get_monitor()
            if monitor:
                self.display.set_monitor(monitor)
                print(f"✓ Окно найдено: {self.app_locator.get_rect()}")

        # Движок
        self.engine = TaskEngine(
            config=self.config,
            display=self.display,
            interactor=self.interactor,
            app_locator=self.app_locator,
            on_log=self._log,
            on_status=self._status,
            on_frame=self._frame,
        )

        # Горячие клавиши
        self.shortcuts = ShortcutManager(
            on_toggle=self.toggle_task,
        )

        # UI
        self.ui = MainView(self)

    def _log(self, msg, category="Система"):
        """Callback для логов от движка."""
        self.ui.log(msg, category)

    def _status(self, state, active, phase=True):
        """Callback для статуса от движка."""
        self.ui.update_status(state, active, phase)

    def _frame(self, frame):
        """Callback для кадров от движка."""
        self.ui.send_frame_to_video(frame)

    def start_task(self):
        """Запуск задачи."""
        if self.active:
            return
        self.active = True
        self.engine.start()

    def stop_task(self):
        """Остановка задачи."""
        if not self.active:
            return
        self.active = False
        self.engine.stop()

    def toggle_task(self):
        """Toggle задачи (для горячей клавиши)."""
        if self.active:
            self.stop_task()
        else:
            self.start_task()

    def run(self):
        """Запуск приложения."""
        # Запускаем горячие клавиши
        self.shortcuts.start()

        # Запуск GUI
        self.root.mainloop()

        # Очистка при закрытии
        self.stop_task()
        self.shortcuts.stop()
        self.display.close()


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()