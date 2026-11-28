"""
Отслеживание и отрисовка курсора мыши на кадре.
🆕 Параметр draw: обновляет last_pos всегда, рисует только если draw=True.
"""
import cv2
import pyautogui


class CursorTracker:
    def __init__(self, input_ctrl):
        self.input_ctrl = input_ctrl
        self.last_pos = None
        self.in_frame = False

    def draw(self, frame, draw=True):
        """Рисует голубой кружок вместо курсора. Возвращает (fx, fy, in_frame)."""
        h, w = frame.shape[:2]
        sx, sy = pyautogui.position()
        fx = sx - self.input_ctrl.offset_x
        fy = sy - self.input_ctrl.offset_y
        self.in_frame = (0 <= fx < w) and (0 <= fy < h)
        self.last_pos = (fx, fy) if self.in_frame else None
        if self.in_frame and draw:
            # Голубой кружок (cyan в BGR = 255, 255, 0)
            cv2.circle(frame, (fx, fy), 10, (255, 255, 0), 2)
            cv2.circle(frame, (fx, fy), 3, (255, 255, 0), -1)
        return fx, fy, self.in_frame
