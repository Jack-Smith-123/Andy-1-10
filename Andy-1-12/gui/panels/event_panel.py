"""
Вкладка "Поклевка" — настройки определения поклевки.
"""
from .base_panel import BaseTab
from ..widgets.sliders import SliderRow


class BiteTab(BaseTab):
    """Настройки определения поклевки: движение, белая часть, таймауты."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build()
    
    def _build(self):
        scroll = self._make_scrollable(self.parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._add_header(scroll, "Настройки определения поклевки", "🎯")
        
        # === Движение поплавка ===
        self._add_section(scroll, "Движение поплавка")
        
        items = [
            ("Порог рывка по Y (px)", "bite_y_threshold", 1, 50,
             "Минимальное движение вниз для определения поклевки."),
            ("Порог рывка по X (px)", "bite_x_threshold", 5, 100,
             "Минимальное движение в сторону для определения поклевки."),
            ("Макс. скачок по X (px)", "max_x_jump", 30, 200,
             "Игнорировать слишком большие скачки (защита от помех)."),
            ("Размер окна анализа", "bite_window_size", 3, 20,
             "Сколько кадров анализировать для определения движения."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)
        
        # === Белая часть поплавка ===
        self._add_section(scroll, "Белая часть поплавка")
        
        items = [
            ("Порог потери белой части", "white_part_loss_threshold", 0.3, 0.9,
             "На сколько должна уменьшиться белая часть (0.5 = 50%)."),
            ("Мин. белых пикселей", "bobber_white_threshold", 100, 255,
             "Порог яркости для определения белой части."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)
        
        # === Потеря поплавка ===
        self._add_section(scroll, "Потеря поплавка")
        
        items = [
            ("Лимит пропущенных кадров", "missing_frames_limit", 1, 10,
             "Сколько кадров поплавок может отсутствовать перед реакцией."),
            ("Лимит пропущенных (поклевка)", "bite_missing_frames_limit", 1, 10,
             "Альтернативный лимит для фазы ожидания поклевки."),
            ("Мин. кадров с поплавком", "min_seen_frames", 1, 10,
             "Сколько кадров поплавок должен быть виден перед анализом."),
            ("Мин. кадров (поклевка)", "bite_min_seen_frames", 1, 10,
             "Альтернативный лимит для фазы ожидания поклевки."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)
        
        # === Таймауты ===
        self._add_section(scroll, "Таймауты")
        
        items = [
            ("Таймаут ожидания поклевки (с)", "hook_timeout", 5.0, 60.0,
             "Максимальное время ожидания поклевки."),
            ("Таймаут потери поплавка (с)", "bobber_lost_timeout", 2.0, 15.0,
             "Сколько ждать после потери поплавка перед перезапуском."),
            ("Задержка после заброса (с)", "hook_initial_delay", 0.5, 10.0,
             "Пауза перед началом анализа поклевки."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)