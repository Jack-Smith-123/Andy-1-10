"""
Захват окна игры через xwd (X Window Dump).
Работает даже если окно перекрыто другими.
"""
import os
import time
import threading
import subprocess
import numpy as np
import cv2


class DisplayReader:
    """Захватывает кадры окна игры через xwd."""

    def __init__(self, target_fps=20):
        self.region = {"left": 0, "top": 0, "width": 1024, "height": 768}
        self.target_fps = max(5, min(60, int(target_fps)))
        self.frame_interval = 1.0 / self.target_fps
        self._latest_frame = None
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        self._frame_count = 0
        self._window_id = None
        self._tmp_path = "/tmp/andy_capture.xwd"

    def set_window_id(self, window_id):
        """Устанавливает ID окна для захвата."""
        self._window_id = window_id
        print(f"[DISPLAY] ID окна: {window_id}")

    def set_monitor(self, monitor):
        """Устанавливает область захвата (для совместимости)."""
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
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        print(f"[DISPLAY] ✓ Захват запущен: {self.target_fps} FPS [xwd]")

    def stop(self):
        """Останавливает поток захвата."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        print("[DISPLAY] ✓ Захват остановлен")

    def get_frame(self):
        """Возвращает последний захваченный кадр."""
        with self._lock:
            if self._latest_frame is None:
                return None
            return self._latest_frame.copy()

    def _capture_loop(self):
        """Основной цикл захвата."""
        while self._running:
            start = time.perf_counter()
            try:
                frame = self._capture_xwd()
                if frame is not None:
                    with self._lock:
                        self._latest_frame = frame
                    self._frame_count += 1
            except Exception as e:
                print(f"[DISPLAY] Ошибка захвата: {e}")

            elapsed = time.perf_counter() - start
            sleep_time = self.frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _capture_xwd(self):
        """Захватывает окно через xwd."""
        if not self._window_id:
            return None

        try:
            # Захватываем окно через xwd
            result = subprocess.run(
                ["xwd", "-id", str(self._window_id), "-out", self._tmp_path],
                check=True,
                capture_output=True,
                timeout=2
            )

            # Конвертируем xwd в png через convert (ImageMagick)
            png_path = self._tmp_path.replace(".xwd", ".png")
            subprocess.run(
                ["convert", self._tmp_path, png_path],
                check=True,
                capture_output=True,
                timeout=2
            )

            # Читаем изображение
            frame = cv2.imread(png_path)
            if frame is None:
                return None

            return frame
        except Exception as e:
            print(f"[DISPLAY] xwd ошибка: {e}")
            return None

    def close(self):
        self.stop()
