"""
Поиск по шаблону.
"""
import cv2
import numpy as np


class TemplateLocator:
    """Ищет объекты по шаблону."""

    def __init__(self, config):
        self.config = config

    def find(self, frame, template_path):
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            return None
        threshold = self.config.get("match_threshold", 0.7)
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        return max_loc if max_val >= threshold else None
