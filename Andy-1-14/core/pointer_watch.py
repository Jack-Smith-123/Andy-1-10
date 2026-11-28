"""
Отслеживание указателя (курсора).
Использует pyautogui.position() как основной метод + HSV fallback.
"""
import cv2
import numpy as np


class PointerMonitor:
    def __init__(self, config):
        self.config = config
        self.offset_x = 0
        self.offset_y = 0
        self._last_pos = None

    def set_offset(self, x, y):
        self.offset_x = x
        self.offset_y = y

    def detect(self, frame):
        # Способ 1: pyautogui.position() (надёжный)
        try:
            import pyautogui
            screen_x, screen_y = pyautogui.position()
            # Переводим в координаты внутри окна
            local_x = screen_x - self.offset_x
            local_y = screen_y - self.offset_y
            h, w = frame.shape[:2]
            if 0 <= local_x < w and 0 <= local_y < h:
                self._last_pos = (local_x, local_y)
                return self._last_pos
        except Exception:
            pass

        # Способ 2: HSV поиск (fallback)
        h_low = self.config.get("pointer_h_low", 90)
        h_high = self.config.get("pointer_h_high", 110)
        s_low = self.config.get("pointer_s_low", 150)
        s_high = self.config.get("pointer_s_high", 255)
        v_low = self.config.get("pointer_v_low", 150)
        v_high = self.config.get("pointer_v_high", 255)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([h_low, s_low, v_low]), np.array([h_high, s_high, v_high]))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M["m00"] > 0:
                return (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        return self._last_pos
