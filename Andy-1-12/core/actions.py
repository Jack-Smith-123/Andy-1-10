"""
Фазы задачи Andy-1: process (мини-игра), restart.
"""
import time


class WorkflowAction:
    """Управляет фазами мини-игры и перезапуска."""

    def __init__(self, engine):
        self.engine = engine
        self._phase_start_time = 0

    def phase_process(self):
        """Фаза мини-игры."""
        if self._phase_start_time == 0:
            self._phase_start_time = time.time()
            self.engine._log("🎮 PROCESS: мини-игра началась", category="Состояния")

        elapsed = time.time() - self._phase_start_time
        timeout = self.engine.config.get("mini_game_max_time", 15.0)

        if elapsed > timeout:
            self.engine._log(f"⏰ Таймаут мини-игры ({elapsed:.1f}с)", category="Состояния")
            self._phase_start_time = 0
            return "RESTART"

        time.sleep(0.1)
        return "RESTART"

    def phase_restart(self):
        """Фаза перезапуска."""
        if self._phase_start_time == 0:
            self._phase_start_time = time.time()
            self.engine._log("🔄 RESTART: перезапуск цикла", category="Состояния")
            self.engine.interactor.right_click()
            return "RESTART"
        
        restart_delay = self.engine.config.get("restart_delay", 2.0)
        if time.time() - self._phase_start_time >= restart_delay:
            self._phase_start_time = 0
            return "START"
        
        return "RESTART"