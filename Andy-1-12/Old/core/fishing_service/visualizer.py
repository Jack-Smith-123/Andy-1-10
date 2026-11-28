"""
Отрисовка визуальных элементов: курсор, вода, зоны поиска, маска поплавка.
🆕 Цвета и видимость берутся из конфига (vis_*_color, vis_*_show).
"""
import cv2


class Visualizer:
    def __init__(self, config, water_detector, cursor_tracker):
        self.config = config
        self.water_detector = water_detector
        self.cursor_tracker = cursor_tracker

    def _parse_color(self, hex_color, default_bgr):
        """#rrggbb -> [b, g, r] для OpenCV."""
        try:
            hex_color = hex_color.lstrip("#")
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return [b, g, r]
        except Exception:
            return default_bgr

    def draw_cursor_and_water(self, frame, has_water, percent, center, water_mask):
        """Рисует курсор, маску воды и зону клика."""
        # Маска воды
        if self.config.get("vis_water_show", True) and water_mask is not None:
            color = self._parse_color(
                self.config.get("vis_water_color", "#00ff00"), [0, 255, 0]
            )
            frame = self.water_detector.draw_overlay(frame, water_mask, color=color)

        # Зона клика (жёлтый квадрат)
        if center:
            cx, cy = center
            click_radius = int(self.config.get("water_click_radius", 40))
            x1 = max(0, cx - click_radius)
            y1 = max(0, cy - click_radius)
            x2 = min(frame.shape[1], cx + click_radius)
            y2 = min(frame.shape[0], cy + click_radius)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.drawMarker(frame, (cx, cy), (0, 255, 255), cv2.MARKER_CROSS, 20, 2)

        # Курсор (рисуем только если включено)
        self.cursor_tracker.draw(
            frame, draw=self.config.get("vis_cursor_show", True)
        )

    def draw_search_zone(self, frame, search_zone):
        """Рисует фиолетовый прямоугольник зоны поиска поплавка."""
        if not self.config.get("vis_zones_show", True):
            return
        if search_zone:
            x1, y1, x2, y2 = search_zone
            color = self._parse_color(
                self.config.get("vis_zones_color", "#b400b4"), [180, 0, 180]
            )
            overlay = frame.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
            cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)

    def draw_state_info(self, frame, last_bobber_loc):
        """Рисует только точку поплавка (без текста)."""
        if not self.config.get("vis_bobber_show", True):
            return
        if last_bobber_loc:
            bx, by = last_bobber_loc
            cv2.circle(frame, (bx, by), 4, (0, 255, 255), -1)

    def draw_bobber_mask(self, frame, bobber_mask):
        """Рисует маску красных пикселей поплавка."""
        if not self.config.get("vis_bobber_show", True):
            return frame
        if bobber_mask is None or bobber_mask.size == 0:
            return frame
        color = self._parse_color(
            self.config.get("vis_bobber_color", "#ff69ff"), [255, 105, 255]
        )
        overlay = frame.copy()
        overlay[bobber_mask > 0] = color
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        return frame
