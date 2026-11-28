"""
Быстрый и устойчивый захват экрана через mss (X11).
ИСПРАВЛЕНИЕ X11 Protocol Error:
  - Захватываем ВЕСЬ монитор целиком + кропаем регион (обход бага mss с BadMatch)
  - Валидация региона по границам монитора
  - Счётчик ошибок + пересоздание MSS-сессии
  - Fallback на pyautogui.screenshot() если mss совсем не работает
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
    print("[CAP] ⚠ mss не установлен. pip install mss")

import pyautogui


class ScreenCapture:
    def __init__(self, target_fps=20, on_frame_callback=None, on_error_callback=None):
        self._check_display_server()
        self.region = {"left": 0, "top": 0, "width": 1024, "height": 768}
        self.target_fps = max(5, min(60, int(target_fps)))
        self.frame_interval = 1.0 / self.target_fps
        self._latest_frame = None
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        self.on_frame_callback = on_frame_callback
        self.on_error_callback = on_error_callback
        self._frame_count = 0
        self._error_count = 0
        self._max_errors_before_reinit = 5
        self._use_fallback = not HAS_MSS  # если mss нет — сразу fallback
        self._monitor_size = (1920, 1080)

    def _check_display_server(self):
        session = os.environ.get("XDG_SESSION_TYPE", "").lower()
        wayland = os.environ.get("WAYLAND_DISPLAY")
        if session == "wayland" or wayland:
            print("⚠️ Wayland. mss может не работать — включим fallback (pyautogui).")
            self._use_fallback = True
        else:
            print(f"✓ X-сервер подтверждён: {session or 'x11'}")

    def set_region(self, left, top, width, height):
        with self._lock:
            self.region = {
                "left": int(left), "top": int(top),
                "width": int(width), "height": int(height),
            }
        print(f"[CAPTURE] Область: {width}x{height} @ ({left}, {top})")

    def set_target_fps(self, fps):
        self.target_fps = max(5, min(60, int(fps)))
        self.frame_interval = 1.0 / self.target_fps

    def _clamp_region(self, region):
        """Ограничивает регион границами монитора. Возвращает (x1, y1, x2, y2) или None."""
        mon_w, mon_h = self._monitor_size
        x1 = max(0, int(region["left"]))
        y1 = max(0, int(region["top"]))
        x2 = min(mon_w, x1 + int(region["width"]))
        y2 = min(mon_h, y1 + int(region["height"]))
        if x2 - x1 < 10 or y2 - y1 < 10:
            return None
        return x1, y1, x2, y2

    def _capture_once_mss(self, sct):
        """Захват всего монитора + кроп региона. Обходит баг mss BadMatch."""
        shot = sct.grab(self._monitor_rect)
        full = cv2.cvtColor(np.array(shot, dtype=np.uint8), cv2.COLOR_BGRA2BGR)
        with self._lock:
            region = self.region.copy()
        clamped = self._clamp_region(region)
        if clamped is None:
            return None
        x1, y1, x2, y2 = clamped
        # Дополнительно ограничиваем по реальному размеру кадра
        h, w = full.shape[:2]
        x2 = min(x2, w)
        y2 = min(y2, h)
        if x2 <= x1 or y2 <= y1:
            return None
        return full[y1:y2, x1:x2].copy()

    def _capture_once_fallback(self):
        """Fallback через pyautogui.screenshot() (медленнее, но стабильнее)."""
        shot = pyautogui.screenshot()
        full = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
        with self._lock:
            region = self.region.copy()
        clamped = self._clamp_region(region)
        if clamped is None:
            return None
        x1, y1, x2, y2 = clamped
        h, w = full.shape[:2]
        x2 = min(x2, w)
        y2 = min(y2, h)
        if x2 <= x1 or y2 <= y1:
            return None
        return full[y1:y2, x1:x2].copy()

    def _capture_loop(self):
        sct = None
        if not self._use_fallback:
            try:
                sct = mss.MSS()
                monitor = sct.monitors[1]
                self._monitor_rect = monitor
                self._monitor_size = (monitor["width"], monitor["height"])
                print(f"[*] Разрешение монитора: {self._monitor_size[0]}x{self._monitor_size[1]}")
            except Exception as e:
                print(f"[CAP] ⚠ mss не инициализировался ({e}). Fallback.")
                self._use_fallback = True
                sct = None

        while self._running:
            start = time.perf_counter()
            try:
                if self._use_fallback:
                    frame = self._capture_once_fallback()
                else:
                    frame = self._capture_once_mss(sct)

                if frame is not None:
                    with self._lock:
                        self._latest_frame = frame
                    self._frame_count += 1
                    self._error_count = 0
                    if self.on_frame_callback:
                        try:
                            self.on_frame_callback(frame)
                        except Exception as e:
                            print(f"[!] Ошибка callback: {e}")
                else:
                    # Регион невалидный — не считаем ошибкой, просто ждём
                    time.sleep(0.1)
                    continue

            except Exception as e:
                self._error_count += 1
                print(f"[!] Ошибка захвата ({self._error_count}): {e}")
                # При серии ошибок — пересоздаём MSS-сессию
                if self._error_count >= self._max_errors_before_reinit:
                    print("[CAP] 🔄 Пересоздаю MSS-сессию...")
                    try:
                        if sct is not None:
                            sct.close()
                    except Exception:
                        pass
                    try:
                        sct = mss.MSS()
                        monitor = sct.monitors[1]
                        self._monitor_rect = monitor
                        self._monitor_size = (monitor["width"], monitor["height"])
                        self._error_count = 0
                        print("[CAP] ✓ MSS пересоздан")
                    except Exception as e2:
                        print(f"[CAP] ❌ MSS не пересоздаётся: {e2}. Переход на fallback.")
                        self._use_fallback = True
                        self._error_count = 0
                    # Уведомляем внешний код (main.py может переспросить окно)
                    if self.on_error_callback:
                        try:
                            self.on_error_callback()
                        except Exception:
                            pass
                time.sleep(0.1)
                continue

            elapsed = time.perf_counter() - start
            sleep_time = self.frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

        try:
            if sct is not None:
                sct.close()
        except Exception:
            pass

    def start(self):
        if self._running:
            return
        self._running = True
        self._error_count = 0
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        mode = "fallback (pyautogui)" if self._use_fallback else "mss"
        print(f"✓ Захват запущен: {self.target_fps} FPS [{mode}]")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        print("✓ Захват остановлен")

    def get_frame(self):
        with self._lock:
            if self._latest_frame is None:
                return None
            return self._latest_frame.copy()
