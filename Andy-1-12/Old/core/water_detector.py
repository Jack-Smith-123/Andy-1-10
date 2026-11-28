"""
Детект воды по всему экрану (исключая UI и центр-персонажа).
Фильтр "синевы" (B > R) для отсечения травы.
Находит самую большую связную область воды и возвращает её центр.
🆕 draw_overlay принимает параметр color для настраиваемого цвета маски.
"""
import cv2
import numpy as np


class WaterDetector:
    def __init__(self, config):
        self.config = config

    def _get_ui_mask(self, h, w):
        """Маска UI-зон (True = игнорировать)."""
        mask = np.zeros((h, w), dtype=bool)
        mask[0:int(h * 0.12), 0:int(w * 0.12)] = True
        mask[0:int(h * 0.15), int(w * 0.75):w] = True
        mask[int(h * 0.82):h, int(w * 0.85):w] = True
        mask[int(h * 0.92):h, :] = True
        mask[int(h * 0.20):int(h * 0.28), int(w * 0.40):int(w * 0.60)] = True
        return mask

    def _get_center_exclusion_mask(self, h, w):
        """Маска центра экрана (зона персонажа)."""
        radius = self.config.get("water_exclude_center_radius", 220)
        yy, xx = np.mgrid[0:h, 0:w]
        cy, cx = h // 2, w // 2
        return ((xx - cx) ** 2 + (yy - cy) ** 2) <= radius ** 2

    def detect(self, frame):
        """
        Анализирует весь экран, исключая UI и центр.
        Находит самую большую связную область воды и возвращает её центр.
        Возвращает (has_water, percent, center, water_mask).
        """
        h, w = frame.shape[:2]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h_min = self.config.get("water_h_min", 95)
        h_max = self.config.get("water_h_max", 135)
        s_min = self.config.get("water_s_min", 30)
        v_min = self.config.get("water_v_min", 30)
        v_max = self.config.get("water_v_max", 220)
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, 255, v_max])
        water_mask = cv2.inRange(hsv, lower, upper)
        # Фильтр "синевы": B - R > threshold
        blue_red_diff = self.config.get("water_blue_red_diff", 20)
        b_channel = frame[:, :, 0].astype(np.int16)
        r_channel = frame[:, :, 2].astype(np.int16)
        blue_mask = (b_channel - r_channel > blue_red_diff).astype(np.uint8) * 255
        water_mask = cv2.bitwise_and(water_mask, blue_mask)
        # Исключаем UI
        ui_mask = self._get_ui_mask(h, w)
        water_mask[ui_mask] = 0
        # Исключаем центр экрана
        center_mask = self._get_center_exclusion_mask(h, w)
        water_mask[center_mask] = 0
        # Считаем процент по валидной области
        valid_mask = ~(ui_mask | center_mask)
        total_valid = int(valid_mask.sum())
        water_pixels = int((water_mask > 0).sum())
        percent = (water_pixels / total_valid * 100) if total_valid > 0 else 0.0
        # Находим самую большую связную область воды
        center = None
        if water_pixels > 0:
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
                water_mask, connectivity=8
            )
            best_area = 0
            best_center = None
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area > best_area:
                    best_area = area
                    best_center = (int(centroids[i][0]), int(centroids[i][1]))
            if best_center:
                center = best_center
        threshold = self.config.get("water_threshold_percent", 8.0)
        return percent > threshold, percent, center, water_mask

    def draw_overlay(self, frame, water_mask, color=None):
        """🆕 Полупрозрачная маска воды с настраиваемым цветом."""
        if water_mask is None or water_mask.size == 0:
            return frame
        if color is None:
            color = [0, 255, 0]  # зелёный по умолчанию
        overlay = frame.copy()
        overlay[water_mask > 0] = color
        cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)
        return frame
