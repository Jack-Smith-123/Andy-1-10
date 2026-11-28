"""
Человеческий контроллер мыши/клавиатуры для Andy-1 (рыбалка).
Плавное движение к цели + клик, режимные паузы в idle_jitter.
"""
import math
import random
import time
import pyautogui

class InputController:
    def __init__(self, config=None):
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01
        self.config = config or {}
        self.offset_x = 0
        self.offset_y = 0
        self.window_w = 1024
        self.window_h = 768

        # Физика движения
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

        # 🆕 Режимное поведение idle_jitter: серии движения + длинные паузы
        self._jitter_active_until = 0.0   # до этого времени — дёргаемся
        self._jitter_pause_until = 0.0    # до этого времени — стоим

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

    # ---------- 🆕 Плавное движение + клик ----------
    def move_to_frame_and_click(self, frame_x, frame_y, miss_chance=0.1, fast=False):
        """
        Плавно ведёт курсор к точке в кадре (физическая траектория) и кликает.
        Не телепортирует!
        """
        sx, sy = self.frame_to_screen(frame_x, frame_y)
        # Человеческий промах по цели
        if random.random() < miss_chance:
            sx += random.randint(-10, 10)
            sy += random.randint(-10, 10)

        self.start_move(sx, sy, miss_chance=0.0, fast=fast)

        # Крутим физический цикл пока не дойдём (таймаут ~3 сек)
        max_steps = 350
        steps = 0
        while self._move_active and steps < max_steps:
            self.move_step()
            time.sleep(0.008)
            steps += 1

        # Если не дошёл за таймаут — мягкая доводка
        if self._move_active:
            pyautogui.moveTo(sx, sy, duration=0.15)
            self._move_active = False

        # Микро-пауза перед кликом (как человек)
        time.sleep(random.uniform(0.06, 0.25))
        pyautogui.click()
        self._total_clicks += 1
        print(f"[INPUT] Плавный клик по ({sx}, {sy}) [кадр: {frame_x}, {frame_y}]")

    # ---------- Физика движения ----------
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

    # ---------- Сырые кнопки ----------
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

    # ---------- 🆕 Режимное дрожание: серии движения + паузы ----------
    def idle_jitter(self):
        """
        Человеческое поведение: курсор не дёргается постоянно.
        Он живёт циклами: серия мелких движений (burst) → длинный покой (pause).
        """
        now = time.time()
        # В паузе — стоим на месте
        if now < self._jitter_pause_until:
            return
        # В серии движений — иногда дёргаем
        if now < self._jitter_active_until:
            if random.random() < 0.5:
                pyautogui.moveRel(random.randint(-3, 3), random.randint(-3, 3))
            return
        # Цикл закончился — выбираем новый режим
        chance = self.config.get("jitter_burst_chance", 0.4)
        if random.random() < chance:
            # начинаем серию движений
            dur = random.uniform(
                self.config.get("jitter_burst_min", 0.5),
                self.config.get("jitter_burst_max", 2.0)
            )
            self._jitter_active_until = now + dur
        else:
            # длинная пауза — стоим
            dur = random.uniform(
                self.config.get("jitter_pause_min", 1.0),
                self.config.get("jitter_pause_max", 5.0)
            )
            self._jitter_pause_until = now + dur

    def cleanup(self):
        """Гарантированно отпустить всё при остановке."""
        self.release_left()
