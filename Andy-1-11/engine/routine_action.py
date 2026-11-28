"""
Фазы задачи: challenge (мини-игра), restart — НЕБЛОКИРУЮЩИЕ.
"""
import time


class RoutineAction:
    """Управляет фазами мини-игры и перезапуска."""

    def __init__(self, engine):
        self.engine = engine
        self._phase_start_time = 0

    def phase_challenge(self):
        """Фаза мини-игры."""
        if self._phase_start_time == 0:
            self._phase_start_time = time.time()
            self.engine._log("🎮 CHALLENGE: мини-игра началась", category="Состояния")

        elapsed = time.time() - self._phase_start_time
        timeout = self.engine.config.get("mini_game_max_time", 15.0)

        if elapsed > timeout:
            self.engine._log(f"⏰ Таймаут мини-игры ({elapsed:.1f}с)", category="Состояния")
            self._phase_start_time = 0
            return "RESTART"

        # Здесь должна быть логика мини-игры (пока просто ждём)
        time.sleep(0.1)
        return "RESTART"

    def phase_restart(self):
        """Фаза перезапуска — клик ПКМ чтобы снова закинуть удочку."""
        if self._phase_start_time == 0:
            self._phase_start_time = time.time()
            self.engine._log("🔄 RESTART: перезапуск цикла", category="Состояния")
            # В Albion нужно ПКМ для повторного заброса
            self.engine.interactor.right_click()
            return "RESTART"
        
        restart_delay = self.engine.config.get("restart_delay", 2.0)
        if time.time() - self._phase_start_time >= restart_delay:
            self._phase_start_time = 0
            return "START"
        
        return "RESTART"