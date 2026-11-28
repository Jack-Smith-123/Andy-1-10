"""
Анализ маркера (поплавка) по цвету.
Ищет красный поплавок с белой частью.
"""
import cv2
import numpy as np


class FloatAnalyzer:
    """Определяет положение маркера на кадре по цвету."""

    def __init__(self, config):
        self.config = config

    def detect(self, frame, search_area=None):
        """
        Ищет поплавок: color + template matching.
        Возвращает (x, y) или None.
        """
        h, w = frame.shape[:2]

        # Метод 1: Color detection (существующий)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        h_min = self.config.get("bobber_h_low", 0)
        h_max = self.config.get("bobber_h_high", 20)
        s_min = self.config.get("bobber_s_low", 100)
        s_max = self.config.get("bobber_s_high", 255)
        v_min = self.config.get("bobber_v_low", 100)
        v_max = self.config.get("bobber_v_high", 255)

        if h_max <= 10:
            lower1 = np.array([h_min, s_min, v_min])
            upper1 = np.array([h_max, s_max, v_max])
            red_mask = cv2.inRange(hsv, lower1, upper1)
        elif h_min >= 170:
            lower2 = np.array([h_min, s_min, v_min])
            upper2 = np.array([h_max, s_max, v_max])
            red_mask = cv2.inRange(hsv, lower2, upper2)
        else:
            lower1 = np.array([0, s_min, v_min])
            upper1 = np.array([h_max, s_max, v_max])
            lower2 = np.array([170, s_min, v_min])
            upper2 = np.array([180, s_max, v_max])
            mask1 = cv2.inRange(hsv, lower1, upper1)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            red_mask = cv2.bitwise_or(mask1, mask2)

        white_mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))
        combined = cv2.bitwise_or(red_mask, white_mask)

        # Метод 2: Template matching (новый)
        template_pos = self._detect_by_template(frame, search_area)
        color_pos = self._find_best_cluster(combined, h, w, search_area)

        # Если оба метода нашли поплавок, выбираем тот что ближе к центру зоны
        if template_pos and color_pos:
            return template_pos  # Template matching точнее
        elif template_pos:
            return template_pos
        else:
            return color_pos

    def _detect_by_template(self, frame, search_area=None):
        """Ищет поплавок по шаблону."""
        import os
        import glob
        
        template_dir = "bobberExamples"
        if not os.path.exists(template_dir):
            return None
        
        template_files = glob.glob(os.path.join(template_dir, "*.png"))
        if not template_files:
            return None
        
        # Берем первые 3 шаблона
        template_files = template_files[:3]
        
        match_threshold = self.config.get("bobber_match_threshold", 0.6)
        
        best_match = None
        best_score = 0
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        for template_path in template_files:
            try:
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                if template is None:
                    continue
                
                # Если есть search_area, вырезаем его
                if search_area:
                    x1, y1, x2, y2 = search_area
                    search_frame = gray_frame[y1:y2, x1:x2]
                    offset_x, offset_y = x1, y1
                else:
                    search_frame = gray_frame
                    offset_x, offset_y = 0, 0
                
                result = cv2.matchTemplate(search_frame, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val > match_threshold and max_val > best_score:
                    best_score = max_val
                    th, tw = template.shape
                    center_x = max_loc[0] + tw // 2 + offset_x
                    center_y = max_loc[1] + th // 2 + offset_y
                    best_match = (center_x, center_y)
            except Exception:
                continue
        
        return best_match

    def detect_white_part(self, frame, search_area=None):
        """
        Детектит белую часть поплавка.
        Возвращает количество белых пикселей (int).
        """
        h, w = frame.shape[:2]

        # Маска белой части (высокая яркость, низкая насыщенность)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        white_mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))

        if search_area:
            x1, y1, x2, y2 = search_area
            full_mask = np.zeros((h, w), dtype=np.uint8)
            full_mask[y1:y2, x1:x2] = white_mask[y1:y2, x1:x2]
            white_mask = full_mask

        # Считаем количество белых пикселей
        white_pixels = cv2.countNonZero(white_mask)

        return white_pixels

    def _find_best_cluster(self, mask, h, w, search_area=None):
        """Находит самый большой связный кластер в маске."""
        if search_area:
            x1, y1, x2, y2 = search_area
            full_mask = np.zeros((h, w), dtype=np.uint8)
            full_mask[y1:y2, x1:x2] = mask[y1:y2, x1:x2]
            mask = full_mask

        # Морфологические операции для улучшения детекта
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            mask, connectivity=8
        )

        min_area = self.config.get("bobber_min_area", 30)
        max_area = self.config.get("bobber_max_area", 3000)

        best_area = 0
        best_cx, best_cy = 0, 0

        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area < min_area or area > max_area:
                continue
            if area > best_area:
                best_area = area
                best_cx = int(centroids[i][0])
                best_cy = int(centroids[i][1])

        if best_area >= min_area:
            return (best_cx, best_cy)
        return None

    def get_mask(self, frame):
        """Возвращает маску маркера для отрисовки."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        h_min = self.config.get("bobber_h_low", 0)
        h_max = self.config.get("bobber_h_high", 20)
        s_min = self.config.get("bobber_s_low", 100)
        s_max = self.config.get("bobber_s_high", 255)
        v_min = self.config.get("bobber_v_low", 100)
        v_max = self.config.get("bobber_v_high", 255)

        if h_max <= 10:
            lower1 = np.array([h_min, s_min, v_min])
            upper1 = np.array([h_max, s_max, v_max])
            return cv2.inRange(hsv, lower1, upper1)
        elif h_min >= 170:
            lower2 = np.array([h_min, s_min, v_min])
            upper2 = np.array([h_max, s_max, v_max])
            return cv2.inRange(hsv, lower2, upper2)
        else:
            lower1 = np.array([0, s_min, v_min])
            upper1 = np.array([h_max, s_max, v_max])
            lower2 = np.array([170, s_min, v_min])
            upper2 = np.array([180, s_max, v_max])
            mask1 = cv2.inRange(hsv, lower1, upper1)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            return cv2.bitwise_or(mask1, mask2)