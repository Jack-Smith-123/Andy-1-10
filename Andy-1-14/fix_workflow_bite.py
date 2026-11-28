with open('core/workflow.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Заменяем логику детекта поклевки в phase_monitor
old_bite_logic = '''                if self._last_target_y is not None:
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
                        return "PROCESS"'''

new_bite_logic = '''                if self._last_target_y is not None:
                    dy = by - self._last_target_y
                    dx = abs(bx - self._last_target_x) if self._last_target_x is not None else 0

                    # Проверяем поклевку по белым пикселям (новая логика)
                    is_biting = self.engine.target_analyzer.is_biting(white_pixels)

                    if should_log:
                        self.engine._log(f"[{self._debug_counter}] ({bx},{by}) dy={dy:+d} dx={dx} white={white_pixels} biting={is_biting}", category="Отладка")

                    if is_biting:
                        self.engine._log(f"СОБЫТИЕ! Поклевка (белая часть ушла под воду, white={white_pixels})", category="Цель")
                        self.engine.interactor.quick_tap(0.1)
                        self._reset_monitor_state()
                        return "PROCESS"
                    if dy >= event_y_threshold:
                        self.engine._log(f"СОБЫТИЕ! Рывок вниз {dy}px (порог {event_y_threshold})", category="Цель")
                        self.engine.interactor.quick_tap(0.1)
                        self._reset_monitor_state()
                        return "PROCESS"
                    if dx >= event_x_threshold:
                        self.engine._log(f"СОБЫТИЕ! Рывок в сторону {dx}px (порог {event_x_threshold})", category="Цель")
                        self.engine.interactor.quick_tap(0.1)
                        self._reset_monitor_state()
                        return "PROCESS"'''

if old_bite_logic in content:
    content = content.replace(old_bite_logic, new_bite_logic)
    with open('core/workflow.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK workflow - updated bite detection')
else:
    print('WARNING: не найдена старая логика поклевки')
