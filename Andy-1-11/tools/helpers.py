"""
Вспомогательные функции.
"""


def clamp(value, min_val, max_val):
    """Ограничивает value в диапазоне [min_val, max_val]."""
    return max(min_val, min(max_val, value))


def safe_int(value, default=0):
    """Безопасное приведение к int."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Безопасное приведение к float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def dist(p1, p2):
    """Евклидово расстояние между двумя точками."""
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def in_rect(point, rect):
    """Проверяет, лежит ли точка внутри прямоугольника (x, y, w, h)."""
    x, y = point
    rx, ry, rw, rh = rect
    return rx <= x <= rx + rw and ry <= y <= ry + rh


def center_of(rect):
    """Центр прямоугольника (x, y, w, h) -> (cx, cy)."""
    x, y, w, h = rect
    return (x + w // 2, y + h // 2)