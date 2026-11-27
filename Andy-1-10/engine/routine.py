"""
Фазы задачи — СТРОГИЙ поиск только в фиолетовых квадратах.
"""
import time
import numpy as np


class Routine:
    """Управляет фазами задачи."""

    def __init__(self, engine):
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
        expand_zones=True увеличивает зоны в 4 раза для HOOK.
        """
        area_centers = self.engine.area_calculator.calculate_areas(
            cursor_pos,
            (frame.shape[1], frame.shape[0])
        )
        
        # 🆕 Сильное расширение зон в HOOK
        expansion = 4.0 if expand_zones else 1.0
        
        for i, (cx, cy) in enumerate(area_centers):
            zone_num = i + 1
            if not self.engine.config.get(f"zone_{zone_num}_enabled", True):
                continue
            
            # Базовый размер из конфига
            base_size = self.engine.config.get(f"zone_{zone_num}_size", 60)
            size = int(base_size * expansion)
            half = size // 2
            
            x1 = max(0, cx - half)
            y1 = max(0, cy - half)
            x2 = min(frame.shape[1], cx + half)
            y2 = min(frame.shape[0], cy + half)
            
            # Вырезаем зону
            zone_crop = frame[y1:y2, x1:x2]
            if zone_crop.size == 0:
                continue
            
            # Ищем поплавок в зоне
            pos = self.engine.float_analyzer.detect(zone_crop)
            if pos:
                # Возвращаем глобальные координаты
                return (pos[0] + x1, pos[1] + y1)
        
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
        """Фаза ожидания клёва — ТОЛЬКО в зонах."""
        try:
            self._debug_counter += 1
            
            if self._debug_counter == 1:
                self.engine._log("🔧 HOOK: первый вход", category="Поплавок")
            
            frame = self.engine.display.get_frame()
            if frame is None:
                if self._debug_counter % 20 == 0:
                    self.engine._log("⚠️ HOOK: нет кадра", category="Поплавок")
                return "HOOK"

            cursor_pos = self.engine.cursor_monitor.detect(frame)
            if not cursor_pos:
                if self._debug_counter % 20 == 0:
                    self.engine._log("⚠️ HOOK: нет курсора", category="Поплавок")
                return "HOOK"

            now = time.time()
            hook_timeout = self.engine.config.get("hook_timeout", 20.0)
            bobber_lost_timeout = self.engine.config.get("bobber_lost_timeout", 5.0)
            hook_initial_delay = self.engine.config.get("hook_initial_delay", 2.0)
            
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
            
            # СТРОГО только в зонах (расширенных в 4 раза)
            float_pos = self._find_bobber_in_zones(frame, cursor_pos, expand_zones=True)
            
            # Отладка каждые 10 кадров
            if self._debug_counter % 10 == 0:
                if float_pos:
                    self.engine._log(f"🔍 [zones] Поплавок: {float_pos}", category="Поплавок")
                else:
                    self.engine._log(f"⚠️ [zones] НЕ найден в зонах", category="Поплавок")
            
            bite_y_threshold = self.engine.config.get("bite_y_threshold", 2)
            bite_x_threshold = self.engine.config.get("bite_x_threshold", 10)
            missing_frames_limit = self.engine.config.get("missing_frames_limit", 1)
            max_x_jump = self.engine.config.get("max_x_jump", 60)
            sink_threshold = self.engine.config.get("sink_threshold", 1)
            sink_frames_needed = self.engine.config.get("sink_frames_needed", 3)
            white_loss_threshold = self.engine.config.get("white_part_loss_threshold", 0.5)
            
            if float_pos:
                self.engine._last_bobber_pos = float_pos
                self._bobber_missing_count = 0
                self._bobber_was_seen_in_hook = True
                self._last_seen_time = now
                
                bx, by = float_pos
                
                # Проверяем белую часть (большая зона)
                zone_size = 120
                half = zone_size // 2
                x1 = max(0, bx - half)
                y1 = max(0, by - half)
                x2 = min(frame.shape[1], bx + half)
                y2 = min(frame.shape[0], by + half)
                zone_crop = frame[y1:y2, x1:x2]
                
                white_pixels = self.engine.float_analyzer.detect_white_part(zone_crop)
                self._white_part_history.append(white_pixels)
                if len(self._white_part_history) > 5:
                    self._white_part_history = self._white_part_history[-5:]
                
                if self._debug_counter % 5 == 0:
                    avg_white = np.mean(self._white_part_history) if self._white_part_history else 0
                    self.engine._log(f"📍 ({bx}, {by}) белых: {white_pixels} (avg: {avg_white:.0f})", category="Поплавок")
                
                # 🎯 КЛЁВ: исчезновение белой части
                if self._last_white_pixels > 10 and white_pixels < self._last_white_pixels * (1 - white_loss_threshold):
                    loss_percent = (1 - white_pixels / self._last_white_pixels) * 100
                    self.engine._log(f"🎯 КЛЁВ! Белая часть -{loss_percent:.0f}% ({self._last_white_pixels}→{white_pixels})", category="Поплавок")
                    self.engine._log("🖱️ Клик ЛКМ → мини-игра", category="Поплавок")
                    self.engine.interactor.quick_tap(0.1)
                    self._reset_hook_state()
                    return "CHALLENGE"
                
                self._last_white_pixels = white_pixels
                
                self._bobber_y_history.append(by)
                if len(self._bobber_y_history) > 10:
                    self._bobber_y_history = self._bobber_y_history[-10:]
                
                if self._last_bobber_y is not None:
                    dy = by - self._last_bobber_y
                    dx = abs(bx - self._last_bobber_x) if self._last_bobber_x is not None else 0
                    
                    if dx > max_x_jump:
                        self.engine._log(f"⚠️ Скачок X: {dx}px", category="Поплавок")
                        self._last_bobber_y = by
                        self._last_bobber_x = bx
                        self._bobber_y_history.clear()
                        self._sink_start_y = None
                        self._sink_frame_count = 0
                        return "HOOK"
                    
                    if self._debug_counter % 3 == 0:
                        self.engine._log(f"📊 dy={dy:.1f} dx={dx} порог={bite_y_threshold}", category="Поплавок")
                    
                    # 🎯 КЛЁВ: резкое движение вниз
                    if dy > bite_y_threshold:
                        self.engine._log(f"🎯 КЛЁВ! Рывок вниз {dy:.1f}px", category="Поплавок")
                        self.engine._log("🖱️ Клик ЛКМ → мини-игра", category="Поплавок")
                        self.engine.interactor.quick_tap(0.1)
                        self._reset_hook_state()
                        return "CHALLENGE"
                    
                    # 🎯 КЛЁВ: резкое движение в сторону
                    if dx > bite_x_threshold:
                        self.engine._log(f"🎯 КЛЁВ! Рывок в сторону {dx}px", category="Поплавок")
                        self.engine._log("🖱️ Клик ЛКМ → мини-игра", category="Поплавок")
                        self.engine.interactor.quick_tap(0.1)
                        self._reset_hook_state()
                        return "CHALLENGE"
                    
                    # 🎯 КЛЁВ: плавное погружение
                    if dy >= sink_threshold:
                        if self._sink_start_y is None:
                            self._sink_start_y = self._last_bobber_y
                            self._sink_frame_count = 1
                        else:
                            self._sink_frame_count += 1
                        
                        total_sink = by - self._sink_start_y
                        if self._sink_frame_count >= sink_frames_needed and total_sink >= sink_threshold * sink_frames_needed:
                            self.engine._log(f"🎯 КЛЁВ! Погружение {total_sink}px/{self._sink_frame_count}кадров", category="Поплавок")
                            self.engine._log("🖱️ Клик ЛКМ → мини-игра", category="Поплавок")
                            self.engine.interactor.quick_tap(0.1)
                            self._reset_hook_state()
                            return "CHALLENGE"
                    else:
                        if dy < 0:
                            self._sink_frame_count = 0
                            self._sink_start_y = None
                
                self._last_bobber_y = by
                self._last_bobber_x = bx
                
            else:
                self._bobber_missing_count += 1
                
                if self._bobber_missing_count % 5 == 0:
                    self.engine._log(f"⚠️ НЕ в зонах ({self._bobber_missing_count} кадров)", category="Поплавок")
                
                # 🎯 КЛЁВ: поплавок исчез из зон
                if self._bobber_was_seen_in_hook and self._bobber_missing_count >= missing_frames_limit:
                    self.engine._log(f"🎯 КЛЁВ! Поплавок ушёл из зон ({self._bobber_missing_count} кадров)", category="Поплавок")
                    self.engine._log("🖱️ Клик ЛКМ → мини-игра", category="Поплавок")
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