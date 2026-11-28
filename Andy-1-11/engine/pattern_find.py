
"""
Поиск паттернов на кадре.
"""
import cv2
import numpy as np
import os


class PatternLocator:
    """Загружает шаблоны и ищет их на кадре."""

    def __init__(self, config, templates_dir="templates"):
        self.config = config
        self.templates_dir = templates_dir
        self.templates = {}
        self._load_templates()

    def _load_templates(self):
        """Загружает все шаблоны из папки templates/."""
        if not os.path.exists(self.templates_dir):
            print(f"⚠ Папка шаблонов не найдена: {self.templates_dir}")
            return

        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".png"):
                name = os.path.splitext(filename)[0]
                path = os.path.join(self.templates_dir, filename)
                template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if template is not None:
                    self.templates[name] = template
                    print(f"✓ Шаблон загружен: {name}")

    def find_best_match(self, frame, threshold=None):
        """Ищет лучшее совпадение среди всех шаблонов."""
        if threshold is None:
            threshold = self.config.get("match_threshold", 0.62)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        best_match = None
        best_score = 0.0
        best_pos = None

        for name, template in self.templates.items():
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > best_score and max_val >= threshold:
                best_score = max_val
                best_match = name
                best_pos = max_loc

        return best_match, best_score, best_pos

    def detect_float(self, frame):
        """Определяет наличие маркера по шаблону."""
        match, score, pos = self.find_best_match(frame)
        if match and "bobber" in match.lower():
            return pos, score
        return None, 0.0