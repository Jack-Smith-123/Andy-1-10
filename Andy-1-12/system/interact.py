"""
Управление мышью и клавиатурой.
"""
import time


class Interactor:
    """Управляет мышью и клавиатурой."""

    def __init__(self):
        self._mouse = None
        self._keyboard = None

    def _get_mouse(self):
        """Lazy import мыши."""
        if self._mouse is None:
            from pynput.mouse import Controller as MouseController
            self._mouse = MouseController()
        return self._mouse

    def _get_keyboard(self):
        """Lazy import клавиатуры."""
        if self._keyboard is None:
            from pynput.keyboard import Controller as KeyboardController
            self._keyboard = KeyboardController()
        return self._keyboard

    def click(self, x=None, y=None, button="left"):
        """Клик мышью."""
        mouse = self._get_mouse()
        if x is not None and y is not None:
            mouse.position = (x, y)
            time.sleep(0.05)

        from pynput.mouse import Button
        btn = Button.left if button == "left" else Button.right
        mouse.click(btn, 1)

    def press(self, key):
        """Нажатие клавиши."""
        keyboard = self._get_keyboard()
        if len(key) == 1:
            keyboard.press(key)
            keyboard.release(key)
        else:
            from pynput.keyboard import Key
            special_keys = {
                "enter": Key.enter,
                "space": Key.space,
                "esc": Key.esc,
                "tab": Key.tab,
            }
            k = special_keys.get(key.lower(), key)
            keyboard.press(k)
            keyboard.release(k)

    def move_to(self, x, y):
        """Перемещение мыши."""
        self._get_mouse().position = (x, y)

    def scroll(self, amount):
        """Прокрутка колеса мыши."""
        self._get_mouse().scroll(0, amount)

    def press_left(self):
        """Зажать ЛКМ."""
        from pynput.mouse import Button
        self._get_mouse().press(Button.left)

    def release_left(self):
        """Отпустить ЛКМ."""
        from pynput.mouse import Button
        self._get_mouse().release(Button.left)

    def quick_tap(self, duration=0.1):
        """Быстрый зажать-отпустить (подсечка)."""
        self.press_left()
        time.sleep(duration)
        self.release_left()

    def right_click(self):
        """Клик правой кнопкой мыши (для заброса удочки в Albion)."""
        from pynput.mouse import Button
        self._get_mouse().click(Button.right, 1)

    def press_right(self):
        """Зажать ПКМ."""
        from pynput.mouse import Button
        self._get_mouse().press(Button.right)

    def release_right(self):
        """Отпустить ПКМ."""
        from pynput.mouse import Button
        self._get_mouse().release(Button.right)