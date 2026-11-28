"""
Машина состояний рыбалки Andy-1-3.
Мульти-шаблонный матчинг. Поиск в зоне от центра экрана до курсора.
Плавный клик по воде в случайной точке зоны. Режимные паузы мыши.
"""
import cv2
import time
import numpy as np
import os
import glob
from .water_detector import WaterDetector
from .cursor_tracker import CursorTracker

class FishingService:
    def __init__(self, config, input_ctrl, log_callback=None):
        self.config = config
        self.input_ctrl = input_ctrl
        self.log = log_callback or print

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.bobber_water_templates = []
        self.bobber_minigame_templates = []
        self.h_in, self.w_in = 0, 0
        self.h_min, self.w_min = 0, 0

        self._load_templates(base_dir, config)

        self.water_detector = WaterDetector(config)
        self.cursor_tracker = CursorTracker(input_ctrl)

        self.state = "IDLE"
        self.active = False
        self.acting = True
        self.state_enter_time = 0
        self._pending_start = False
        self._has_water = False
        self._water_percent = 0.0
        self._water_center = None
        self._last_water_log = 0
        self._last_water_check_time = 0

        self.last_bobber_y = None
        self.last_bobber_x = None
        self.missing_frames = 0
        self.bobber_was_seen = False
        self.seen_streak = 0

        self.time_in_zone = 0.0
        self.last_seen_time = 0
        self.last_action_time = 0

        self._last_score = 0.0
        self._last_bobber_loc = None
        self._best_template_idx = -1
        self._search_zone = None

    def _load_templates(self, base_dir, config):
        max_templates = config.get("bobber_max_templates", 10)

        water_dir = config.get("bobber_water_dir", "templates/bobber_in_water")
        water_dir_full = os.path.join(base_dir, water_dir)
        if os.path.isdir(water_dir_full):
            files = sorted(glob.glob(os.path.join(water_dir_full, "*.png")))
            for f in files[:max_templates]:
                img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    self.bobber_water_templates.append(img)
                    if self.h_in == 0:
                        self.h_in, self.w_in = img.shape[:2]
            self.log(f"✓ Загружено {len(self.bobber_water_templates)} шаблонов воды из {water_dir}")

        if not self.bobber_water_templates:
            water_path = config.get("bobber_water_path", "templates/bobber_in_water.png")
            water_path_full = os.path.join(base_dir, water_path)
            if not os.path.exists(water_path_full):
                water_path_full = os.path.join(base_dir, "bobberExamples", "bobberExampleInWatter2.png")
            img = cv2.imread(water_path_full, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                self.bobber_water_templates.append(img)
                self.h_in, self.w_in = img.shape[:2]
                self.log("✓ Загружен одиночный шаблон воды (fallback)")

        minigame_dir = config.get("bobber_minigame_dir", "templates/bobber_minigame")
        minigame_dir_full = os.path.join(base_dir, minigame_dir)
        if os.path.isdir(minigame_dir_full):
            files = sorted(glob.glob(os.path.join(minigame_dir_full, "*.png")))
            for f in files[:max_templates]:
                img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    self.bobber_minigame_templates.append(img)
                    if self.h_min == 0:
                        self.h_min, self.w_min = img.shape[:2]
            self.log(f"✓ Загружено {len(self.bobber_minigame_templates)} шаблонов мини-игры")

        if not self.bobber_minigame_templates:
            minigame_path = config.get("bobber_minigame_path", "templates/bobber_minigame.png")
            minigame_path_full = os.path.join(base_dir, minigame_path)
            if not os.path.exists(minigame_path_full):
                minigame_path_full = os.path.join(base_dir, "bobberExamples", "bobberExample2.png")
            img = cv2.imread(minigame_path_full, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                self.bobber_minigame_templates.append(img)
                self.h_min, self.w_min = img.shape[:2]
                self.log("✓ Загружен одиночный шаблон мини-игры (fallback)")

        if not self.bobber_water_templates or not self.bobber_minigame_templates:
            self.log("⚠️ ВНИМАНИЕ: Не найдены картинки поплавка!")

    def _crop_search_zone(self, frame):
        """
        Обрезает кадр до зоны поиска: от центра экрана (персонаж) до курсора + радиус.
        Возвращает (cropped_frame, offset_x, offset_y, zone_rect).
        """
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2  # центр экрана (персонаж)
        
        cursor_pos = self.cursor_tracker.last_pos
        radius = self.config.get("bobber_search_radius", 150)
        
        if cursor_pos is None:
            # Курсор вне кадра — используем только центр
            x1 = max(0, cx - radius)
            y1 = max(0, cy - radius)
            x2 = min(w, cx + radius)
            y2 = min(h, cy + radius)
        else:
            mx, my = cursor_pos
            # Bounding box от центра до курсора + радиус вокруг
            x1 = max(0, min(cx, mx) - radius)
            y1 = max(0, min(cy, my) - radius)
            x2 = min(w, max(cx, mx) + radius)
            y2 = min(h, max(cy, my) + radius)
        
        cropped = frame[y1:y2, x1:x2].copy()
        return cropped, x1, y1, (x1, y1, x2, y2)

    def _match_best(self, gray_frame, templates):
        best_val = -1.0
        best_loc = (0, 0)
        best_idx = -1
        for idx, tmpl in enumerate(templates):
            if tmpl is None:
                continue
            res = cv2.matchTemplate(gray_frame, tmpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > best_val:
                best_val = max_val
                best_loc = max_loc
                best_idx = idx
        return best_val, best_loc, best_idx

    def set_active(self, active):
        self.active = active
        if active and self.state == "IDLE":
            self._pending_start = True
            self.log("🔍 Проверка воды и курсора...")
        elif not active:
            self._set_state("IDLE")
            self._pending_start = False
            self.input_ctrl.release_left()

    def set_acting(self, acting):
        if self.acting == acting:
            return
        self.acting = acting
        if not acting:
            self.input_ctrl.release_left()
            self.log("⏸ Действия приостановлены (режим ожидания)")
        else:
            self.log("▶ Действия возобновлены")
            if self.active and self.state == "IDLE":
                self._pending_start = True

    def _set_state(self, new_state):
        self.state = new_state
        self.state_enter_time = time.time()
        self.log(f"➡️ STATE: {new_state}")
        if new_state == "HOOK":
            self.bobber_was_seen = False
            self.seen_streak = 0
            self.missing_frames = 0
            self.last_bobber_y = None
            self.last_bobber_x = None
        elif new_state == "MINI_GAME":
            self.time_in_zone = 0.0
            self.last_seen_time = time.time()
            self.last_action_time = 0

    def crop_center(self, frame, crop_w=130, crop_h=50):
        h, w, _ = frame.shape
        cx, cy = w // 2, h // 2
        x1 = max(cx - crop_w // 2, 0)
        y1 = max(cy - crop_h // 2, 0)
        x2 = min(cx + crop_w // 2, w)
        y2 = min(cy + crop_h // 2, h)
        return frame[y1:y2, x1:x2]

    def _draw_cursor_and_water(self, frame):
        """Рисует курсор, маску воды и зоны (жёлтый квадрат клика + фиолетовый прямоугольник поиска)."""
        check_interval = self.config.get("water_check_interval", 2.0)
        now = time.time()
        if now - self._last_water_check_time < check_interval:
            has_water = self._has_water
            percent = self._water_percent
            center = self._water_center
            water_mask = None
        else:
            has_water, percent, center, water_mask = self.water_detector.detect(frame)
            self._has_water = has_water
            self._water_percent = percent
            self._water_center = center
            self._last_water_check_time = now

        if water_mask is not None:
            frame = self.water_detector.draw_overlay(frame, water_mask)

        if center:
            cx, cy = center
            # Жёлтый квадрат зоны клика
            click_radius = int(self.config.get("water_click_radius", 40))
            x1 = max(0, cx - click_radius)
            y1 = max(0, cy - click_radius)
            x2 = min(frame.shape[1], cx + click_radius)
            y2 = min(frame.shape[0], cy + click_radius)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.drawMarker(frame, (cx, cy), (0, 255, 255), cv2.MARKER_CROSS, 20, 2)

        self.cursor_tracker.draw(frame)

        # Фиолетовый прямоугольник зоны поиска поплавка
        if self._search_zone:
            x1, y1, x2, y2 = self._search_zone
            overlay = frame.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (180, 0, 180), 2)
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (180, 0, 180), -1)
            cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)

    def _draw_state_info(self, frame):
        if self._last_bobber_loc:
            bx, by = self._last_bobber_loc
            cv2.circle(frame, (bx, by), 4, (0, 255, 255), -1)

    def _state_starting(self, frame):
        if time.time() - self.state_enter_time < 2.0:
            return frame
        self.log("🎣 Забрасываем...")
        duration = np.random.uniform(
            self.config.get("cast_hold_min", 0.4),
            self.config.get("cast_hold_max", 1.2)
        )
        self.input_ctrl.cast_hold(duration)
        time.sleep(2.0)
        self._set_state("HOOK")
        return frame

    def _state_hook(self, frame):
        if time.time() - self.state_enter_time < 1.0:
            return frame
        if not self.bobber_was_seen and (time.time() - self.state_enter_time > 30):
            self.log("⚠️ Поплавок так и не появился за 30 сек. Рестарт.")
            self._set_state("RESTART")
            return frame

        cropped, offset_x, offset_y, zone_rect = self._crop_search_zone(frame)
        self._search_zone = zone_rect

        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        max_val, max_loc, best_idx = self._match_best(gray, self.bobber_water_templates)
        bx, by = max_loc
        self._last_score = max_val
        self._best_template_idx = best_idx
        self._last_bobber_loc = (bx + offset_x + self.w_in // 2, by + offset_y + self.h_in // 2)

        match_threshold = self.config.get("match_threshold", 0.62)
        bite_y_threshold = self.config.get("bite_y_threshold", 7)
        missing_frames_limit = self.config.get("missing_frames_limit", 4)
        min_seen_frames = self.config.get("min_seen_frames", 4)
        max_x_jump = self.config.get("max_x_jump", 80)

        if max_val >= match_threshold:
            color = (0, 255, 0) if self.bobber_was_seen else (0, 200, 200)
            cv2.rectangle(cropped, (bx, by), (bx + self.w_in, by + self.h_in), color, 2)
        else:
            cv2.rectangle(cropped, (bx, by), (bx + self.w_in, by + self.h_in), (0, 0, 255), 1)
        frame[offset_y:offset_y + cropped.shape[0], offset_x:offset_x + cropped.shape[1]] = cropped

        if max_val < match_threshold:
            self.missing_frames += 1
            if self.bobber_was_seen and self.seen_streak >= min_seen_frames and self.missing_frames >= missing_frames_limit:
                self.log(f"🎯 КЛЮЁТ! (Поплавок исчез, score={max_val:.2f}, шаблон #{best_idx+1})")
                self.input_ctrl.quick_tap(0.1)
                self._set_state("MINI_GAME")
            return frame

        self.missing_frames = 0
        self.seen_streak += 1
        if self.seen_streak >= min_seen_frames:
            self.bobber_was_seen = True

        current_bobber_y = by + offset_y + (self.h_in // 2)
        current_bobber_x = bx + offset_x + (self.w_in // 2)

        if self.bobber_was_seen and self.last_bobber_y is not None:
            dy = current_bobber_y - self.last_bobber_y
            dx = abs(current_bobber_x - self.last_bobber_x)
            if dx > max_x_jump:
                self.last_bobber_y = current_bobber_y
                self.last_bobber_x = current_bobber_x
                return frame
            if dy > bite_y_threshold:
                self.log(f"🎯 КЛЮЁТ! (Рывок вниз на {dy}px, score={max_val:.2f}, шаблон #{best_idx+1})")
                self.input_ctrl.quick_tap(0.1)
                self._set_state("MINI_GAME")
                self.last_bobber_y = None
                return frame

        self.last_bobber_y = current_bobber_y
        self.last_bobber_x = current_bobber_x
        return frame

    def _state_mini_game(self, frame):
        cropped = self.crop_center(frame, 130, 50)
        if cropped is None or cropped.size == 0:
            return frame

        zoomed = cv2.resize(cropped, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        gray = cv2.cvtColor(zoomed, cv2.COLOR_BGR2GRAY)
        max_val, max_loc, best_idx = self._match_best(gray, self.bobber_minigame_templates)
        self._last_score = max_val
        self._best_template_idx = best_idx

        minigame_threshold = 0.55
        minigame_pull_x = 120
        minigame_release_x = 168
        minigame_center_min = 135
        minigame_center_max = 155
        now = time.time()

        if max_val < minigame_threshold:
            if (now - self.last_seen_time > 2.0) or (now - self.state_enter_time > 15):
                self.log("⏱️ Мини-игра завершена. Перезапуск.")
                self.input_ctrl.release_left()
                self._set_state("STARTING")
            return frame

        self.last_seen_time = now
        x, y = max_loc
        self._last_bobber_loc = (x // 2 + self.w_min // 2, y // 2 + self.h_min // 2)

        cv2.rectangle(zoomed, (x, y), (x + self.w_min, y + self.h_min), (0, 255, 0), 2)
        cv2.line(zoomed, (minigame_pull_x, 0), (minigame_pull_x, zoomed.shape[0]), (255, 0, 0), 2)
        cv2.line(zoomed, (minigame_release_x, 0), (minigame_release_x, zoomed.shape[0]), (255, 0, 0), 2)
        cv2.line(zoomed, (minigame_center_min, 0), (minigame_center_min, zoomed.shape[0]), (0, 255, 0), 1)
        cv2.line(zoomed, (minigame_center_max, 0), (minigame_center_max, zoomed.shape[0]), (0, 255, 0), 1)

        h_zoom, w_zoom = zoomed.shape[:2]
        insert_y = max(0, frame.shape[0] - h_zoom - 10)
        insert_x = max(0, frame.shape[1] - w_zoom - 10)
        frame[insert_y:insert_y + h_zoom, insert_x:insert_x + w_zoom] = zoomed

        if x <= minigame_pull_x:
            if not self.input_ctrl.is_left_down():
                self.input_ctrl.press_left()
        elif x >= minigame_release_x:
            if self.input_ctrl.is_left_down():
                self.input_ctrl.release_left()
        elif minigame_center_min <= x <= minigame_center_max:
            if self.input_ctrl.is_left_down():
                self.input_ctrl.release_left()

        return frame

    def _state_restart(self, frame):
        if time.time() - self.state_enter_time < 0.5:
            return frame
        self.log("🔄 Отмена и перезапуск...")
        self.input_ctrl.release_left()
        self.input_ctrl.right_click()
        time.sleep(1)
        self._set_state("STARTING")
        return frame

    def controller(self, frame):
        self._draw_cursor_and_water(frame)

        if not self.active:
            self._draw_state_info(frame)
            return frame

        if not self.acting:
            self._draw_state_info(frame)
            return frame

        if self._pending_start:
            if self._has_water and self._water_center:
                # Случайная точка в зоне вокруг центра воды (равномерно по площади)
                click_radius = int(self.config.get("water_click_radius", 40))
                angle = np.random.uniform(0, 2 * np.pi)
                dist = np.sqrt(np.random.uniform(0, 1)) * click_radius
                tx = int(self._water_center[0] + dist * np.cos(angle))
                ty = int(self._water_center[1] + dist * np.sin(angle))
                self.log(f"🖱️ Плавный клик по воде: ({tx}, {ty}) [зона ±{click_radius}px]")
                # Плавное движение + клик (не телепорт!)
                self.input_ctrl.move_to_frame_and_click(tx, ty)
                time.sleep(1.5)
                self._pending_start = False
                self._set_state("STARTING")
            elif self._has_water:
                self._pending_start = False
                self._set_state("STARTING")
            else:
                if time.time() - self._last_water_log > 5.0:
                    self.log(f"❌ Вода не найдена ({self._water_percent:.1f}%). "
                             f"Нужно >{self.config.get('water_threshold_percent', 8.0):.0f}%.")
                    if self._water_center:
                        self.log(f"   Ближайший центр воды: {self._water_center}")
                    self._last_water_log = time.time()
            return frame

        if self.state == "STARTING":
            frame = self._state_starting(frame)
        elif self.state == "HOOK":
            frame = self._state_hook(frame)
        elif self.state == "MINI_GAME":
            frame = self._state_mini_game(frame)
        elif self.state == "RESTART":
            frame = self._state_restart(frame)

        self._draw_state_info(frame)
        return frame
