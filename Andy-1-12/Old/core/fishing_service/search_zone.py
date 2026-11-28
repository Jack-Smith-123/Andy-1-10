"""
Зона поиска поплавка.
🆕 Основной режим: прямая линия от центра экрана через курсор до края.
🆕 Вдоль линии размещается 3 зоны (t=0.33, 0.5, 0.66).
🆕 1-я (у персонажа) и 5-я (у края) убраны.
🆕 Возвращает список зон + зону курсора.
"""
import cv2
import numpy as np


class SearchZone:
    def __init__(self, config, cursor_tracker):
        self.config = config
        self.cursor_tracker = cursor_tracker

    def crop_search_zone(self, frame, water_mask=None, direction=None):
        """
        🆕 Возвращает (cropped, offset_x, offset_y, zone_rect, all_zones, cursor_zone).
        all_zones — список из 3 зон [(x1,y1,x2,y2), ...] вдоль линии.
        cursor_zone — квадрат 300x300 вокруг курсора (или None).
        """
        h, w = frame.shape[:2]
        pad = int(self.config.get("bobber_search_width", 150))
        cx, cy = w // 2, h // 2

        # 🆕 Зона курсора (300x300)
        cursor_zone = None
        cursor_pos = self.cursor_tracker.last_pos
        if cursor_pos is not None:
            cur_x, cur_y = cursor_pos
            half = 150
            x1 = max(0, cur_x - half)
            y1 = max(0, cur_y - half)
            x2 = min(w, cur_x + half)
            y2 = min(h, cur_y + half)
            if x2 - x1 >= 10 and y2 - y1 >= 10:
                cursor_zone = (x1, y1, x2, y2)

        # 🆕 3 зоны вдоль линии от центра через курсор до края
        zones = []
        if cursor_pos is not None:
            cur_x, cur_y = cursor_pos
            dx = cur_x - cx
            dy = cur_y - cy
            length = max(1.0, np.sqrt(dx ** 2 + dy ** 2))
            ndx, ndy = dx / length, dy / length

            if abs(ndx) > 1e-6:
                t_x = (w - cx) / ndx if ndx > 0 else -cx / ndx
            else:
                t_x = float("inf")
            if abs(ndy) > 1e-6:
                t_y = (h - cy) / ndy if ndy > 0 else -cy / ndy
            else:
                t_y = float("inf")
            t_edge = min(t_x, t_y)
            edge_x = int(cx + ndx * t_edge)
            edge_y = int(cy + ndy * t_edge)
            edge_x = max(0, min(w - 1, edge_x))
            edge_y = max(0, min(h - 1, edge_y))

            for t in (0.33, 0.5, 0.66):
                zx = int(cx + (edge_x - cx) * t)
                zy = int(cy + (edge_y - cy) * t)
                x1 = max(0, zx - pad)
                y1 = max(0, zy - pad)
                x2 = min(w, zx + pad)
                y2 = min(h, zy + pad)
                if x2 - x1 >= 5 and y2 - y1 >= 5:
                    zones.append((x1, y1, x2, y2))

        if zones:
            x1, y1, x2, y2 = zones[0]
            cropped = frame[y1:y2, x1:x2].copy()
            return cropped, x1, y1, (x1, y1, x2, y2), zones, cursor_zone

        # Fallback: квадрат вокруг центра
        half = pad
        x1 = max(0, cx - half)
        y1 = max(0, cy - half)
        x2 = min(w, cx + half)
        y2 = min(h, cy + half)
        cropped = frame[y1:y2, x1:x2].copy()
        return cropped, x1, y1, (x1, y1, x2, y2), [(x1, y1, x2, y2)], cursor_zone
