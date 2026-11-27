"""
Вкладка "Подсказки" — настройка задержки.
"""
import customtkinter as ctk
from ..widgets.sliders import SliderRow


def _make_scrollable(parent, theme):
    return ctk.CTkScrollableFrame(
        parent,
        fg_color=theme.get("bg_panel", "#2a3142"),
        corner_radius=8,
        scrollbar_button_color=theme.get("bg_slider", "#3a4152"),
        scrollbar_button_hover_color=theme.get("bg_button_secondary_hover", "#34495e"),
    )


class TipsTab:
    def __init__(self, parent, config, font_size=13, theme=None, font_manager=None):
        self.config = config
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="💡 Настройки подсказок",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 10))

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