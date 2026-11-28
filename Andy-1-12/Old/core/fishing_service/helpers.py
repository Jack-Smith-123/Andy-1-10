"""
Хелперы для FishingService.
Все вспомогательные методы: зоны поиска, отрисовка, поиск поплавка.
"""
import cv2
import numpy as np


class FishingHelpers:
    """Миксин с хелперами для FishingService."""

    def crop_center(self, frame, crop_w=130, crop_h=50):
        """Вырезает центр кадра для мини-игры."""
        h, w, _ = frame.shape
        cx, cy = w // 2, h // 2
        x1 = max(cx - crop_w // 2, 0)
        y1 = max(cy - crop_h // 2, 0)
        x2 = min(cx + crop_w // 2, w)
        y2 = min(cy + crop_h // 2, h)
        return frame[y1:y2, x1:x2]

    def _has_soft_red(self, box):
        """Ослабленная проверка: ловит и красный, и оранжевый (RGB + HSV)."""
        if box is None or box.size == 0:
            return 0
        b, g, r = cv2.split(box)
        red_ok = (r > 100) & (g < 150) & (b < 110)
        hsv = cv2.cvtColor(box, cv2.COLOR_BGR2HSV)
        orange_mask = cv2.inRange(hsv, (0, 80, 80), (25, 255, 255))
        combined = red_ok | (orange_mask > 0)
        return int(np.sum(combined))

    def _compute_cursor_zone(self, frame):
        """Квадрат вокруг курсора (если включено в настройках)."""
        if not self.config.get("bobber_cursor_zone_enabled", True):
            return None
        h, w = frame.shape[:2]
        radius = int(self.config.get("bobber_cursor_zone_radius", 150))
        cursor_pos = self.cursor_tracker.last_pos
        if cursor_pos is None:
            return None
        cx, cy = cursor_pos
        x1 = max(0, cx - radius)
        y1 = max(0, cy - radius)
        x2 = min(w, cx + radius)
        y2 = min(h, cy + radius)
        if x2 - x1 < 10 or y2 - y1 < 10:
            return None
        return (x1, y1, x2, y2)

    def _compute_zones_along_line(self, frame):
        """3 зоны вдоль линии (если включено в настройках)."""
        if not self.config.get("bobber_line_search_enabled", True):
            return []
        h, w = frame.shape[:2]
        pad = int(self.config.get("bobber_line_search_width", 150))
        cx, cy = w // 2, h // 2
        cursor_pos = self.cursor_tracker.last_pos
        if cursor_pos is None:
            return []
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
        zones = []
        for t in (0.33, 0.5, 0.66):
            zx = int(cx + (edge_x - cx) * t)
            zy = int(cy + (edge_y - cy) * t)
            x1 = max(0, zx - pad)
            y1 = max(0, zy - pad)
            x2 = min(w, zx + pad)
            y2 = min(h, zy + pad)
            if x2 - x1 >= 5 and y2 - y1 >= 5:
                zones.append((x1, y1, x2, y2))
        return zones

    def _draw_search_line(self, frame, all_zones, cursor_zone):
        """Рисует зоны и линию."""
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        if self.config.get("vis_zones_show", True):
            zone_color = [180, 0, 180]
            for zx1, zy1, zx2, zy2 in all_zones:
                cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), zone_color, 1)
        if self.config.get("vis_zones_show", True) and cursor_zone is not None:
            zx1, zy1, zx2, zy2 = cursor_zone
            cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (255, 165, 0), 2)
        if self.config.get("vis_line_show", True):
            cursor_pos = self.cursor_tracker.last_pos
            if cursor_pos is not None:
                cur_x, cur_y = cursor_pos
                line_color = [0, 255, 255]
                cv2.line(frame, (cx, cy), (cur_x, cur_y), line_color, 1)
                dx, dy = cur_x - cx, cur_y - cy
                length = max(1, np.sqrt(dx ** 2 + dy ** 2))
                ndx, ndy = dx / length, dy / length
                if abs(ndx) > 1e-6:
                    t_x = (w - cx) / ndx if ndx > 0 else -cx / ndx
                else:
                    t_x = float("inf")
                if abs(ndy) > 1e-6:
                    t_y = (h - cy) / ndy if ndy > 0 else -cy / ndy
                else:
                    t_y = float("inf")
                t = min(t_x, t_y)
                edge_x = int(cx + ndx * t)
                edge_y = int(cy + ndy * t)
                cv2.line(frame, (cur_x, cur_y), (edge_x, edge_y), line_color, 1)
                cv2.circle(frame, (edge_x, edge_y), 4, line_color, -1)

    def _find_bobber_in_zones(self, frame, all_zones, cursor_zone):
        """
        Ищет поплавок с учётом настроек поиска и цветовой валидации.
        """
        threshold = self.config.get("match_threshold", 0.62)
        hh = self.template_matcher.h_water
        ww = self.template_matcher.w_water

        cursor_enabled = self.config.get("bobber_cursor_zone_enabled", True)
        line_enabled = self.config.get("bobber_line_search_enabled", True)
        color_validation = self.config.get("bobber_color_validation_enabled", True)

        best_val = -1.0
        best_loc = (0, 0)
        best_idx = -1
        best_offset = (0, 0)
        best_zone_shape = (1, 1)

        # 1. Поиск в зоне курсора (если включено)
        if cursor_enabled and cursor_zone is not None:
            zx1, zy1, zx2, zy2 = cursor_zone
            zone_crop = frame[zy1:zy2, zx1:zx2]
            if zone_crop.size > 0 and zone_crop.shape[0] >= 5 and zone_crop.shape[1] >= 5:
                gray = cv2.cvtColor(zone_crop, cv2.COLOR_BGR2GRAY)
                max_val, max_loc, idx = self.template_matcher.match_best(
                    gray, self.template_matcher.water_templates
                )
                if color_validation and max_val >= threshold:
                    bx, by = max_loc
                    y1c = max(0, by)
                    y2c = min(zone_crop.shape[0], by + hh)
                    x1c = max(0, bx)
                    x2c = min(zone_crop.shape[1], bx + ww)
                    box = zone_crop[y1c:y2c, x1c:x2c]
                    if self._has_soft_red(box) < 3:
                        max_val = 0.0
                if max_val > best_val:
                    best_val = max_val
                    best_loc = max_loc
                    best_idx = idx
                    best_offset = (zx1, zy1)
                    best_zone_shape = zone_crop.shape[:2]

        # 2. Поиск в зонах линии (если включено)
        if line_enabled and all_zones:
            for zone in all_zones:
                zx1, zy1, zx2, zy2 = zone
                zone_crop = frame[zy1:zy2, zx1:zx2]
                if zone_crop.size == 0 or zone_crop.shape[0] < 5 or zone_crop.shape[1] < 5:
                    continue
                gray = cv2.cvtColor(zone_crop, cv2.COLOR_BGR2GRAY)
                max_val, max_loc, idx = self.template_matcher.match_best(
                    gray, self.template_matcher.water_templates
                )
                if color_validation and max_val >= threshold:
                    bx, by = max_loc
                    y1c = max(0, by)
                    y2c = min(zone_crop.shape[0], by + hh)
                    x1c = max(0, bx)
                    x2c = min(zone_crop.shape[1], bx + ww)
                    box = zone_crop[y1c:y2c, x1c:x2c]
                    if self._has_soft_red(box) < 3:
                        max_val = 0.0
                if max_val > best_val:
                    best_val = max_val
                    best_loc = max_loc
                    best_idx = idx
                    best_offset = (zx1, zy1)
                    best_zone_shape = zone_crop.shape[:2]

        bx, by = best_loc
        self._last_score = best_val
        self._best_template_idx = best_idx

        if best_val >= threshold:
            abs_x = bx + best_offset[0] + ww // 2
            abs_y = by + best_offset[1] + hh // 2
            return True, abs_x, abs_y, best_val, best_offset, bx, by

        # 3. Цветовой fallback (если включено)
        if color_validation:
            color_found, color_x, color_y, color_conf, _ = self.color_detector.detect(
                frame, None
            )
            if color_found:
                if cursor_enabled and cursor_zone is not None:
                    zx1, zy1, zx2, zy2 = cursor_zone
                    if zx1 <= color_x < zx2 and zy1 <= color_y < zy2:
                        best_offset = (zx1, zy1)
                        bx = color_x - best_offset[0]
                        by = color_y - best_offset[1]
                        abs_x = color_x
                        abs_y = color_y
                        return True, abs_x, abs_y, color_conf, best_offset, bx, by
                if line_enabled:
                    for zx1, zy1, zx2, zy2 in all_zones:
                        if zx1 <= color_x < zx2 and zy1 <= color_y < zy2:
                            best_offset = (zx1, zy1)
                            bx = color_x - best_offset[0]
                            by = color_y - best_offset[1]
                            abs_x = color_x
                            abs_y = color_y
                            return True, abs_x, abs_y, color_conf, best_offset, bx, by

        return False, 0, 0, 0.0, (0, 0), 0, 0

    def _check_bobber_present(self, frame):
        """Проверяет наличие поплавка."""
        all_zones = self._compute_zones_along_line(frame)
        cursor_zone = self._compute_cursor_zone(frame)
        found, abs_x, abs_y, score, best_offset, bx, by = self._find_bobber_in_zones(
            frame, all_zones, cursor_zone
        )
        self._draw_search_line(frame, all_zones, cursor_zone)
        hh = self.template_matcher.h_water
        ww = self.template_matcher.w_water
        if found:
            cv2.rectangle(
                frame,
                (bx + best_offset[0], by + best_offset[1]),
                (bx + best_offset[0] + ww, by + best_offset[1] + hh),
                (0, 255, 0), 2
            )
        else:
            cv2.rectangle(
                frame,
                (bx + best_offset[0], by + best_offset[1]),
                (bx + best_offset[0] + ww, by + best_offset[1] + hh),
                (0, 0, 255), 1
            )
        return found, abs_x, abs_y, score
