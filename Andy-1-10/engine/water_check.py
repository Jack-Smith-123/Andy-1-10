"""
Анализ воды по HSV и фильтру синевы.
"""
import cv2
import numpy as np


class WaterAnalyzer:
    """Анализирует наличие воды на кадре."""

    def __init__(self, config):
        self.config = config
        self._last_check_time = 0
        self._has_water = False
        self._water_percent = 0.0
        self._water_center = None

    def analyze(self, frame, current_time):
        """Проверяет наличие воды на кадре."""
        if current_time - self._last_check_time < self.config.get("water_check_interval", 2.0):
            return self._has_water

        self._last_check_time = current_time

        h_low = self.config.get("water_h_low", 90)
        h_high = self.config.get("water_h_high", 140)
        s_low = self.config.get("water_s_low", 30)
        s_high = self.config.get("water_s_high", 255)
        v_low = self.config.get("water_v_low", 30)
        v_high = self.config.get("water_v_high", 255)
        min_area = self.config.get("water_min_area", 5000)
        blue_ratio = self.config.get("water_blue_ratio", 1.1)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (h_low, s_low, v_low), (h_high, s_high, v_high))

        # Фильтр синевы
        blue_mask = cv2.inRange(hsv, (100, 50, 50), (140, 255, 255))
        blue_pixels = cv2.countNonZero(blue_mask)
        total_pixels = frame.shape[0] * frame.shape[1]
        blue_percent = (blue_pixels / total_pixels) * 100

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        water_area = sum(cv2.contourArea(c) for c in contours)
        total_area = frame.shape[0] * frame.shape[1]
        self._water_percent = (water_area / total_area) * 100

        self._has_water = water_area > min_area and blue_percent > blue_ratio

        if self._has_water and contours:
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M["m00"] > 0:
                self._water_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        return self._has_water

    def get_mask(self, frame=None):
        """Возвращает маску воды для отрисовки."""
        if frame is None:
            return None
        
        h_low = self.config.get("water_h_low", 90)
        h_high = self.config.get("water_h_high", 140)
        s_low = self.config.get("water_s_low", 30)
        s_high = self.config.get("water_s_high", 255)
        v_low = self.config.get("water_v_low", 30)
        v_high = self.config.get("water_v_high", 255)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        return cv2.inRange(hsv, (h_low, s_low, v_low), (h_high, s_high, v_high))

    @property
    def has_water(self):
        return self._has_water

    @property
    def water_percent(self):
        return self._water_percent

    @property
    def water_center(self):
        return self._water_center
