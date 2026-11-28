"""
Цветовой детектор поплавка.
🆕 Поддержка HSV с настраиваемыми параметрами (как у воды).
🆕 Галочка bobber_hsv_enabled вкл/выкл HSV детект.
🆕 RGB fallback если HSV отключён.
"""
import cv2
import numpy as np


class ColorBobberDetector:
    def __init__(self, config):
        self.config = config

    def detect(self, frame, water_mask=None):
        """
        Ищет поплавок: HSV (если включён) + RGB fallback.
        Возвращает (found, x, y, confidence, mask).
        """
        h, w = frame.shape[:2]

        # 🆕 HSV детект (если включён)
        hsv_enabled = self.config.get("bobber_hsv_enabled", True)
        if hsv_enabled:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            h_min = self.config.get("bobber_h_min", 0)
            h_max = self.config.get("bobber_h_max", 25)
            s_min = self.config.get("bobber_s_min", 60)
            s_max = self.config.get("bobber_s_max", 255)
            v_min = self.config.get("bobber_v_min", 60)
            v_max = self.config.get("bobber_v_max", 255)

            # Красный в HSV разорван по кругу — два диапазона
            if h_max <= 10:
                # Только нижний диапазон
                lower1 = np.array([h_min, s_min, v_min])
                upper1 = np.array([h_max, s_max, v_max])
                mask1 = cv2.inRange(hsv, lower1, upper1)
                combined_hsv = mask1
            elif h_min >= 170:
                # Только верхний диапазон
                lower2 = np.array([h_min, s_min, v_min])
                upper2 = np.array([h_max, s_max, v_max])
                mask2 = cv2.inRange(hsv, lower2, upper2)
                combined_hsv = mask2
            else:
                # Оба диапазона (красный переходит через 0/180)
                lower1 = np.array([0, s_min, v_min])
                upper1 = np.array([h_max, s_max, v_max])
                lower2 = np.array([170, s_min, v_min])
                upper2 = np.array([180, s_max, v_max])
                mask1 = cv2.inRange(hsv, lower1, upper1)
                mask2 = cv2.inRange(hsv, lower2, upper2)
                combined_hsv = cv2.bitwise_or(mask1, mask2)

            return self._find_best_cluster(combined_hsv, h, w)

        # 🆕 RGB fallback (если HSV отключён)
        b, g, r = cv2.split(frame)
        red_mask = (r > 100) & (g < 150) & (b < 110)
        white_threshold = self.config.get("bobber_white_threshold", 180)
        white_mask = (r > white_threshold) & (g > white_threshold) & (b > white_threshold)
        combined = red_mask | white_mask
        return self._find_best_cluster(combined.astype(np.uint8), h, w)

    def _find_best_cluster(self, mask, h, w):
        """Находит самый большой связный кластер в маске."""
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            mask, connectivity=8
        )
        min_area = 10
        best_area = 0
        best_cx, best_cy = 0, 0
        best_confidence = 0.0

        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area < min_area:
                continue
            if area > best_area:
                best_area = area
                best_cx = int(centroids[i][0])
                best_cy = int(centroids[i][1])
                best_confidence = min(1.0, area / 100.0)

        if best_area >= min_area:
            return True, best_cx, best_cy, best_confidence, mask
        return False, 0, 0, 0.0, mask
