"""
Отрисовка оверлеев на кадре Andy-1.
"""
import cv2
import numpy as np
import math


class FrameOverlay:
    def __init__(self, config):
        self.config = config

    def render(self, frame, environment_mask=None, zones=None,
               pointer_pos=None, target_mask=None, environment_center=None,
               launch_zone=None, target_loc=None, target_state="not_found"):
        result = frame.copy()
        h, w = frame.shape[:2]
        frame_center = (w // 2, h // 2)

        # 1. Полупрозрачная маска воды (зелёная)
        if environment_mask is not None and self.config.get("show_environment", True):
            r = self.config.get("environment_mask_r", 0)
            g = self.config.get("environment_mask_g", 255)
            b = self.config.get("environment_mask_b", 0)
            overlay = np.zeros_like(result)
            overlay[environment_mask > 0] = [b, g, r]
            result = cv2.addWeighted(result, 0.7, overlay, 0.3, 0)

        # 2. Розовая маска поиска поплавка
        if target_mask is not None and self.config.get("show_bobber_mask", True):
            r = self.config.get("target_mask_r", 255)
            g = self.config.get("target_mask_g", 0)
            b = self.config.get("target_mask_b", 255)
            overlay = np.zeros_like(result)
            overlay[target_mask > 0] = [b, g, r]
            result = cv2.addWeighted(result, 0.85, overlay, 0.15, 0)

        # 3. Жёлтый крест + круг в центре воды
        if environment_center and self.config.get("show_water_cross", True):
            r = self.config.get("water_cross_r", 255)
            g = self.config.get("water_cross_g", 255)
            b = self.config.get("water_cross_b", 0)
            cx, cy = environment_center
            size = 18
            cv2.line(result, (cx - size, cy), (cx + size, cy), (b, g, r), 2)
            cv2.line(result, (cx, cy - size), (cx, cy + size), (b, g, r), 2)
            radius = int(self.config.get("water_click_radius", 50))
            cv2.circle(result, environment_center, radius, (b, g, r), 2)

        # 4. Жёлтая линия от центра окна через курсор до края
        if pointer_pos and self.config.get("show_line", True):
            r = self.config.get("line_mask_r", 255)
            g = self.config.get("line_mask_g", 255)
            b = self.config.get("line_mask_b", 0)
            dx = pointer_pos[0] - frame_center[0]
            dy = pointer_pos[1] - frame_center[1]
            mag = math.hypot(dx, dy)
            if mag > 1:
                ndx, ndy = dx / mag, dy / mag
                t = float("inf")
                if ndx > 0: t = min(t, (w - 1 - frame_center[0]) / ndx)
                elif ndx < 0: t = min(t, -frame_center[0] / ndx)
                if ndy > 0: t = min(t, (h - 1 - frame_center[1]) / ndy)
                elif ndy < 0: t = min(t, -frame_center[1] / ndy)
                ex = int(frame_center[0] + t * ndx)
                ey = int(frame_center[1] + t * ndy)
                cv2.line(result, frame_center, (ex, ey), (b, g, r), 2)
            cv2.drawMarker(result, frame_center, (b, g, r), cv2.MARKER_TILTED_CROSS, 12, 2)

        # 5. Фиолетовые квадраты зон (с индивидуальными размерами)
        if zones and self.config.get("show_zones", True):
            r = self.config.get("zone_mask_r", 127)
            g = self.config.get("zone_mask_g", 0)
            b = self.config.get("zone_mask_b", 127)
            for cx, cy, size in zones:
                half = size // 2
                cv2.rectangle(result, (cx - half, cy - half), (cx + half, cy + half), (b, g, r), 2)

        # 6. Голубой крест на курсоре
        if pointer_pos and self.config.get("show_pointer", True):
            r = self.config.get("pointer_mask_r", 0)
            g = self.config.get("pointer_mask_g", 255)
            b = self.config.get("pointer_mask_b", 255)
            cv2.drawMarker(result, pointer_pos, (b, g, r), cv2.MARKER_CROSS, 24, 2)
            cv2.circle(result, pointer_pos, 14, (b, g, r), 1)

        # 7. Квадратная рамка детекта поплавка (зелёная)
        if target_loc:
            colors = {
                "found": (self.config.get("target_found_r", 0), self.config.get("target_found_g", 255), self.config.get("target_found_b", 0)),
                "checking": (self.config.get("target_checking_r", 0), self.config.get("target_checking_g", 200), self.config.get("target_checking_b", 200)),
                "not_found": (self.config.get("target_not_found_r", 255), self.config.get("target_not_found_g", 0), self.config.get("target_not_found_b", 0)),
            }
            r, g, b = colors.get(target_state, colors["not_found"])
            box = int(self.config.get("target_box_size", 40))
            half = box // 2
            tx, ty = target_loc
            cv2.rectangle(result, (tx - half, ty - half), (tx + half, ty + half), (b, g, r), 2)
            cv2.drawMarker(result, target_loc, (b, g, r), cv2.MARKER_CROSS, 10, 1)

        return result
