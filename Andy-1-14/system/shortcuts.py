"""
Управление сочетаниями клавиш.
"""


class ShortcutManager:
    """Регистрирует и обрабатывает сочетания клавиш."""

    def __init__(self, on_toggle=None):
        self.on_toggle = on_toggle
        self._listener = None
        self._hotkeys = {}

    def register(self, key, callback):
        """Регистрирует сочетание клавиш."""
        self._hotkeys[key] = callback

    def start(self):
        """Запускает слушатель горячих клавиш."""
        if self._listener:
            return

        from pynput import keyboard

        # Регистрируем F1 по умолчанию
        if self.on_toggle:
            self._hotkeys[keyboard.Key.f1] = self.on_toggle

        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()
        print("[HOTKEY] Слушатель горячих клавиш запущен")

    def stop(self):
        """Останавливает слушатель."""
        if self._listener:
            self._listener.stop()
            self._listener = None
            print("[HOTKEY] Слушатель остановлен")

    def _on_press(self, key):
        """Обработка нажатия клавиши."""
        if key in self._hotkeys:
            try:
                self._hotkeys[key]()
            except Exception as e:
                print(f"⚠ Ошибка обработки горячей клавиши: {e}")

    def _on_release(self, key):
        """Обработка отпускания клавиши."""
        pass