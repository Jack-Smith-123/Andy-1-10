"""
Вкладка "Подсказки" — настройки подсказок.
"""
import customtkinter as ctk
from .base_panel import BaseTab
from ..widgets.sliders import SliderRow


class TipsTab(BaseTab):
    """Настройки отображения подсказок."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build()
    
    def _build(self):
        scroll = self._make_scrollable(self.parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._add_header(scroll, "Настройки подсказок", "💡")
        
        SliderRow(
            scroll, "Задержка показа (сек)", "tooltip_delay", 0.1, 5.0,
            self.config, self.theme, self.font_manager,
            tooltip_text="Время задержки перед показом подсказки."
        ).pack(fill="x", padx=10, pady=3)
        
        ctk.CTkLabel(
            scroll,
            text="Подсказки появляются при наведении курсора на любую настройку.\n"
                 "Они исчезают при уходе курсора или клике.",
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_secondary", "#a0a8b8"),
            justify="left"
        ).pack(anchor="w", padx=10, pady=(20, 10))