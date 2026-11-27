"""
Отрисовка оверлеев на кадр (зрение бота).
Все цвета берутся из конфига.
"""
import cv2
import numpy as np


class FrameOverlay:
    """Рисует вспомогательную графику на кадре."""

    def __init__(self, config):
        self.config = config

    def _get_color(self, r_key, g_key, b_key, default=(0, 255, 0)):
        """Получает BGR цвет из конфига."""
        r = self.config.get(r_key, default[2])
        g = self.config.get(g_key, default[1])
        b = self.config.get(b_key, default[0])
        return (b, g, r)

    def render(self, frame, water_mask=None, area_centers=None, cursor_pos=None,
               float_mask=None, water_center=None, cast_zone=None,
               bobber_loc=None, bobber_state="checking"):
        """
        Отрисовывает все оверлеи на кадре.
        
        Args:
            frame: исходный кадр (BGR)
            water_mask: маска воды
            area_centers: список центров зон [(cx, cy), ...]
            cursor_pos: позиция курсора (x, y)
            float_mask: маска поплавка
            water_center: центр воды (x, y)
            cast_zone: зона заброса (x, y, w, h)
            bobber_loc: позиция поплавка (x, y) или None
            bobber_state: "found", "checking", "not_found"
        """
        result = frame.copy()
        fh, fw = result.shape[:2]

        # === 1. Маска воды ===
        if self.config.get("show_water", True) and water_mask is not None:
            color = self._get_color("water_mask_r", "water_mask_g", "water_mask_b", (0, 255, 0))
            overlay = result.copy()
            overlay[water_mask > 0] = color
            cv2.addWeighted(overlay, 0.3, result, 0.7, 0, result)

        # === 2. Маска поплавка ===
        if self.config.get("show_bobber_mask", False) and float_mask is not None:
            color = self._get_color("bobber_mask_r", "bobber_mask_g", "bobber_mask_b", (255, 0, 255))
            overlay = result.copy()
            overlay[float_mask > 0] = color
            cv2.addWeighted(overlay, 0.4, result, 0.6, 0, result)

        # === 3. Линия из центра через курсор (рисуем всегда) ===
        cx, cy = fw // 2, fh // 2
        if cursor_pos:
            mx, my = cursor_pos
            
            dx = mx - cx
            dy = my - cy
            length = max(1, (dx**2 + dy**2) ** 0.5)
            nx, ny = dx / length, dy / length
            
            end_x = int(mx + nx * 300)
            end_y = int(my + ny * 300)
            
            line_color = self._get_color("line_mask_r", "line_mask_g", "line_mask_b", (0, 255, 255))
            cv2.line(result, (cx, cy), (end_x, end_y), line_color, 2)

        # === 4. Зоны поиска (квадраты) — рисуем всегда если есть центры ===
        if area_centers:
            zone_color = self._get_color("zone_mask_r", "zone_mask_g", "zone_mask_b", (255, 0, 255))
            
            for i, (sx, sy) in enumerate(area_centers):
                zone_num = i + 1
                enabled_key = f"zone_{zone_num}_enabled"
                size_key = f"zone_{zone_num}_size"
                
                if not self.config.get(enabled_key, True):
                    continue
                
                size = self.config.get(size_key, 60)
                half = size // 2
                
                x1 = max(0, sx - half)
                y1 = max(0, sy - half)
                x2 = min(fw, sx + half)
                y2 = min(fh, sy + half)
                
                cv2.rectangle(result, (x1, y1), (x2, y2), zone_color, 2)

        # === 5. Центр воды (крест + квадрат зоны заброса) ===
        if water_center:
            wx, wy = water_center
            cross_size = 15
            
            cross_color = self._get_color("water_cross_r", "water_cross_g", "water_cross_b", (0, 255, 255))
            
            # Крестик
            cv2.line(result, (wx - cross_size, wy), (wx + cross_size, wy), cross_color, 2)
            cv2.line(result, (wx, wy - cross_size), (wx, wy + cross_size), cross_color, 2)

            # Квадрат зоны заброса
            if cast_zone:
                x, y, w, h = cast_zone
                zone_color = self._get_color("water_zone_r", "water_zone_g", "water_zone_b", (0, 255, 255))
                cv2.rectangle(result, (x, y), (x + w, y + h), zone_color, 2)

        # === 6. Рамка поплавка (в зависимости от состояния) ===
        if bobber_loc:
            bx, by = bobber_loc
            box_size = 30
            
            if bobber_state == "found":
                color = self._get_color("bobber_found_r", "bobber_found_g", "bobber_found_b", (0, 255, 0))
            elif bobber_state == "checking":
                color = self._get_color("bobber_checking_r", "bobber_checking_g", "bobber_checking_b", (0, 200, 200))
            else:
                color = self._get_color("bobber_not_found_r", "bobber_not_found_g", "bobber_not_found_b", (0, 0, 255))
            
            x1 = max(0, bx - box_size)
            y1 = max(0, by - box_size)
            x2 = min(fw, bx + box_size)
            y2 = min(fh, by + box_size)
            cv2.rectangle(result, (x1, y1), (x2, y2), color, 2)

        # === 7. Курсор (круг) ===
        if self.config.get("enable_cursor", True) and self.config.get("show_cursor", True) and cursor_pos:
            mx, my = cursor_pos
            color = self._get_color("cursor_mask_r", "cursor_mask_g", "cursor_mask_b", (255, 200, 0))
            cv2.circle(result, (mx, my), 8, color, -1)
            cv2.circle(result, (mx, my), 8, (255, 255, 255), 1)

        return result