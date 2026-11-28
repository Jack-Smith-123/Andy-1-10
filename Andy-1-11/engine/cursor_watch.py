"""
Наблюдение за курсором мыши.
"""
import cv2
import numpy as np


class CursorMonitor:
    """Отслеживает положение курсора на кадре."""

    def __init__(self, config):
        self.config = config
        self.last_pos = None
        self._offset_x = 0
        self._offset_y = 0
        self._mouse = None

    def set_offset(self, x, y):
        """Устанавливает смещение окна захвата."""
        self._offset_x = x
        self._offset_y = y

    def _get_mouse(self):
        """Lazy import мыши."""
        if self._mouse is None:
            from pynput.mouse import Controller
            self._mouse = Controller()
        return self._mouse

    def detect(self, frame):
        """Определяет положение курсора на кадре."""
        try:
            mouse = self._get_mouse()
            global_x, global_y = mouse.position
            
            # Переводим глобальные координаты в локальные координаты кадра
            local_x = global_x - self._offset_x
            local_y = global_y - self._offset_y

            h, w = frame.shape[:2]
            
            # Проверяем, что курсор находится внутри захваченного кадра
            if 0 <= local_x < w and 0 <= local_y < h:
                self.last_pos = (int(local_x), int(local_y))
            else:
                self.last_pos = None
        except Exception as e:
            pass

        return self.last_pos

    def get_position(self):
        """Возвращает последнюю известную позицию курсора."""
        return self.last_pos