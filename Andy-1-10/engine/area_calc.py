"""
Расчёт зон анализа на кадре.
5 квадратов: 1-й в центре экрана, остальные 4 вдоль линии.
"""


class AreaCalculator:
    """Вычисляет 5 зон для поиска маркера."""

    def __init__(self, config):
        self.config = config

    def calculate_areas(self, cursor_pos, frame_size):
        """
        Рассчитывает 5 зон.
        Квадрат 1: центр в центре экрана.
        Квадраты 2-5: линия от центра до края делится на 5 частей, центры частей = центры квадратов.
        Возвращает список из 5 кортежей (cx, cy) — центров квадратов.
        """
        if not cursor_pos:
            return []

        fw, fh = frame_size
        cx, cy = fw // 2, fh // 2  # Центр экрана
        mx, my = cursor_pos  # Позиция курсора

        # Вектор от центра к курсору
        dx = mx - cx
        dy = my - cy
        length = max(1, (dx**2 + dy**2) ** 0.5)

        # Нормализованный вектор
        nx = dx / length
        ny = dy / length

        # Находим край экрана по направлению вектора
        if abs(nx) > 1e-6:
            t_x = (fw - cx) / nx if nx > 0 else -cx / nx
        else:
            t_x = float('inf')
        
        if abs(ny) > 1e-6:
            t_y = (fh - cy) / ny if ny > 0 else -cy / ny
        else:
            t_y = float('inf')
        
        t_edge = min(t_x, t_y)
        edge_x = int(cx + nx * t_edge)
        edge_y = int(cy + ny * t_edge)

        # Длина линии от центра до края
        line_length = ((edge_x - cx)**2 + (edge_y - cy)**2) ** 0.5

        centers = []
        
        # Квадрат 1: центр экрана
        centers.append((cx, cy))
        
        # Квадраты 2-5: линия делится на 5 равных частей, центры частей
        # Часть 1: 0 - 1/5 → центр в 1/10
        # Часть 2: 1/5 - 2/5 → центр в 3/10
        # Часть 3: 2/5 - 3/5 → центр в 5/10
        # Часть 4: 3/5 - 4/5 → центр в 7/10
        fractions = [0.1, 0.3, 0.5, 0.7]
        
        for frac in fractions:
            sx = int(cx + nx * line_length * frac)
            sy = int(cy + ny * line_length * frac)
            centers.append((sx, sy))

        return centers

    def get_cast_zone(self, water_center, frame_size):
        """
        Возвращает зону заброса вокруг центра воды.
        """
        if not water_center:
            return None

        fw, fh = frame_size
        wx, wy = water_center
        zone_size = 200  # Размер зоны заброса

        x = max(0, wx - zone_size // 2)
        y = max(0, wy - zone_size // 2)
        w = min(zone_size, fw - x)
        h = min(zone_size, fh - y)

        return (x, y, w, h)