"""
Детект поплавка Albion Online.
Поплавок = розово-красный (H150-180) + белая основа рядом.
"""
import cv2
import numpy as np


class TargetAnalyzer:
    def __init__(self, config):
        self.config = config
        self._white_history = []

    def _red_mask(self, hsv):
        """Розово-красный диапазон (H150-180)."""
        return cv2.inRange(hsv, np.array([150, 80, 60]), np.array([180, 255, 255]))

    def _white_mask(self, hsv):
        """Белая часть поплавка."""
        return cv2.inRange(hsv, np.array([0, 0, 160]), np.array([180, 50, 255]))

    def _is_ui_zone(self, cx, cy, w, h):
        """Исключает UI элементы."""
        # Чат (левый нижний)
        if cx < 100 and cy > h - 280:
            return True
        # Мини-карта (правый нижний)
        if cx > w - 220 and cy > h - 220:
            return True
        # Верхняя панель (иконки, здоровье)
        if cy < 60:
            return True
        # Нижняя панель (скиллы)
        if cy > h - 70:
            return True
        # Портрет (левый верхний)
        if cx < 200 and cy < 130:
            return True
        return False

    def detect(self, frame):
        """Ищет поплавок."""
        h, w = frame.shape[:2]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        red_mask = self._red_mask(hsv)
        white_mask = self._white_mask(hsv)

        # Морфология
        kernel = np.ones((2, 2), np.uint8)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        min_area = 5
        max_area = 500
        radius = 30
        min_white = 2

        candidates = []

        for c in contours:
            area = cv2.contourArea(c)
            if not (min_area < area < max_area):
                continue

            M = cv2.moments(c)
            if M["m00"] <= 0:
                continue

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            if self._is_ui_zone(cx, cy, w, h):
                continue

            x1 = max(0, cx - radius)
            y1 = max(0, cy - radius)
            x2 = min(w, cx + radius)
            y2 = min(h, cy + radius)

            white_nearby = cv2.countNonZero(white_mask[y1:y2, x1:x2])
            if white_nearby < min_white:
                continue

            candidates.append((cx, cy, area, white_nearby))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[3], reverse=True)
        best = candidates[0]
        return (best[0], best[1])

    def get_mask(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        red = self._red_mask(hsv)
        white = self._white_mask(hsv)
        return cv2.bitwise_or(red, white)

    def detect_white_part(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        white_mask = self._white_mask(hsv)
        white_count = cv2.countNonZero(white_mask)
        self._white_history.append(white_count)
        if len(self._white_history) > 30:
            self._white_history.pop(0)
        return white_count

    def is_biting(self, current_white_count):
        if len(self._white_history) < 5:
            return False
        avg_white = np.mean(self._white_history[-10:])
        if avg_white < 10:
            return False
        threshold = self.config.get("bobber_bite_white_threshold", 0.3)
        return current_white_count < avg_white * threshold
