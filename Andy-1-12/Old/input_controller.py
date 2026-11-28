"""
Человеческий контроллер мыши/клавиатуры для Andy-1 (рыбалка).
Перенос физики движения из Andy-2 + специфичные действия рыбалки:
заброс, подсечка, удержание в мини-игре, отмена (ПКМ), микро-дрожание.
"""
import math
import random
import time
import pyautogui


class InputController:
    def __init__(self):
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01
        self.offset_x = 0
        self.offset_y = 0
        self.window_w = 1024
        self.window_h = 768

        # Физика движения (из Andy-2)
        self._move_active = False
        self._move_dest_x = 0
        self._move_dest_y = 0
        self._move_vx = 0.0
        self._move_vy = 0.0
        self._move_gravity = 4.0
        self._move_wind = 15.0
        self._move_max_step = 24
        self._move_friction = 0.82
        self._move_fast = False

        self._left_down = False
        self._total_clicks = 0
        self._missed_clicks = 0

    # ---------- Координаты ----------
    def set_window(self, geometry):
        self.offset_x = geometry["left"]
        self.offset_y = geometry["top"]
        self.window_w = geometry["width"]
        self.window_h = geometry["height"]
        print(f"[INPUT] Окно: offset=({self.offset_x},{self.offset_y}) "
              f"{self.window_w}x{self.window_h}")

    def frame_to_screen(self, target_x, target_y):
        sx = self.offset_x + int(target_x)
        sy = self.offset_y + int(target_y)
        sw, sh = pyautogui.size()
        return max(0, min(sx, sw - 1)), max(0, min(sy, sh - 1))

    def screen_to_frame(self, screen_x, screen_y):
        return screen_x - self.offset_x, screen_y - self.offset_y

    def get_cursor(self):
        return pyautogui.position()

    # ---------- Физика движения (из Andy-2) ----------
    def start_move(self, dest_x, dest_y, miss_chance=0.15, fast=False):
        if random.random() < miss_chance:
            dest_x += random.randint(-12, 12)
            dest_y += random.randint(-12, 12)
        self._move_dest_x = dest_x
        self._move_dest_y = dest_y
        self._move_vx = 0.0
        self._move_vy = 0.0
        self._move_fast = fast
        if fast:
            self._move_gravity = random.uniform(16, 24)
            self._move_wind = random.uniform(2, 5)
            self._move_max_step = random.randint(90, 140)
            self._move_friction = random.uniform(0.66, 0.74)
        else:
            self._move_gravity = random.uniform(3, 5)
            self._move_wind = random.uniform(12, 18)
            self._move_max_step = random.randint(20, 28)
            self._move_friction = random.uniform(0.78, 0.86)
        self._move_active = True

    def move_step(self):
        if not self._move_active:
            return True
        cur_x, cur_y = pyautogui.position()
        dx = self._move_dest_x - cur_x
        dy = self._move_dest_y - cur_y
        dist = math.hypot(dx, dy)
        finish_dist = 4 if self._move_fast else 6
        if dist < finish_dist:
            self._move_active = False
            return True
        nx, ny = dx / dist, dy / dist
        px, py = -ny, nx
        self._move_vx += px * random.uniform(-self._move_wind, self._move_wind) * 0.12
        self._move_vy += py * random.uniform(-self._move_wind, self._move_wind) * 0.12
        self._move_vx += nx * self._move_gravity
        self._move_vy += ny * self._move_gravity
        self._move_vx *= self._move_friction
        self._move_vy *= self._move_friction
        speed = math.hypot(self._move_vx, self._move_vy)
        if speed > self._move_max_step:
            self._move_vx = self._move_vx / speed * self._move_max_step
            self._move_vy = self._move_vy / speed * self._move_max_step
        mx, my = int(round(self._move_vx)), int(round(self._move_vy))
        if mx != 0 or my != 0:
            pyautogui.move(mx, my)
        return False

    def is_moving(self):
        return self._move_active

    # ---------- Сырые кнопки (для мини-игры) ----------
    def press_left(self):
        if not self._left_down:
            pyautogui.mouseDown(button='left')
            self._left_down = True

    def release_left(self):
        if self._left_down:
            pyautogui.mouseUp(button='left')
            self._left_down = False

    def is_left_down(self):
        return self._left_down

    # ---------- Специфика рыбалки ----------
    def cast_hold(self, duration):
        """Заброс: зажать ЛКМ на duration секунд с человеческим джиттером."""
        self._total_clicks += 1
        time.sleep(random.uniform(0.15, 0.5))
        self.press_left()
        # Микро-дрожание во время удержания
        steps = max(1, int(duration / 0.1))
        for _ in range(steps):
            time.sleep(random.uniform(0.08, 0.12))
            pyautogui.moveRel(random.randint(-2, 2), random.randint(-2, 2))
        self.release_left()

    def quick_tap(self, duration=0.1):
        """Подсечка: быстрый зажать-отпустить."""
        self._total_clicks += 1
        self.press_left()
        time.sleep(duration + random.uniform(-0.02, 0.05))
        self.release_left()

    def right_click(self):
        """Отмена / рестарт (ПКМ)."""
        pyautogui.click(button='right')

    def react_and_click(self, button='left', miss_chance=0.08):
        """Человеческий клик с шансом промаха (из Andy-2)."""
        self._total_clicks += 1
        time.sleep(random.uniform(0.15, 1.2))
        if random.random() < miss_chance:
            self._missed_clicks += 1
            pyautogui.moveRel(random.randint(-40, 40), random.randint(-25, 25))
            time.sleep(random.uniform(0.25, 0.6))
            pyautogui.click(button=button)
            time.sleep(random.uniform(0.3, 0.7))
            pyautogui.moveRel(random.randint(-35, 35), random.randint(-20, 20))
            time.sleep(random.uniform(0.15, 0.4))
            pyautogui.click(button=button)
            return "miss_then_hit"
        pyautogui.moveRel(random.randint(-3, 3), random.randint(-3, 3))
        time.sleep(random.uniform(0.04, 0.12))
        pyautogui.click(button=button)
        return "hit"

    def idle_jitter(self):
        """Микро-дрожание мыши в ожидании (анти-детект бездействия)."""
        if random.random() < 0.3:
            pyautogui.moveRel(random.randint(-3, 3), random.randint(-3, 3))
            time.sleep(random.uniform(0.05, 0.15))

    def cleanup(self):
        """Гарантированно отпустить всё при остановке."""
        self.release_left()