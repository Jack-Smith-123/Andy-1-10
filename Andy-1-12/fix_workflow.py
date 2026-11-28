content = '''"""
Управляет фазами задачи Andy-1.
"""
import time
import numpy as np


class Workflow:
    def __init__(self, engine):
        self._debug_counter = 0
        self.engine = engine
        self._phase_start_time = 0
        self._launch_duration = 0
        self._target_seen_count = 0
        self._target_missing_count = 0
        self._last_target_y = None
        self._last_target_x = None
        self._target_was_seen_in_monitor = False
        self._monitor_start_time = 0
        self._last_seen_time = 0
        self._target_y_history = []
        self._sink_start_y = None
        self._sink_frame_count = 0
        self._last_white_pixels = 0
        self._white_part_history = []

    def phase_start(self):
        now = time.time()
        if self._phase_start_time == 0:
            self._phase_start_time = now
            self.engine._log("START: запуск удочки", category="Состояния")
            launch_min = self.engine.config.get("cast_hold_min", 0.8)
            launch_max = self.engine.config.get("cast_hold_max", 2.0)
            launch_jitter = self.engine.config.get("cast_hold_jitter", 0.3)
            base = np.random.uniform(launch_min, launch_max)
            jitter = np.random.uniform(-launch_jitter, launch_jitter)
            self._launch_duration = max(0.1, base + jitter)
            self.engine._log(f"Удержание ЛКМ: {self._launch_duration:.2f} сек", category="Состояния")
            self.engine.interactor.press_left()
            return "START"
        elapsed = now - self._phase_start_time
        if elapsed >= self._launch_duration:
            self.engine.interactor.release_left()
            self.engine._log("Ждём появления цели...", category="Цель")
            self._phase_start_time = 0
            self._target_seen_count = 0
            self._target_missing_count = 0
            self._last_target_y = None
            self._last_target_x = None
            self._target_was_seen_in_monitor = False
            self._monitor_start_time = 0
            self._last_seen_time = 0
            self._debug_counter = 0
            self._target_y_history.clear()
            self._sink_start_y = None
            self._sink_frame_count = 0
            self._last_white_pixels = 0
            self._white_part_history.clear()
            return "CHECK_TARGET"
        return "START"

    def _find_target_in_zones(self, frame, pointer_pos, expand_zones=False):
        """
        СТРОГО ищет цель ТОЛЬКО внутри фиолетовых квадратов.
        Использует те же зоны с размерами, что и overlay.
        """
        if not pointer_pos:
            return None

        zones = self.engine.zone_calculator.calculate_zones_with_sizes(
            pointer_pos,
            (frame.shape[1], frame.shape[0])
        )

        if not zones:
            return None

        frame_h, frame_w = frame.shape[:2]

        for cx, cy, zone_size in zones:
            half = zone_size // 2
            x1 = max(0, cx - half)
            y1 = max(0, cy - half)
            x2 = min(frame_w, cx + half)
            y2 = min(frame_h, cy + half)

            zone_crop = frame[y1:y2, x1:x2]
            if zone_crop.size == 0:
                continue

            pos = self.engine.target_analyzer.detect(zone_crop)
            if pos:
                global_x = pos[0] + x1
                global_y = pos[1] + y1

                if not (x1 <= global_x <= x2 and y1 <= global_y <= y2):
                    continue

                margin = 50
                if global_x < margin or global_x > (frame_w - margin):
                    continue
                if global_y < margin or global_y > (frame_h - margin):
                    continue

                return (global_x, global_y)

        return None

    def phase_check_target(self):
        try:
            frame = self.engine.display.get_frame()
            if frame is None:
                return "CHECK_TARGET"
            pointer_pos = self.engine.pointer_monitor.detect(frame)
            if not pointer_pos:
                return "CHECK_TARGET"

            if self._debug_counter % 50 == 0:
                self._debug_counter += 1
                full_frame_pos = self.engine.target_analyzer.detect(frame)
                if full_frame_pos:
                    self.engine._log(f"Отладка: цель найдена ВЕЗДЕ в ({full_frame_pos[0]}, {full_frame_pos[1]})", category="Отладка")
                else:
                    self.engine._log("Отладка: цель НЕ найдена нигде!", category="Отладка")

            target_pos = self._find_target_in_zones(frame, pointer_pos, expand_zones=False)

            if target_pos:
                self.engine._last_target_pos = target_pos
                self._target_seen_count += 1
                self._target_missing_count = 0
                min_seen = self.engine.config.get("min_seen_frames", 2)
                if self._target_seen_count >= min_seen:
                    self.engine._log(f"Цель в зоне ({target_pos[0]}, {target_pos[1]}), ждём события...", category="Цель")
                    return "MONITOR"
            else:
                self._target_missing_count += 1
                self._target_seen_count = 0
                if self._target_missing_count > 30:
                    self.engine._log("Цель не в зонах 30 кадров, перезапуск", category="Цель")
                    return "RESTART"
            return "CHECK_TARGET"
        except Exception as e:
            self.engine._log(f"Ошибка в CHECK_TARGET: {e}", category="Цель")
            return "CHECK_TARGET"

    def phase_monitor(self):
        try:
            self._debug_counter += 1
            frame = self.engine.display.get_frame()
            if frame is None:
                return "MONITOR"
            pointer_pos = self.engine.pointer_monitor.detect(frame)
            if not pointer_pos:
                return "MONITOR"

            now = time.time()
            monitor_timeout = self.engine.config.get("monitor_timeout", 30.0)
            target_lost_timeout = self.engine.config.get("target_lost_timeout", 5.0)
            monitor_initial_delay = self.engine.config.get("monitor_initial_delay", 1.5)

            if self._monitor_start_time == 0:
                self._monitor_start_time = now
                self.engine._log(f"MONITOR: старт (delay={monitor_initial_delay}s, timeout={monitor_timeout}s)", category="Цель")

            if now - self._monitor_start_time < monitor_initial_delay:
                return "MONITOR"
            if now - self._monitor_start_time > monitor_timeout:
                self.engine._log(f"Таймаут ({monitor_timeout}с), перезапуск", category="Цель")
                return "RESTART"
            if self._target_was_seen_in_monitor and self._last_seen_time > 0:
                if now - self._last_seen_time > target_lost_timeout:
                    self.engine._log(f"Потерян на {target_lost_timeout}с, перезапуск", category="Цель")
                    return "RESTART"

            target_pos = self._find_target_in_zones(frame, pointer_pos, expand_zones=False)

            event_y_threshold = self.engine.config.get("event_y_threshold", 3)
            event_x_threshold = self.engine.config.get("event_x_threshold", 15)
            missing_frames_limit = self.engine.config.get("missing_frames_limit", 2)

            should_log = self._debug_counter <= 30 or self._debug_counter % 5 == 0

            if target_pos:
                bx, by = target_pos
                self.engine._last_target_pos = target_pos
                self._target_missing_count = 0
                self._target_was_seen_in_monitor = True
                self._last_seen_time = now

                zone_size = int(self.engine.config.get("zone_size", 100))
                half = zone_size // 2
                x1 = max(0, bx - half)
                y1 = max(0, by - half)
                x2 = min(frame.shape[1], bx + half)
                y2 = min(frame.shape[0], by + half)
                zone_crop = frame[y1:y2, x1:x2]
                white_pixels = self.engine.target_analyzer.detect_white_part(zone_crop)

                if self._last_target_y is not None:
                    dy = by - self._last_target_y
                    dx = abs(bx - self._last_target_x) if self._last_target_x is not None else 0

                    if should_log:
                        self.engine._log(f"[{self._debug_counter}] ({bx},{by}) dy={dy:+d} dx={dx} white={white_pixels}", category="Отладка")

                    if dy >= event_y_threshold:
                        self.engine._log(f"СОБЫТИЕ! Рывок вниз {dy}px (порог {event_y_threshold})", category="Цель")
                        self.engine.interactor.quick_tap(0.1)
                        self._reset_monitor_state()
                        return "PROCESS"
                    if dx >= event_x_threshold:
                        self.engine._log(f"СОБЫТИЕ! Рывок в сторону {dx}px (порог {event_x_threshold})", category="Цель")
                        self.engine.interactor.quick_tap(0.1)
                        self._reset_monitor_state()
                        return "PROCESS"
                    if self._last_white_pixels > 20 and white_pixels < self._last_white_pixels * 0.5:
                        loss = self._last_white_pixels - white_pixels
                        self.engine._log(f"СОБЫТИЕ! Белая часть -{loss} пикселей ({self._last_white_pixels}->{white_pixels})", category="Цель")
                        self.engine.interactor.quick_tap(0.1)
                        self._reset_monitor_state()
                        return "PROCESS"
                else:
                    if should_log:
                        self.engine._log(f"[{self._debug_counter}] ({bx},{by}) ПЕРВЫЙ КАДР white={white_pixels}", category="Отладка")

                self._last_target_y = by
                self._last_target_x = bx
                self._last_white_pixels = white_pixels
            else:
                self._target_missing_count += 1
                self.engine._last_target_pos = None
                if should_log:
                    self.engine._log(f"[{self._debug_counter}] Цель не найдена ({self._target_missing_count} кадров)", category="Отладка")
                if self._target_was_seen_in_monitor and self._target_missing_count >= missing_frames_limit:
                    self.engine._log(f"СОБЫТИЕ! Цель исчезла из зон ({self._target_missing_count} кадров)", category="Цель")
                    self.engine.interactor.quick_tap(0.1)
                    self._reset_monitor_state()
                    return "PROCESS"
            return "MONITOR"
        except Exception as e:
            self.engine._log(f"ОШИБКА В MONITOR: {e}", category="Цель")
            import traceback
            self.engine._log(traceback.format_exc(), category="Цель")
            return "MONITOR"

    def _reset_monitor_state(self):
        self._last_target_y = None
        self._last_target_x = None
        self._target_was_seen_in_monitor = False
        self._target_y_history.clear()
        self._sink_start_y = None
        self._sink_frame_count = 0
        self._last_white_pixels = 0
        self._white_part_history.clear()
'''

with open('core/workflow.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('OK workflow.py переписан')
