# capture.py - Быстрый захват экрана и мыши
import mss
import cv2
import numpy as np
import pyautogui

class ScreenCapture:
    def __init__(self, window_manager):
        self.wm = window_manager

    def get_frame(self):
        if not self.wm.is_found:
            return None
        with mss.mss() as sct:
            screenshot = sct.grab(self.wm.rect)
            frame = np.array(screenshot)
            return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def get_mouse_rel(self):
        if not self.wm.is_found:
            return None
        try:
            mx, my = pyautogui.position()
            rel_x = mx - self.wm.rect["left"]
            rel_y = my - self.wm.rect["top"]
            if 0 <= rel_x < self.wm.rect["width"] and 0 <= rel_y < self.wm.rect["height"]:
                return (rel_x, rel_y)
            return None
        except Exception:
            return None
