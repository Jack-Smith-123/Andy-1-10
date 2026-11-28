"""
Анализ окружения (воды).
"""
import cv2
import numpy as np


class EnvironmentAnalyzer:
    """Анализирует кадр на наличие воды."""

    def __init__(self, config):
        self.config = config
        self.environment_center = None
        self._last_check_time = 0

    def analyze(self, frame, current_time):
        check_interval = self.config.get("environment_check_interval", 3.0)
        if current_time - self._last_check_time < check_interval:
            return
        self._last_check_time = current_time

        h_low = self.config.get("environment_h_low", 90)
        h_high = self.config.get("environment_h_high", 140)
        s_low = self.config.get("environment_s_low", 30)
        s_high = self.config.get("environment_s_high", 255)
        v_low = self.config.get("environment_v_low", 30)
        v_high = self.config.get("environment_v_high", 255)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([h_low, s_low, v_low])
        upper = np.array([h_high, s_high, v_high])
        mask = cv2.inRange(hsv, lower, upper)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = self.config.get("environment_min_area", 5000)
        valid = [c for c in contours if cv2.contourArea(c) > min_area]

        if valid:
            largest = max(valid, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M["m00"] > 0:
                self.environment_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

    def get_mask(self, frame):
        h_low = self.config.get("environment_h_low", 90)
        h_high = self.config.get("environment_h_high", 140)
        s_low = self.config.get("environment_s_low", 30)
        s_high = self.config.get("environment_s_high", 255)
        v_low = self.config.get("environment_v_low", 30)
        v_high = self.config.get("environment_v_high", 255)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        return cv2.inRange(hsv, np.array([h_low, s_low, v_low]), np.array([h_high, s_high, v_high]))
