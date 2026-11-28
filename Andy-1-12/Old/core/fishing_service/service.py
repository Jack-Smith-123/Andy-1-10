"""
Оркестратор рыбалки Andy-1-3.
🆕 Разбит на 3 файла: service.py + helpers.py + states.py.
🆕 HSV настройки для поиска поплавка.
"""
import cv2
import time
import numpy as np

from .template_matcher import TemplateMatcher
from .search_zone import SearchZone
from .visualizer import Visualizer
from .color_bobber_detector import ColorBobberDetector
from ..water_detector import WaterDetector
from ..cursor_tracker import CursorTracker
from .helpers import FishingHelpers
from .states import FishingStates


class FishingService(FishingHelpers, FishingStates):
    """Главный класс рыбалки. Наследует хелперы и состояния."""

    def __init__(self, config, input_ctrl, log_callback=None):
        self.config = config
        self.input_ctrl = input_ctrl
        self.log = log_callback or print

        self.water_detector = WaterDetector(config)
        self.cursor_tracker = CursorTracker(input_ctrl)
        self.template_matcher = TemplateMatcher(config, log_callback)
        self.search_zone = SearchZone(config, self.cursor_tracker)
        self.visualizer = Visualizer(config, self.water_detector, self.cursor_tracker)
        self.color_detector = ColorBobberDetector(config)

        self.state = "IDLE"
        self.active = False
        self.acting = True
        self.state_enter_time = 0
        self._pending_start = False

        self._has_water = False
        self._water_percent = 0.0
        self._water_center = None
        self._water_mask = None
        self._last_water_log = 0
        self._last_water_check_time = 0

        self.last_bobber_y = None
        self.last_bobber_x = None
        self.missing_frames = 0
        self.bobber_was_seen = False
        self.seen_streak = 0
        self.last_seen_bobber_time = None

        self.time_in_zone = 0.0
        self.last_seen_time = 0
        self.last_action_time = 0

        self._last_score = 0.0
        self._last_bobber_loc = None
        self._best_template_idx = -1
        self._search_zone = None
        self._all_search_zones = []
        self._cast_direction = None
        self._bobber_mask = None

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
            self.log("⏸ Действия приостановлены")
        else:
            self.log("▶ Действия возобновлены")
            if self.active and self.state == "IDLE":
                self._pending_start = True

    def _set_state(self, new_state):
        self.state = new_state
        self.state_enter_time = time.time()
        self.log("➡️ STATE: " + new_state)
        if new_state == "HOOK":
            self.bobber_was_seen = False
            self.seen_streak = 0
            self.missing_frames = 0
            self.last_bobber_y = None
            self.last_bobber_x = None
            self.last_seen_bobber_time = None
        elif new_state == "MINI_GAME":
            self.time_in_zone = 0.0
            self.last_seen_time = time.time()
            self.last_action_time = 0

    def controller(self, frame):
        """Основной цикл обработки кадра."""
        check_interval = self.config.get("water_check_interval", 2.0)
        now = time.time()
        if self.config.get("vis_water_enabled", True):
            if now - self._last_water_check_time < check_interval:
                has_water = self._has_water
                percent = self._water_percent
                center = self._water_center
                water_mask = self._water_mask
            else:
                has_water, percent, center, water_mask = self.water_detector.detect(frame)
                self._has_water = has_water
                self._water_percent = percent
                self._water_center = center
                self._water_mask = water_mask
                self._last_water_check_time = now
        else:
            has_water, percent, center, water_mask = False, 0.0, None, None
        self.visualizer.draw_cursor_and_water(frame, has_water, percent, center, water_mask)
        if self.config.get("vis_bobber_show", True) and self._bobber_mask is not None:
            overlay = frame.copy()
            overlay[self._bobber_mask > 0] = [255, 105, 255]
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        if not self.active or not self.acting:
            self.visualizer.draw_state_info(frame, self._last_bobber_loc)
            return frame
        if self._pending_start:
            if self._has_water and self._water_center:
                click_radius = int(self.config.get("water_click_radius", 40))
                angle = np.random.uniform(0, 2 * np.pi)
                dist = np.sqrt(np.random.uniform(0, 1)) * click_radius
                tx = int(self._water_center[0] + dist * np.cos(angle))
                ty = int(self._water_center[1] + dist * np.sin(angle))
                h, w = frame.shape[:2]
                cx, cy = w // 2, h // 2
                dx = tx - cx
                dy = ty - cy
                length = max(1, np.sqrt(dx ** 2 + dy ** 2))
                self._cast_direction = (dx / length, dy / length)
                self.log("🎯 Направление заброса: (" + str(round(self._cast_direction[0], 2)) + ", " + str(round(self._cast_direction[1], 2)) + ")")
                self.log("🖱️ Плавный клик по воде: (" + str(tx) + ", " + str(ty) + ") [зона ±" + str(click_radius) + "px]")
                self.input_ctrl.move_to_frame_and_click(tx, ty)
                time.sleep(1.5)
                self._pending_start = False
                self._set_state("STARTING")
            elif self._has_water:
                self._pending_start = False
                self._set_state("STARTING")
            else:
                if time.time() - self._last_water_log > 5.0:
                    thr = self.config.get("water_threshold_percent", 8.0)
                    self.log("❌ Вода не найдена (" + str(round(self._water_percent, 1)) + "%). Нужно >" + str(int(thr)) + "%.")
                    self._last_water_log = time.time()
            return frame
        if self.state == "STARTING":
            frame = self._state_starting(frame)
        elif self.state == "CHECK_BOBBER":
            frame = self._state_check_bobber(frame)
        elif self.state == "HOOK":
            frame = self._state_hook(frame)
        elif self.state == "MINI_GAME":
            frame = self._state_mini_game(frame)
        elif self.state == "RESTART":
            frame = self._state_restart(frame)
        self.visualizer.draw_state_info(frame, self._last_bobber_loc)
        return frame
