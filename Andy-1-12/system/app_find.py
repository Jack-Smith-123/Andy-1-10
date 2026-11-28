"""
Поиск окна приложения.
"""
import subprocess


class AppLocator:
    """Находит окно приложения и получает его параметры."""

    def __init__(self, window_title="Albion Online Client"):
        self.window_title = window_title
        self._window_id = None
        self._rect = None

    def find_window(self):
        """Ищет окно приложения через xdotool с fallback на wmctrl."""
        # Способ 1: xdotool
        try:
            result = subprocess.run(
                ["xdotool", "search", "--name", self.window_title],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                self._window_id = result.stdout.strip().split("\n")[0]
                print(f"[APP] ✓ Окно найдено через xdotool: '{self.window_title}' (ID={self._window_id})")
                self._update_rect()
                if self._rect:
                    return True
        except Exception as e:
            print(f"[APP] ⚠ xdotool не сработал: {e}")

        # Способ 2: wmctrl (fallback)
        try:
            result = subprocess.run(
                ["wmctrl", "-l"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if self.window_title in line:
                        self._window_id = line.split()[0]
                        print(f"[APP] ✓ Окно найдено через wmctrl: '{self.window_title}' (ID={self._window_id})")
                        self._update_rect()
                        if self._rect:
                            return True
        except Exception as e:
            print(f"[APP] ⚠ wmctrl не сработал: {e}")

        print(f"[APP] ✗ Окно '{self.window_title}' не найдено")
        return False

    def _update_rect(self):
        """Обновляет координаты окна через xdotool."""
        if not self._window_id:
            return

        try:
            result = subprocess.run(
                ["xdotool", "getwindowgeometry", "--shell", self._window_id],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                print(f"[APP] Геометрия окна: {result.stdout.strip()}")
                lines = result.stdout.strip().split("\n")
                rect = {}
                for line in lines:
                    if "=" in line:
                        key, value = line.split("=", 1)
                        # Ключи приходят в ВЕРХНЕМ регистре: X, Y, WIDTH, HEIGHT
                        rect[key.upper()] = int(value)

                x = rect.get("X", 0)
                y = rect.get("Y", 0)
                w = rect.get("WIDTH", 0)
                h = rect.get("HEIGHT", 0)
                self._rect = (x, y, w, h)
                print(f"[APP] Прямоугольник окна: {self._rect}")
        except Exception as e:
            print(f"[APP] ⚠ Ошибка получения геометрии: {e}")

    def get_rect(self):
        """Возвращает координаты окна (x, y, width, height)."""
        if not self._rect:
            self._update_rect()
        return self._rect

    def get_monitor(self):
        """Возвращает словарь monitor для mss."""
        rect = self.get_rect()
        if rect:
            x, y, w, h = rect
            return {
                "left": x,
                "top": y,
                "width": w,
                "height": h,
            }
        return None

    @property
    def window_id(self):
        return self._window_id