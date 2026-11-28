"""
Методы состояний для FishingService.
Все состояния: STARTING, CHECK_BOBBER, HOOK, MINI_GAME, RESTART.
"""
import cv2
import time
import numpy as np


class FishingStates:
    """Миксин с методами состояний для FishingService."""

    def _state_starting(self, frame):
        """Заброс удочки."""
        all_zones = self._compute_zones_along_line(frame)
        cursor_zone = self._compute_cursor_zone(frame)
        self._all_search_zones = all_zones
        self._draw_search_line(frame, all_zones, cursor_zone)
        if time.time() - self.state_enter_time < 2.0:
            return frame
        cast_min = self.config.get("cast_hold_min", 0.8)
        cast_max = self.config.get("cast_hold_max", 2.0)
        cast_jitter = self.config.get("cast_hold_jitter", 0.3)
        base = np.random.uniform(cast_min, cast_max)
        jitter = np.random.uniform(-cast_jitter, cast_jitter)
        duration = max(0.1, base + jitter)
        self.log("🎣 Забрасываем (удержание " + str(round(duration, 2)) + " сек)...")
        self.input_ctrl.cast_hold(duration)
        time.sleep(2.0)
        self._set_state("CHECK_BOBBER")
        return frame

    def _state_check_bobber(self, frame):
        """Проверяем наличие поплавка."""
        all_zones = self._compute_zones_along_line(frame)
        cursor_zone = self._compute_cursor_zone(frame)
        self._all_search_zones = all_zones
        self._draw_search_line(frame, all_zones, cursor_zone)
        hook_delay = self.config.get("hook_initial_delay", 6.0)
        if time.time() - self.state_enter_time < hook_delay:
            return frame
        found, px, py, score = self._check_bobber_present(frame)
        if found:
            self.log("✅ Поплавок найден! score=" + str(round(score, 2)) + " pos=(" + str(px) + "," + str(py) + ")")
            self._last_bobber_loc = (px, py)
            self._set_state("HOOK")
            self.bobber_was_seen = True
        else:
            self.log("⚠️ Поплавок не найден. Повторный заброс.")
            self._set_state("STARTING")
        return frame

    def _state_hook(self, frame):
        """Ожидание поклёвки."""
        hook_timeout = self.config.get("hook_timeout", 15.0)
        if not self.bobber_was_seen and hook_timeout > 0:
            if time.time() - self.state_enter_time > hook_timeout:
                self.log("⚠️ Поплавок так и не появился. Рестарт.")
                self._set_state("RESTART")
                return frame
        bobber_lost_timeout = self.config.get("bobber_lost_timeout", 8.0)
        if self.bobber_was_seen and self.last_seen_bobber_time:
            if time.time() - self.last_seen_bobber_time > bobber_lost_timeout:
                self.log("⚠️ Поплавок потерян на " + str(bobber_lost_timeout) + " сек. Рестарт.")
                self._set_state("RESTART")
                return frame
        all_zones = self._compute_zones_along_line(frame)
        cursor_zone = self._compute_cursor_zone(frame)
        self._all_search_zones = all_zones
        found, abs_x, abs_y, score, best_offset, bx, by = self._find_bobber_in_zones(
            frame, all_zones, cursor_zone
        )
        self._draw_search_line(frame, all_zones, cursor_zone)
        hh = self.template_matcher.h_water
        ww = self.template_matcher.w_water
        if found:
            self.last_seen_bobber_time = time.time()
            color = (0, 255, 0) if self.bobber_was_seen else (0, 200, 200)
            cv2.rectangle(
                frame,
                (bx + best_offset[0], by + best_offset[1]),
                (bx + best_offset[0] + ww, by + best_offset[1] + hh),
                color, 2
            )
        else:
            cv2.rectangle(
                frame,
                (bx + best_offset[0], by + best_offset[1]),
                (bx + best_offset[0] + ww, by + best_offset[1] + hh),
                (0, 0, 255), 1
            )
        bite_y_threshold = self.config.get("bite_y_threshold", 7)
        missing_frames_limit = self.config.get("missing_frames_limit", 4)
        min_seen_frames = self.config.get("min_seen_frames", 4)
        max_x_jump = self.config.get("max_x_jump", 80)
        if not found:
            self.missing_frames += 1
            if self.bobber_was_seen and self.seen_streak >= min_seen_frames:
                if self.missing_frames >= missing_frames_limit:
                    self.log("🎯 КЛЮЁТ! Поплавок исчез score=" + str(round(score, 2)))
                    self.input_ctrl.quick_tap(0.1)
                    self._set_state("MINI_GAME")
            return frame
        self.missing_frames = 0
        self.seen_streak += 1
        if self.seen_streak >= min_seen_frames:
            self.bobber_was_seen = True
        current_bobber_y = by + best_offset[1] + hh // 2
        current_bobber_x = bx + best_offset[0] + ww // 2
        if self.bobber_was_seen and self.last_bobber_y is not None:
            dy = current_bobber_y - self.last_bobber_y
            dx = abs(current_bobber_x - self.last_bobber_x)
            if dx > max_x_jump:
                self.last_bobber_y = current_bobber_y
                self.last_bobber_x = current_bobber_x
                return frame
            if dy > bite_y_threshold:
                self.log("🎯 КЛЮЁТ! Рывок вниз на " + str(dy) + "px score=" + str(round(score, 2)))
                self.input_ctrl.quick_tap(0.1)
                self._set_state("MINI_GAME")
                self.last_bobber_y = None
                return frame
        self.last_bobber_y = current_bobber_y
        self.last_bobber_x = current_bobber_x
        return frame

    def _state_mini_game(self, frame):
        """Мини-игра."""
        cropped = self.crop_center(frame, 130, 50)
        if cropped is None or cropped.size == 0:
            return frame
        zoomed = cv2.resize(cropped, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        gray = cv2.cvtColor(zoomed, cv2.COLOR_BGR2GRAY)
        max_val, max_loc, best_idx = self.template_matcher.match_best(
            gray, self.template_matcher.minigame_templates
        )
        self._last_score = max_val
        self._best_template_idx = best_idx
        minigame_threshold = 0.55
        minigame_pull_x = int(self.config.get("minigame_pull_x", 130))
        minigame_release_x = int(self.config.get("minigame_release_x", 158))
        minigame_center_min = 135
        minigame_center_max = 155
        now = time.time()
        minigame_lost_timeout = self.config.get("minigame_lost_timeout", 1.0)
        minigame_max_duration = self.config.get("minigame_max_duration", 12.0)
        if max_val < minigame_threshold:
            if now - self.last_seen_time > minigame_lost_timeout:
                self.log("⚠️ Мини-игра не найдена " + str(minigame_lost_timeout) + " сек. Рестарт.")
                self.input_ctrl.release_left()
                self._set_state("RESTART")
                return frame
        else:
            self.last_seen_time = now
        if now - self.state_enter_time > minigame_max_duration:
            self.log("⏱️ Мини-игра дольше " + str(minigame_max_duration) + " сек. Рестарт.")
            self.input_ctrl.release_left()
            self._set_state("RESTART")
            return frame
        x, y = max_loc
        self._last_bobber_loc = (
            x // 2 + self.template_matcher.w_minigame // 2,
            y // 2 + self.template_matcher.h_minigame // 2
        )
        cv2.rectangle(
            zoomed, (x, y),
            (x + self.template_matcher.w_minigame, y + self.template_matcher.h_minigame),
            (0, 255, 0), 2
        )
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
        """Отмена и перезапуск."""
        if time.time() - self.state_enter_time < 0.5:
            return frame
        self.log("🔄 Отмена и перезапуск...")
        self.input_ctrl.release_left()
        self.input_ctrl.right_click()
        time.sleep(1)
        self._set_state("STARTING")
        return frame
