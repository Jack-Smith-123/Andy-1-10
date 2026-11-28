"""
Вкладка "Мини-игра" — настройки прохождения мини-игры.
"""
from .base_panel import BaseTab
from ..widgets.sliders import SliderRow


class MiniGameTab(BaseTab):
    """Настройки прохождения мини-игры после поклевки."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build()
    
    def _build(self):
        scroll = self._make_scrollable(self.parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._add_header(scroll, "Настройки мини-игры", "🎮")
        
        # === Чувствительность ===
        self._add_section(scroll, "Чувствительность")
        
        items = [
            ("Чувствительность", "mini_game_sensitivity", 0.1, 3.0,
             "Скорость реакции в мини-игре."),
            ("Скорость движения", "mini_game_move_speed", 0.1, 2.0,
             "Скорость перемещения курсора."),
            ("Допуск центра (px)", "mini_game_center_tolerance", 5, 50,
             "Допустимое отклонение от центра."),
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
            ("Макс. время мини-игры (с)", "mini_game_max_time", 5.0, 60.0,
             "Максимальное время на прохождение мини-игры."),
            ("Таймаут мини-игры (с)", "mini_game_timeout", 5.0, 30.0,
             "Альтернативный таймаут мини-игры."),
            ("Таймаут потери (с)", "minigame_lost_timeout", 0.5, 5.0,
             "Время реакции на потерю в мини-игре."),
            ("Макс. длительность (с)", "minigame_max_duration", 5.0, 30.0,
             "Максимальная длительность одной попытки."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)
        
        # === Позиции ===
        self._add_section(scroll, "Позиции кликов")
        
        items = [
            ("X для вытягивания", "minigame_pull_x", 0, 500,
             "Позиция X для вытягивания рыбы."),
            ("X для отпускания", "minigame_release_x", 0, 500,
             "Позиция X для отпускания."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)