"""
Вкладка "Общее" — основные настройки бота.
"""
from .base_panel import BaseTab
from ..widgets.sliders import SliderRow


class GeneralTab(BaseTab):
    """Общие настройки: таймауты, FPS, производительность."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build()
    
    def _build(self):
        scroll = self._make_scrollable(self.parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._add_header(scroll, "Общие настройки", "⚙")
        
        items = [
            ("FPS бота", "bot_fps", 5, 60,
             "Частота обработки кадров (меньше = менее заметно для анти-чита)."),
            ("FPS захвата", "capture_fps", 5, 60,
             "Частота захвата экрана."),
            ("Порог совпадения", "match_threshold", 0.30, 0.95,
             "Минимальное совпадение шаблона (0.30-0.95). Чем выше — тем строже поиск."),
            ("Задержка клика (с)", "click_delay", 0.05, 3.0,
             "Пауза между кликами мыши."),
            ("Задержка заброса (с)", "cast_delay", 0.5, 10.0,
             "Время ожидания после заброса удочки."),
            ("Задержка подсечки (с)", "hook_delay", 0.05, 3.0,
             "Пауза перед подсечкой после обнаружения клёва."),
            ("Задержка перезапуска (с)", "restart_delay", 0.5, 5.0,
             "Пауза перед новым забросом после завершения рыбалки."),
            ("Таймаут поплавка (с)", "float_timeout", 3.0, 30.0,
             "Максимальное время ожидания появления поплавка."),
            ("Макс. попыток заброса", "max_cast_attempts", 1, 20,
             "Сколько раз пытаться забросить удочку перед остановкой."),
        ]
        
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)
        
        # Секция "Задержка подсказок"
        self._add_section(scroll, "Интерфейс")
        
        SliderRow(
            scroll, "Задержка подсказок (с)", "tooltip_delay", 0.1, 5.0,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Время задержки перед показом подсказки при наведении."
        ).pack(fill="x", padx=10, pady=3)