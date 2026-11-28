"""
Главный цикл задачи Andy-1.
"""
import time
import threading
from .environment_check import EnvironmentAnalyzer
from .target_check import TargetAnalyzer
from .pointer_watch import PointerMonitor
from .template_find import TemplateLocator
from .zone_calc import ZoneCalculator
from .overlay_view import FrameOverlay
from .workflow import Workflow
from .actions import WorkflowAction


class AppCore:
    """Главный движок задачи Andy-1."""

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
        self.environment_analyzer = EnvironmentAnalyzer(config)
        self.target_analyzer = TargetAnalyzer(config)
        self.pointer_monitor = PointerMonitor(config)
        self.template_locator = TemplateLocator(config)
        self.zone_calculator = ZoneCalculator(config)
        self.frame_overlay = FrameOverlay(config)

        self.workflow = Workflow(self)
        self.workflow_action = WorkflowAction(self)

        self.acting = True
        self.state = "IDLE"
        self._last_score = 0.0
        self._last_target_pos = None

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

        rect = self.app_locator.get_rect()
        if rect:
            self.pointer_monitor.set_offset(rect[0], rect[1])
            self._log(f"🎯 Смещение указателя: x={rect[0]}, y={rect[1]}")

        self.display.start()

        while self.active:
            try:
                frame = self.display.get_frame()
                if frame is None:
                    time.sleep(0.05)
                    continue

                current_time = time.time()

                if self.config.get("enable_environment", True):
                    self.environment_analyzer.analyze(frame, current_time)

                pointer_pos = self.pointer_monitor.detect(frame)

                zones = self.zone_calculator.calculate_zones_with_sizes(
                    pointer_pos,
                    (frame.shape[1], frame.shape[0])
                )

                launch_zone = self.zone_calculator.get_launch_zone(
                    self.environment_analyzer.environment_center,
                    (frame.shape[1], frame.shape[0])
                )

                target_mask = None
                if self.config.get("enable_target_color", True):
                    target_mask = self.target_analyzer.get_mask(frame)

                target_loc = self._last_target_pos
                target_state = "not_found"
                if target_loc:
                    target_state = "found"
                elif self.state == "CHECK_TARGET":
                    target_state = "checking"

                result = self.frame_overlay.render(
                    frame,
                    environment_mask=self.environment_analyzer.get_mask(frame),
                    zones=zones,
                    pointer_pos=pointer_pos,
                    target_mask=target_mask,
                    environment_center=self.environment_analyzer.environment_center,
                    launch_zone=launch_zone,
                    target_loc=target_loc,
                    target_state=target_state,
                )

                if self.on_frame:
                    self.on_frame(result)

                if self.acting:
                    old_state = self.state
                    if self.state == "START":
                        self.state = self.workflow.phase_start()
                    elif self.state == "CHECK_TARGET":
                        self.state = self.workflow.phase_check_target()
                    elif self.state == "MONITOR":
                        self.state = self.workflow.phase_monitor()
                    elif self.state == "ACTION":
                        self.state = self.workflow.phase_action()
                    elif self.state == "PROCESS":
                        self.state = self.workflow_action.phase_process()
                    elif self.state == "RESTART":
                        self.state = self.workflow_action.phase_restart()

                    if self.state != old_state:
                        self._log(f"➡️ {old_state} → {self.state}", category="Состояния")

                time.sleep(0.05)

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