"""
Потоковый захват экрана через mss/pyautogui.
Работает в отдельном потоке, отдаёт последний кадр через get_frame().
"""
import os
import time
import threading
import numpy as np
import cv2

try:
    import mss
    HAS_MSS = True
except ImportError:
    HAS_MSS = False

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False


class DisplayReader:
    """Захватывает кадры экрана в отдельном потоке."""

    def __init__(self, target_fps=20):
        self._check_display_server()
        self.region = {"left": 0, "top": 0, "width": 1024, "height": 768}
        self.target_fps = max(5, min(60, int(target_fps)))
        self.frame_interval = 1.0 / self.target_fps
        self._latest_frame = None
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        self._frame_count = 0
        self._error_count = 0
        self._max_errors_before_fallback = 5
        self._use_fallback = not HAS_MSS
        self._monitor_size = (1920, 1080)
        self._sct = None

    def _check_display_server(self):
        session = os.environ.get("XDG_SESSION_TYPE", "").lower()
        wayland = os.environ.get("WAYLAND_DISPLAY")
        if session == "wayland" or wayland:
            print("[DISPLAY] ⚠ Wayland — включаем fallback")
            self._use_fallback = True
        else:
            print(f"[DISPLAY] ✓ X-сервер: {session or 'x11'}")

    def set_monitor(self, monitor):
        """Устанавливает область захвата."""
        self.region = {
            "left": int(monitor.get("left", 0)),
            "top": int(monitor.get("top", 0)),
            "width": int(monitor.get("width", 1024)),
            "height": int(monitor.get("height", 768)),
        }
        print(f"[DISPLAY] Область захвата: {self.region['width']}x{self.region['height']} @ ({self.region['left']}, {self.region['top']})")

    def start(self):
        """Запускает поток захвата."""
        if self._running:
            return
        self._running = True
        self._error_count = 0
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        mode = "fallback (pyautogui)" if self._use_fallback else "mss"
        print(f"[DISPLAY] ✓ Захват запущен: {self.target_fps} FPS [{mode}]")

    def stop(self):
        """Останавливает поток захвата."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        if self._sct:
            try:
                self._sct.close()
            except Exception:
                pass
        print("[DISPLAY] ✓ Захват остановлен")

    def get_frame(self):
        """Возвращает последний захваченный кадр (копию)."""
        with self._lock:
            if self._latest_frame is None:
                return None
            return self._latest_frame.copy()

    def _capture_loop(self):
        """Основной цикл захвата в отдельном потоке."""
        if not self._use_fallback:
            try:
                self._sct = mss.mss()
                if len(self._sct.monitors) > 1:
                    monitor = self._sct.monitors[1]
                else:
                    monitor = self._sct.monitors[0]
                self._monitor_size = (monitor["width"], monitor["height"])
                self._full_monitor = monitor
                print(f"[DISPLAY] ✓ mss инициализирован. Монитор: {self._monitor_size}")
            except Exception as e:
                print(f"[DISPLAY] ⚠ mss не инициализировался: {e}. Fallback.")
                self._use_fallback = True
                self._sct = None

        while self._running:
            start = time.perf_counter()
            try:
                if self._use_fallback:
                    frame = self._capture_fallback()
                else:
                    frame = self._capture_mss()

                if frame is not None:
                    with self._lock:
                        self._latest_frame = frame
                    self._frame_count += 1
                    self._error_count = 0
                else:
                    time.sleep(0.1)
                    continue
            except Exception as e:
                self._error_count += 1
                if self._error_count >= self._max_errors_before_fallback:
                    print(f"[DISPLAY] 🔄 Переключаюсь на fallback ({e})")
                    self._use_fallback = True
                    self._error_count = 0
                    if self._sct:
                        try:
                            self._sct.close()
                        except Exception:
                            pass
                        self._sct = None
                time.sleep(0.1)
                continue

            elapsed = time.perf_counter() - start
            sleep_time = self.frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _capture_mss(self):
        """Захват через mss: весь монитор + кроп региона."""
        if not self._sct:
            return None

        shot = self._sct.grab(self._full_monitor)
        full = np.array(shot, dtype=np.uint8)
        full = cv2.cvtColor(full, cv2.COLOR_BGRA2BGR)

        left = self.region["left"]
        top = self.region["top"]
        width = self.region["width"]
        height = self.region["height"]

        h, w = full.shape[:2]
        x2 = min(left + width, w)
        y2 = min(top + height, h)

        if x2 <= left or y2 <= top:
            return None

        return full[top:y2, left:x2].copy()

    def _capture_fallback(self):
        """Fallback через pyautogui."""
        if not HAS_PYAUTOGUI:
            return None

        try:
            shot = pyautogui.screenshot()
            full = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)

            left = self.region["left"]
            top = self.region["top"]
            width = self.region["width"]
            height = self.region["height"]

            h, w = full.shape[:2]
            x2 = min(left + width, w)
            y2 = min(top + height, h)

            if x2 <= left or y2 <= top:
                return None

            return full[top:y2, left:x2].copy()
        except Exception as e:
            print(f"[DISPLAY] ⚠ Fallback ошибка: {e}")
            return None

    def close(self):
        self.stop()