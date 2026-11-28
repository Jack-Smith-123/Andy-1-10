"""
Вкладка "Анти-чит" — имитация человеческого поведения.
"""
from .base_panel import BaseTab
from ..widgets.sliders import SliderRow
from ..widgets.checkbox_row import CheckboxRow


class AntiCheatTab(BaseTab):
    """Настройки для имитации человеческого поведения."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build()
    
    def _build(self):
        scroll = self._make_scrollable(self.parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._add_header(scroll, "Имитация человеческого поведения", "🤖")
        
        # === FPS и производительность ===
        self._add_section(scroll, "Производительность")
        
        items = [
            ("FPS бота", "bot_fps", 5, 60,
             "Частота обработки кадров (меньше = менее заметно)."),
            ("FPS захвата", "capture_fps", 5, 60,
             "Частота захвата экрана."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)
        
        # === Вероятности ===
        self._add_section(scroll, "Вероятности")
        
        items = [
            ("Вероятность пропуска", "miss_chance", 0.0, 0.5,
             "Шанс пропустить поклевку (0.15 = 15%)."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)
        
        CheckboxRow(
            scroll, "Включить джиттер", "idle_jitter_enabled",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Добавлять случайные задержки между действиями.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)
        
        # === Джиттер ===
        self._add_section(scroll, "Параметры джиттера")
        
        items = [
            ("Мин. серия джиттера (с)", "jitter_burst_min", 0.1, 5.0,
             "Минимальная длительность серии случайных действий."),
            ("Макс. серия джиттера (с)", "jitter_burst_max", 0.5, 10.0,
             "Максимальная длительность серии случайных действий."),
            ("Мин. пауза (с)", "jitter_pause_min", 0.5, 10.0,
             "Минимальная пауза между сериями."),
            ("Макс. пауза (с)", "jitter_pause_max", 2.0, 30.0,
             "Максимальная пауза между сериями."),
            ("Шанс джиттера", "jitter_burst_chance", 0.1, 0.9,
             "Вероятность включения джиттера (0.4 = 40%)."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)