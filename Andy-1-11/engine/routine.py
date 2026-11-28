"""
Фазы задачи — СТРОГИЙ поиск только в фиолетовых квадратах.
"""
import time
import numpy as np


class Routine:
    """Управляет фазами задачи."""

    def __init__(self, engine):
        self._debug_counter = 0
        self.engine = engine
        self._phase_start_time = 0
        self._cast_duration = 0
        
        
        self._bobber_seen_count = 0
        self._bobber_missing_count = 0
        self._last_bobber_y = None
        self._last_bobber_x = None
        self._bobber_was_seen_in_hook = False
        self._hook_start_time = 0
        self._last_seen_time = 0
        self._debug_counter = 0
        
        self._bobber_y_history = []
        self._sink_start_y = None
        self._sink_frame_count = 0
        
        self._last_white_pixels = 0
        self._white_part_history = []

    def phase_start(self):
        now = time.time()
        
        if self._phase_start_time == 0:
            self._phase_start_time = now
            self.engine._log("🎣 START: заброс удочки", category="Состояния")
            
            cast_min = self.engine.config.get("cast_hold_min", 0.8)
            cast_max = self.engine.config.get("cast_hold_max", 2.0)
            cast_jitter = self.engine.config.get("cast_hold_jitter", 0.3)
            
            base = np.random.uniform(cast_min, cast_max)
            jitter = np.random.uniform(-cast_jitter, cast_jitter)
            self._cast_duration = max(0.1, base + jitter)
            
            self.engine._log(f"🎯 Удержание ЛКМ: {self._cast_duration:.2f} сек", category="Состояния")
            self.engine.interactor.press_left()
            return "START"
        
        elapsed = now - self._phase_start_time
        if elapsed >= self._cast_duration:
            self.engine.interactor.release_left()
            self.engine._log("⏳ Ждём появления поплавка...", category="Поплавок")
            self._phase_start_time = 0
            self._bobber_seen_count = 0
            self._bobber_missing_count = 0
            self._last_bobber_y = None
            self._last_bobber_x = None
            self._bobber_was_seen_in_hook = False
            self._hook_start_time = 0
            self._last_seen_time = 0
            self._debug_counter = 0
            self._bobber_y_history.clear()
            self._sink_start_y = None
            self._sink_frame_count = 0
            self._last_white_pixels = 0
            self._white_part_history.clear()
            return "CHECK_FLOAT"
        
        return "START"

    def _find_bobber_in_zones(self, frame, cursor_pos, expand_zones=False):
        """
        СТРОГО ищет поплавок ТОЛЬКО внутри фиолетовых квадратов.
        expand_zones=True слегка увеличивает зоны для HOOK (в 1.5 раза вместо 4).
        """
        area_centers = self.engine.area_calculator.calculate_areas(
            cursor_pos,
            (frame.shape[1], frame.shape[0])
        )
        
        # Уменьшенное расширение в HOOK (было 4.0, стало 1.5)
        expansion = 1.5 if expand_zones else 1.0
        
        frame_h, frame_w = frame.shape[:2]
        
        for i, (cx, cy) in enumerate(area_centers):
            zone_num = i + 1
            if not self.engine.config.get(f"zone_{zone_num}_enabled", True):
                continue
            
            # Базовый размер из конфига
            base_size = self.engine.config.get(f"zone_{zone_num}_size", 100)
            size = int(base_size * expansion)
            half = size // 2
            
            x1 = max(0, cx - half)
            y1 = max(0, cy - half)
            x2 = min(frame_w, cx + half)
            y2 = min(frame_h, cy + half)
            
            # Вырезаем зону
            zone_crop = frame[y1:y2, x1:x2]
            if zone_crop.size == 0:
                continue
            
            # Ищем поплавок в зоне
            pos = self.engine.float_analyzer.detect(zone_crop)
            if pos:
                # Возвращаем глобальные координаты
                global_x = pos[0] + x1
                global_y = pos[1] + y1
                
                # СТРОГАЯ проверка: координаты должны быть внутри зоны!
                if not (x1 <= global_x <= x2 and y1 <= global_y <= y2):
                    continue
                
                # Дополнительная проверка: поплавок не должен быть слишком близко к краям экрана (где UI)
                margin = 50  # отступ от краев
                if global_x < margin or global_x > (frame_w - margin):
                    continue
                if global_y < margin or global_y > (frame_h - margin):
                    continue
                
                return (global_x, global_y)
        
        return None

    def phase_check_float(self):
        """Фаза проверки — ТОЛЬКО в зонах."""
        try:
            frame = self.engine.display.get_frame()
            if frame is None:
                return "CHECK_FLOAT"

            cursor_pos = self.engine.cursor_monitor.detect(frame)
            if not cursor_pos:
                return "CHECK_FLOAT"

            # ОТЛАДКА: ищем поплавок ВЕЗДЕ (не только в зонах) каждые 50 кадров
            if self._debug_counter % 50 == 0:
                self._debug_counter += 1
                full_frame_pos = self.engine.float_analyzer.detect(frame)
                if full_frame_pos:
                    self.engine._log(f"🔍 Отладка: поплавок найден ВЕЗДЕ в ({full_frame_pos[0]}, {full_frame_pos[1]})", category="Отладка")
                else:
                    self.engine._log("🔍 Отладка: поплавок НЕ найден нигде!", category="Отладка")

            # Строго только в зонах
            float_pos = self._find_bobber_in_zones(frame, cursor_pos, expand_zones=False)
            
            if float_pos:
                self.engine._last_bobber_pos = float_pos
                self._bobber_seen_count += 1
                self._bobber_missing_count = 0
                
                min_seen = self.engine.config.get("min_seen_frames", 2)
                if self._bobber_seen_count >= min_seen:
                    self.engine._log(f"🎯 Поплавок в зоне ({float_pos[0]}, {float_pos[1]}), ждём клёва...", category="Поплавок")
                    return "HOOK"
            else:
                self._bobber_missing_count += 1
                self._bobber_seen_count = 0
                
                if self._bobber_missing_count > 30:
                    self.engine._log("⚠️ Поплавок не в зонах 30 кадров, перезапуск", category="Поплавок")
                    return "RESTART"
            
            return "CHECK_FLOAT"
        except Exception as e:
            self.engine._log(f"❌ Ошибка в CHECK_FLOAT: {e}", category="Поплавок")
            return "CHECK_FLOAT"

    def phase_hook(self):
        """Фаза ожидания клёва — с МАКСИМАЛЬНОЙ отладкой."""
        try:
            self._debug_counter += 1
            
            frame = self.engine.display.get_frame()
            if frame is None:
                return "HOOK"

            cursor_pos = self.engine.cursor_monitor.detect(frame)
            if not cursor_pos:
                return "HOOK"

            now = time.time()
            hook_timeout = self.engine.config.get("hook_timeout", 30.0)
            bobber_lost_timeout = self.engine.config.get("bobber_lost_timeout", 5.0)
            hook_initial_delay = self.engine.config.get("hook_initial_delay", 1.5)
            
            if self._hook_start_time == 0:
                self._hook_start_time = now
                self.engine._log(f"🔧 HOOK: старт (delay={hook_initial_delay}s, timeout={hook_timeout}s)", category="Поплавок")
            
            if now - self._hook_start_time < hook_initial_delay:
                return "HOOK"
            
            if now - self._hook_start_time > hook_timeout:
                self.engine._log(f"⏰ Таймаут ({hook_timeout}с), перезапуск", category="Поплавок")
                return "RESTART"
            
            if self._bobber_was_seen_in_hook and self._last_seen_time > 0:
                if now - self._last_seen_time > bobber_lost_timeout:
                    self.engine._log(f"⚠️ Потерян на {bobber_lost_timeout}с, перезапуск", category="Поплавок")
                    return "RESTART"
            
            # Ищем поплавок БЕЗ расширения зон (только в фиолетовых квадратах)
            float_pos = self._find_bobber_in_zones(frame, cursor_pos, expand_zones=False)
            
            # Пороги из конфига
            bite_y_threshold = self.engine.config.get("bite_y_threshold", 3)
            bite_x_threshold = self.engine.config.get("bite_x_threshold", 15)
            missing_frames_limit = self.engine.config.get("missing_frames_limit", 2)
            
            # 📊 ОТЛАДКА КАЖДОГО КАДРА (первые 30 кадров, потом каждые 5)
            should_log = self._debug_counter <= 30 or self._debug_counter % 5 == 0
            
            if float_pos:
                bx, by = float_pos
                self.engine._last_bobber_pos = float_pos
                self._bobber_missing_count = 0
                self._bobber_was_seen_in_hook = True
                self._last_seen_time = now
                
                # Считаем белую часть
                zone_size = 120
                half = zone_size // 2
                x1 = max(0, bx - half)
                y1 = max(0, by - half)
                x2 = min(frame.shape[1], bx + half)
                y2 = min(frame.shape[0], by + half)
                zone_crop = frame[y1:y2, x1:x2]
                white_pixels = self.engine.float_analyzer.detect_white_part(zone_crop)
                
                # Логируем движение
                if self._last_bobber_y is not None:
                    dy = by - self._last_bobber_y
                    dx = abs(bx - self._last_bobber_x) if self._last_bobber_x is not None else 0
                    
                    if should_log:
                        self.engine._log(
                            f"📊 [{self._debug_counter}] ({bx},{by}) dy={dy:+d} dx={dx} white={white_pixels}",
                            category="Отладка"
                        )
                    
                    # 🎯 АНАЛИЗ ПОКЛЕВКИ
                    
                    # 1. Резкое движение вниз
                    if dy >= bite_y_threshold:
                        self.engine._log(f"🎯 КЛЁВ! Рывок вниз {dy}px (порог {bite_y_threshold})", category="Поплавок")
                        self.engine.interactor.quick_tap(0.1)
                        self._reset_hook_state()
                        return "CHALLENGE"
                    
                    # 2. Резкое движение в сторону
                    if dx >= bite_x_threshold:
                        self.engine._log(f"🎯 КЛЁВ! Рывок в сторону {dx}px (порог {bite_x_threshold})", category="Поплавок")
                        self.engine.interactor.quick_tap(0.1)
                        self._reset_hook_state()
                        return "CHALLENGE"
                    
                    # 3. Исчезновение белой части (поплавок ушел под воду)
                    if self._last_white_pixels > 20 and white_pixels < self._last_white_pixels * 0.5:
                        loss = self._last_white_pixels - white_pixels
                        self.engine._log(f"🎯 КЛЁВ! Белая часть -{loss} пикселей ({self._last_white_pixels}→{white_pixels})", category="Поплавок")
                        self.engine.interactor.quick_tap(0.1)
                        self._reset_hook_state()
                        return "CHALLENGE"
                    
                else:
                    if should_log:
                        self.engine._log(
                            f"📊 [{self._debug_counter}] ({bx},{by}) ПЕРВЫЙ КАДР white={white_pixels}",
                            category="Отладка"
                        )
                
                self._last_bobber_y = by
                self._last_bobber_x = bx
                self._last_white_pixels = white_pixels
                
            else:
                # Поплавок НЕ найден
                self._bobber_missing_count += 1
                self.engine._last_bobber_pos = None
                
                if should_log:
                    self.engine._log(f"⚠️ [{self._debug_counter}] Поплавок НЕ найден ({self._bobber_missing_count} кадров)", category="Отладка")
                
                # КЛЁВ: поплавок исчез из зон (это часто значит что его дернула рыба)
                if self._bobber_was_seen_in_hook and self._bobber_missing_count >= missing_frames_limit:
                    self.engine._log(f"🎯 КЛЁВ! Поплавок исчез из зон ({self._bobber_missing_count} кадров)", category="Поплавок")
                    self.engine.interactor.quick_tap(0.1)
                    self._reset_hook_state()
                    return "CHALLENGE"
            
            return "HOOK"
            
        except Exception as e:
            self.engine._log(f"❌ ОШИБКА В HOOK: {e}", category="Поплавок")
            import traceback
            self.engine._log(traceback.format_exc(), category="Поплавок")
            return "HOOK"

    def _reset_hook_state(self):
        self._last_bobber_y = None
        self._last_bobber_x = None
        self._bobber_was_seen_in_hook = False
        self._bobber_y_history.clear()
        self._sink_start_y = None
        self._sink_frame_count = 0
        self._last_white_pixels = 0
        self._white_part_history.clear()