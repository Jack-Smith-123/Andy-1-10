import threading
from collections import deque
from datetime import datetime
from config import load_config, save_config

CATEGORIES = ["Система", "Захват", "Зоны", "Общий"]

class LogManager:
    """Глобальный логгер. Пишет в память независимо от открытых окон."""
    def __init__(self):
        self._lock = threading.Lock()
        cfg = load_config()
        log_cfg = cfg.get("log", {})
        self.enabled = bool(log_cfg.get("enabled", True))
        maxlen = int(log_cfg.get("max_lines", 1000))
        self.logs = {cat: deque(maxlen=maxlen) for cat in CATEGORIES}
        self.counters = {cat: 0 for cat in CATEGORIES}
        self._flag_listeners = []

    def set_enabled(self, value):
        value = bool(value)
        if value == self.enabled:
            return
        self.enabled = value
        cfg = load_config()
        cfg.setdefault("log", {})["enabled"] = value
        save_config(cfg)
        for cb in list(self._flag_listeners):
            try:
                cb(value)
            except Exception:
                pass

    def add_flag_listener(self, cb):
        if cb not in self._flag_listeners:
            self._flag_listeners.append(cb)

    def remove_flag_listener(self, cb):
        if cb in self._flag_listeners:
            self._flag_listeners.remove(cb)

    def log(self, message, category="Система"):
        if not self.enabled:
            return
        entry = f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n"
        with self._lock:
            if category in self.logs:
                self.logs[category].append(entry)
                self.counters[category] += 1
            self.logs["Общий"].append(entry)
            self.counters["Общий"] += 1

    def get_all(self, category):
        with self._lock:
            return list(self.logs.get(category, []))

    def get_counter(self, category):
        with self._lock:
            return self.counters.get(category, 0)

    def clear(self, category):
        with self._lock:
            if category in self.logs:
                self.logs[category].clear()
                self.counters[category] = 0

log_manager = LogManager()
