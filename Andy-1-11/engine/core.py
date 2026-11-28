"""
Главный цикл задачи.
"""
import time
import threading
from .water_check import WaterAnalyzer
from .float_check import FloatAnalyzer
from .cursor_watch import CursorMonitor
from .pattern_find import PatternLocator
from .area_calc import AreaCalculator
from .draw_view import FrameOverlay
from .routine import Routine
from .routine_action import RoutineAction


class TaskEngine:
    """Главный движок задачи."""

    def __init__(self, config, display, interactor, app_locator,
                 on_log=None, on_status=None, on_frame=None):
        self.config = config
        self.display = display
        self.interactor = interactor
        self.app_locator = app_locator
        self.on_log = on_log
        self.on_status = on_status
        self.on_frame = on_frame

        self.active = False
        self._thread = None

        # Компоненты
        self.water_analyzer = WaterAnalyzer(config)
        self.float_analyzer = FloatAnalyzer(config)
        self.cursor_monitor = CursorMonitor(config)
        self.pattern_locator = PatternLocator(config)
        self.area_calculator = AreaCalculator(config)
        self.frame_overlay = FrameOverlay(config)

        self.routine = Routine(self)
        self.routine_action = RoutineAction(self)

        self.acting = True
        self.state = "IDLE"
        self._last_score = 0.0
        self._last_bobber_pos = None

    def set_acting(self, value):
        self.acting = bool(value)
        if self.on_status:
            self.on_status(self.state, self.active, self.acting)

    def start(self):
        if self.active:
            return
        self.active = True
        self._thread = threading.Thread(target=self.run_loop, daemon=True)
        self._thread.start()
        self._log("▶️ Задача запущена!")

    def stop(self):
        self.active = False
        if self._thread:
            self._thread.join(timeout=5)
        self._log("⏹ Задача остановлена")

    def run_loop(self):
        """Главный цикл задачи — НЕБЛОКИРУЮЩИЙ."""
        self._log("🎣 Задача запущена!")
        self.state = "START"

        # Обновляем смещение курсора
        rect = self.app_locator.get_rect()
        if rect:
            self.cursor_monitor.set_offset(rect[0], rect[1])
            self._log(f"🎯 Смещение курсора: x={rect[0]}, y={rect[1]}")

        # Запускаем поток захвата кадров
        self.display.start()

        while self.active:
            try:
                # Получаем последний кадр (не блокирует)
                frame = self.display.get_frame()
                if frame is None:
                    time.sleep(0.05)
                    continue

                current_time = time.time()

                # Анализ воды
                if self.config.get("enable_water", True):
                    self.water_analyzer.analyze(frame, current_time)

                # Позиция курсора (обновляем каждый кадр)
                cursor_pos = self.cursor_monitor.detect(frame)

                # Зоны поиска
                area_centers = self.area_calculator.calculate_areas(
                    cursor_pos,
                    (frame.shape[1], frame.shape[0])
                )

                # Зона заброса
                cast_zone = self.area_calculator.get_cast_zone(
                    self.water_analyzer.water_center,
                    (frame.shape[1], frame.shape[0])
                )

                # Маска поплавка
                float_mask = None
                if self.config.get("enable_bobber_color", True):
                    float_mask = self.float_analyzer.get_mask(frame)

                # Отрисовка оверлеев
                bobber_loc = self._last_bobber_pos
                bobber_state = "not_found"
                if bobber_loc:
                    bobber_state = "found"
                elif self.state == "CHECK_FLOAT":
                    bobber_state = "checking"

                result = self.frame_overlay.render(
                    frame,
                    water_mask=self.water_analyzer.get_mask(frame),
                    area_centers=area_centers,
                    cursor_pos=cursor_pos,
                    float_mask=float_mask,
                    water_center=self.water_analyzer.water_center,
                    cast_zone=cast_zone,
                    bobber_loc=bobber_loc,
                    bobber_state=bobber_state,
                )

                # Отправка кадра в UI
                if self.on_frame:
                    self.on_frame(result)

                # Машина состояний (неблокирующая)
                if self.acting:
                    old_state = self.state
                    if self.state == "START":
                        self.state = self.routine.phase_start()
                    elif self.state == "CHECK_FLOAT":
                        self.state = self.routine.phase_check_float()
                    elif self.state == "HOOK":  # 🆕 Добавлено!
                        self.state = self.routine.phase_hook()
                    elif self.state == "ACTION":
                        self.state = self.routine.phase_action()
                    elif self.state == "CHALLENGE":
                        self.state = self.routine_action.phase_challenge()
                    elif self.state == "RESTART":
                        self.state = self.routine_action.phase_restart()

                    if self.state != old_state:
                        self._log(f"➡️ {old_state} → {self.state}", category="Состояния")

                time.sleep(0.05)  # ~20 FPS

            except Exception as e:
                self._log(f"⚠ Ошибка в цикле: {e}")
                time.sleep(1)

        self.display.stop()
        self.state = "IDLE"
        if self.on_status:
            self.on_status("IDLE", False)

    def _log(self, msg, category="Система"):
        if self.on_log:
            self.on_log(msg, category)