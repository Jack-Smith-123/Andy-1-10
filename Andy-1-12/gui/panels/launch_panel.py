"""
Вкладка "Заброс" — настройки механики заброса удочки.
"""
from .base_panel import BaseTab
from ..widgets.sliders import SliderRow


class CastTab(BaseTab):
    """Настройки удержания кнопки мыши и задержек при забросе."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build()
    
    def _build(self):
        scroll = self._make_scrollable(self.parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._add_header(scroll, "Настройки заброса", "🎣")
        
        # === Удержание мыши ===
        self._add_section(scroll, "Удержание кнопки мыши")
        
        items = [
            ("Мин. время удержания (с)", "cast_hold_min", 0.5, 5.0,
             "Минимальное время удержания ЛКМ при забросе."),
            ("Макс. время удержания (с)", "cast_hold_max", 1.0, 10.0,
             "Максимальное время удержания ЛКМ при забросе."),
            ("Джиттер удержания (с)", "cast_hold_jitter", 0.0, 1.0,
             "Случайное отклонение от времени удержания (для имитации человека)."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)
        
        # === Задержки ===
        self._add_section(scroll, "Задержки")
        
        items = [
            ("Задержка перед забросом (с)", "cast_delay", 0.5, 10.0,
             "Пауза перед началом заброса."),
            ("Задержка клика (с)", "click_delay", 0.05, 2.0,
             "Пауза между кликами мыши."),
            ("Задержка подсечки (с)", "hook_delay", 0.05, 2.0,
             "Пауза перед подсечкой после обнаружения поклевки."),
            ("Задержка перезапуска (с)", "restart_delay", 0.5, 5.0,
             "Пауза перед новым забросом после завершения рыбалки."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)
        
        # === Попытки ===
        self._add_section(scroll, "Попытки и таймауты")
        
        items = [
            ("Макс. попыток заброса", "max_cast_attempts", 1, 20,
             "Сколько раз пытаться забросить удочку перед остановкой."),
            ("Таймаут поплавка (с)", "float_timeout", 3.0, 30.0,
             "Максимальное время ожидания появления поплавка."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)