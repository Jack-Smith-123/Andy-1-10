"""
Расчёт зон поиска вдоль линии заброса.
Единый источник правды для отрисовки и поиска.
"""
import math


class ZoneCalculator:
    def __init__(self, config):
        self.config = config

    def get_frame_center(self, frame_size):
        w, h = frame_size
        return (w // 2, h // 2)

    def is_zone_active(self, index):
        """Проверяет, включена ли зона index (0-based)."""
        i = index + 1
        return self.config.get(f"zone_{i}_active", True)

    def get_zone_size(self, index):
        """Размер зоны index (0-based). Если индивидуальный включён — берём его."""
        i = index + 1
        if self.config.get(f"zone_{i}_enabled", False):
            return int(self.config.get(f"zone_{i}_size", 100))
        return int(self.config.get("zone_size", 100))

    def calculate_zones_with_sizes(self, pointer_pos, frame_size):
        """
        Возвращает список кортежей (cx, cy, size) — центры и размеры зон.
        Пропускает отключённые зоны (zone_{i}_active = False).
        """
        if not pointer_pos:
            return []
        w, h = frame_size
        center = self.get_frame_center(frame_size)
        dx = pointer_pos[0] - center[0]
        dy = pointer_pos[1] - center[1]
        mag = math.hypot(dx, dy)
        if mag < 1:
            return [(center[0], center[1], self.get_zone_size(0))]
        ndx, ndy = dx / mag, dy / mag

        count = int(self.config.get("zone_count", 5))
        spacing = int(self.config.get("zone_spacing", 80))
        start = int(self.config.get("zone_start_distance", 0))

        zones = []
        for i in range(count):
            # Пропускаем отключённые зоны
            if not self.is_zone_active(i):
                continue

            distance = start + spacing * i
            cx = int(center[0] + ndx * distance)
            cy = int(center[1] + ndy * distance)
            if 0 <= cx < w and 0 <= cy < h:
                zones.append((cx, cy, self.get_zone_size(i)))
        return zones

    # Старые методы для совместимости
    def calculate_areas(self, pointer_pos, frame_size):
        return [(cx, cy) for cx, cy, _ in self.calculate_zones_with_sizes(pointer_pos, frame_size)]

    def get_launch_zone(self, environment_center, frame_size):
        return environment_center
