"""
Ядро рыбалки Andy-1-3 (улучшенный).
Детект воды по всему экрану (исключая UI и центр-персонажа).
Фильтр "синевы" (B > R) для отсечения травы.
Настраиваемые параметры через config.
"""
import cv2
import time
import numpy as np
import os
import pyautogui

class FishingService:
    def __init__(self, config, input_ctrl, log_callback=None):
        self.config = config
        self.input_ctrl = input_ctrl
        self.log = log_callback or print

        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        water_path = os.path.join(base_dir, config.get("bobber_water_path", "templates/bobber_in_water.png"))
        if not os.path.exists(water_path):
            water_path = os.path.join(base_dir, "bobberExamples", "bobberExampleInWatter2.png")
            
        minigame_path = os.path.join(base_dir, config.get("bobber_minigame_path", "templates/bobber_minigame.png"))
        if not os.path.exists(minigame_path):
            minigame_path = os.path.join(base_dir, "bobberExamples", "bobberExample2.png")

        self.bobber_in_water = cv2.imread(water_path, cv2.IMREAD_GRAYSCALE)
        self.bobber_minigame = cv2.imread(minigame_path, cv2.IMREAD_GRAYSCALE)

        if self.bobber_in_water is None or self.bobber_minigame is None:
            print("⚠️ ВНИМАНИЕ: Не найдены картинки поплавка!")
        else:
            self.h_in, self.w_in = self.bobber_in_water.shape[:2]
            self.h_min, self.w_min = self.bobber_minigame.shape[:2]
            self.log("✓ Шаблоны поплавка загружены")

        self.state = "IDLE"
        self.active = False
        self.state_enter_time = 0
        self._pending_start = False
        self._has_water = False
        self._water_percent = 0.0
        self._water_center = None
        self._last_water_log = 0
        self._last_water_check_time = 0  # 🆕 Для таймера проверки

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

    def set_active(self, active):
        self.active = active
        if active and self.state == "IDLE":
            self._pending_start = True
            self.log("🔍 Проверка воды и курсора...")
        elif not active:
            self._set_state("IDLE")
            self._pending_start = False
            self.input_ctrl.release_left()

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

    # === 🆕 ДЕТЕКТ ВОДЫ (ИСПРАВЛЕННЫЙ) ===
    def _get_ui_mask(self, h, w):
        """Маска UI-зон (True = игнорировать)."""
        mask = np.zeros((h, w), dtype=bool)
        # Левый верх: портрет
        mask[0:int(h*0.12), 0:int(w*0.12)] = True
        # Правый верх: иконки/квесты
        mask[0:int(h*0.15), int(w*0.75):w] = True
        # Правый нижний: миникарта
        mask[int(h*0.82):h, int(w*0.85):w] = True
        # Самый низ: панель скиллов
        mask[int(h*0.92):h, :] = True
        # Центр-верх: полоска HP/маны
        mask[int(h*0.20):int(h*0.28), int(w*0.40):int(w*0.60)] = True
        return mask

    def _get_center_exclusion_mask(self, h, w):
        """🆕 Маска центра экрана (зона персонажа) — исключается из анализа воды."""
        radius = self.config.get("water_exclude_center_radius", 150)
        yy, xx = np.mgrid[0:h, 0:w]
        cy, cx = h // 2, w // 2
        return ((xx - cx) ** 2 + (yy - cy) ** 2) <= radius ** 2

    def _check_water_fullscreen(self, frame):
        """
        Анализирует весь экран, исключая UI и центр.
        Фильтр "синевы" (B > R) для отсечения травы.
        Возвращает (has_water, percent, center, water_mask).
        """
        h, w = frame.shape[:2]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 🆕 Только синий/бирюзовый диапазон (убран "фиолетовый", который захватывал траву)
        h_min = self.config.get("water_h_min", 95)
        h_max = self.config.get("water_h_max", 135)
        s_min = self.config.get("water_s_min", 30)
        v_min = self.config.get("water_v_min", 30)
        v_max = self.config.get("water_v_max", 220)
        
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, 255, v_max])
        water_mask = cv2.inRange(hsv, lower, upper)
        
        # 🆕 Фильтр "синевы": B - R > threshold (вода синяя, трава — нет)
        blue_red_diff = self.config.get("water_blue_red_diff", 20)
        b_channel = frame[:, :, 0].astype(np.int16)
        r_channel = frame[:, :, 2].astype(np.int16)
        blue_mask = (b_channel - r_channel > blue_red_diff).astype(np.uint8) * 255
        water_mask = cv2.bitwise_and(water_mask, blue_mask)
        
        # Исключаем UI
        ui_mask = self._get_ui_mask(h, w)
        water_mask[ui_mask] = 0
        
        # 🆕 Исключаем центр экрана (зону персонажа)
        center_mask = self._get_center_exclusion_mask(h, w)
        water_mask[center_mask] = 0
        
        # Считаем процент по валидной области
        valid_mask = ~(ui_mask | center_mask)
        total_valid = int(valid_mask.sum())
        water_pixels = int((water_mask > 0).sum())
        percent = (water_pixels / total_valid * 100) if total_valid > 0 else 0.0
        
        # Центр массы воды
        center = None
        if water_pixels > 0:
            ys, xs = np.where(water_mask > 0)
            if len(xs) > 0:
                cx = int(xs.mean())
                cy = int(ys.mean())
                center = (cx, cy)
        
        threshold = self.config.get("water_threshold_percent", 8.0)
        return percent > threshold, percent, center, water_mask

    def _draw_water_overlay(self, frame, water_mask):
        """Полупрозрачная зелёная маска воды."""
        if water_mask is None or water_mask.size == 0:
            return frame
        overlay = frame.copy()
        overlay[water_mask > 0] = [0, 255, 0]
        cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)
        return frame

    def _draw_cursor_and_water(self, frame):
        """Рисует курсор, статус воды, процент и центр."""
        h, w = frame.shape[:2]
        
        # 🆕 Таймер проверки воды
        check_interval = self.config.get("water_check_interval", 2.0)
        now = time.time()
        if now - self._last_water_check_time < check_interval:
            # Используем последний результат, не пересчитываем
            has_water = self._has_water
            percent = self._water_percent
            center = self._water_center
            water_mask = None  # не перерисовываем каждый кадр
        else:
            has_water, percent, center, water_mask = self._check_water_fullscreen(frame)
            self._has_water = has_water
            self._water_percent = percent
            self._water_center = center
            self._last_water_check_time = now
        
        # Рисуем маску (только при пересчёте)
        if water_mask is not None:
            frame = self._draw_water_overlay(frame, water_mask)
        
        # Центр воды
        if center:
            cx, cy = center
            cv2.circle(frame, (cx, cy), 12, (0, 255, 255), 2)
            cv2.drawMarker(frame, (cx, cy), (0, 255, 255), cv2.MARKER_CROSS, 20, 2)
        
        # Курсор
        sx, sy = pyautogui.position()
        fx = sx - self.input_ctrl.offset_x
        fy = sy - self.input_ctrl.offset_y
        in_frame = (0 <= fx < w) and (0 <= fy < h)
        
        if in_frame:
            cv2.rectangle(frame, (fx-15, fy-15), (fx+15, fy+15), (0, 255, 0), 2)
            cv2.putText(frame, f"CURSOR: ({fx}, {fy})", (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        else:
            cv2.putText(frame, "CURSOR: OUT OF FRAME", (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Статус воды
        water_text = f"WATER: {'OK' if has_water else 'NO'} ({percent:.1f}%)"
        water_color = (0, 255, 0) if has_water else (0, 0, 255)
        cv2.putText(frame, water_text, (10, 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, water_color, 1)
        
        if center:
            cv2.putText(frame, f"WATER_CENTER: {center}", (10, 145),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

    def _draw_state_info(self, frame):
        color = (0, 255, 0) if self.active else (100, 100, 100)
        cv2.putText(frame, f"STATE: {self.state}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, f"Score: {self._last_score:.2f}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        if self._last_bobber_loc:
            bx, by = self._last_bobber_loc
            cv2.circle(frame, (bx, by), 4, (0, 255, 255), -1)

    # === СОСТОЯНИЯ ===
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

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray, self.bobber_in_water, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        bx, by = max_loc
        self._last_score = max_val
        self._last_bobber_loc = (bx + self.w_in // 2, by + self.h_in // 2)

        match_threshold = self.config.get("match_threshold", 0.62)
        bite_y_threshold = self.config.get("bite_y_threshold", 7)
        missing_frames_limit = self.config.get("missing_frames_limit", 4)
        min_seen_frames = self.config.get("min_seen_frames", 4)
        max_x_jump = self.config.get("max_x_jump", 80)

        if max_val >= match_threshold:
            color = (0, 255, 0) if self.bobber_was_seen else (0, 200, 200)
            cv2.rectangle(frame, (bx, by), (bx + self.w_in, by + self.h_in), color, 2)
        else:
            cv2.rectangle(frame, (bx, by), (bx + self.w_in, by + self.h_in), (0, 0, 255), 1)

        if max_val < match_threshold:
            self.missing_frames += 1
            if self.bobber_was_seen and self.seen_streak >= min_seen_frames and self.missing_frames >= missing_frames_limit:
                self.log(f"🎯 КЛЮЁТ! (Поплавок исчез, score={max_val:.2f})")
                cv2.putText(frame, "BITE!", (frame.shape[1]//2 - 50, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                self.input_ctrl.quick_tap(0.1)
                self._set_state("MINI_GAME")
            return frame

        self.missing_frames = 0
        self.seen_streak += 1
        if self.seen_streak >= min_seen_frames:
            self.bobber_was_seen = True

        current_bobber_y = by + (self.h_in // 2)
        current_bobber_x = bx + (self.w_in // 2)

        if self.bobber_was_seen and self.last_bobber_y is not None:
            dy = current_bobber_y - self.last_bobber_y
            dx = abs(current_bobber_x - self.last_bobber_x)
            if dx > max_x_jump:
                self.last_bobber_y = current_bobber_y
                self.last_bobber_x = current_bobber_x
                return frame
            if dy > bite_y_threshold:
                self.log(f"🎯 КЛЮЁТ! (Рывок вниз на {dy}px, score={max_val:.2f})")
                cv2.putText(frame, "BITE!", (frame.shape[1]//2 - 50, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
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
        res = cv2.matchTemplate(gray, self.bobber_minigame, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        self._last_score = max_val

        match_threshold = self.config.get("match_threshold", 0.62)
        minigame_pull_x = self.config.get("minigame_pull_x", 130)
        minigame_release_x = self.config.get("minigame_release_x", 158)

        now = time.time()
        if max_val < match_threshold:
            if (now - self.last_seen_time > 2.0) or (now - self.state_enter_time > 15):
                self.log("⏱️ Мини-игра завершена. Перезапуск.")
                self.input_ctrl.release_left()
                self._set_state("STARTING")
            return frame

        self.last_seen_time = now
        x, y = max_loc
        self._last_bobber_loc = (x + self.w_min // 2, y + self.h_min // 2)

        cv2.rectangle(zoomed, (x, y), (x + self.w_min, y + self.h_min), (0, 255, 0), 2)
        cv2.line(zoomed, (minigame_pull_x, 0), (minigame_pull_x, zoomed.shape[0]), (255, 0, 0), 1)
        cv2.line(zoomed, (minigame_release_x, 0), (minigame_release_x, zoomed.shape[0]), (0, 0, 255), 1)
        cv2.putText(zoomed, f"X:{x} S:{max_val:.2f}", (5, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        h_zoom, w_zoom = zoomed.shape[:2]
        insert_y = max(0, frame.shape[0] - h_zoom - 10)
        insert_x = max(0, frame.shape[1] - w_zoom - 10)
        frame[insert_y:insert_y+h_zoom, insert_x:insert_x+w_zoom] = zoomed

        if x <= minigame_pull_x:
            if not self.input_ctrl.is_left_down():
                self.input_ctrl.press_left()
                cv2.putText(frame, "PULL", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        elif x >= minigame_release_x:
            if self.input_ctrl.is_left_down():
                self.input_ctrl.release_left()
                cv2.putText(frame, "RELEASE", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

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
        """Возвращает помеченный кадр."""
        self._draw_cursor_and_water(frame)
        
        if not self.active:
            self._draw_state_info(frame)
            return frame
            
        if self._pending_start:
            if self._has_water:
                self._pending_start = False
                self._set_state("STARTING")
            else:
                if time.time() - self._last_water_log > 5.0:
                    self.log(f"❌ Вода не найдена ({self._water_percent:.1f}%). Нужно >{self.config.get('water_threshold_percent', 8.0):.0f}%.")
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
