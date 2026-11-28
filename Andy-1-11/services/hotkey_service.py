"""
Глобальные горячие клавиши через pynput (без root).
Потокобезопасно, callback запускается в отдельном потоке.
"""
import threading
from pynput import keyboard


class HotkeyService:
    def __init__(self):
        self._listener = None
        self._running = False
        self._callbacks = {}
        self._lock = threading.Lock()

    def register(self, key, callback):
        with self._lock:
            self._callbacks[key.lower()] = callback
            print(f"[HOTKEY] Зарегистрирована: {key.upper()}")

    def start(self):
        if self._running:
            return
        self._running = True
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.daemon = True
        self._listener.start()
        print("✓ Hotkey service запущен")

    def stop(self):
        self._running = False
        if self._listener:
            self._listener.stop()
            self._listener = None
        print("✓ Hotkey service остановлен")

    def _on_press(self, key):
        try:
            if hasattr(key, 'char'):
                key_str = key.char.lower() if key.char else None
            else:
                key_str = key.name.lower() if key.name else None
            if key_str is None:
                return
            with self._lock:
                if key_str in self._callbacks:
                    print(f"[HOTKEY] Нажата: {key_str.upper()}")
                    threading.Thread(
                        target=self._callbacks[key_str], daemon=True
                    ).start()
        except Exception as e:
            print(f"[HOTKEY] Ошибка: {e}")