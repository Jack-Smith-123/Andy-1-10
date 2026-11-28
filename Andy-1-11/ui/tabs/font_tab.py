"""
Вкладка "Шрифты" — семейство + превью + размеры.
"""
import customtkinter as ctk
from ..widgets.sliders import SliderRow
from ..widgets.fonts import AVAILABLE_FONTS


def _make_scrollable(parent, theme):
    return ctk.CTkScrollableFrame(
        parent,
        fg_color=theme.get("bg_panel", "#2a3142"),
        corner_radius=8,
        scrollbar_button_color=theme.get("bg_slider", "#3a4152"),
        scrollbar_button_hover_color=theme.get("bg_button_secondary_hover", "#34495e"),
    )


class FontTab:
    def __init__(self, parent, config, font_size=13, theme=None, font_manager=None):
        self.config = config
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self._family_var = ctk.StringVar(value=config.get("font_family", "Arial"))
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Верхняя часть: семейство слева + превью справа
        top_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=(10, 10))

        left = ctk.CTkFrame(top_frame, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left, text="🔤 Семейство шрифта",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", pady=(0, 5))

        ctk.CTkOptionMenu(
            left,
            variable=self._family_var,
            values=AVAILABLE_FONTS,
            width=200, height=32,
            fg_color=self.theme.get("bg_button_secondary", "#2c3e50"),
            button_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=lambda v: self._update_preview()
        ).pack(anchor="w")

        # Превью справа
        right = ctk.CTkFrame(top_frame, fg_color=self.theme.get("bg_panel", "#2a3142"),
                             corner_radius=6, width=180, height=80)
        right.pack(side="right", padx=(10, 0))
        right.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(
            right, text="Пример текста\nAa Бб 0123",
            font=self._get_font("font_size_header", "normal"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            justify="center"
        )
        self.preview_label.pack(expand=True)

        # Размеры шрифтов
        ctk.CTkLabel(
            scroll, text="📏 Размеры шрифтов",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        font_keys = [
            ("Заголовок окна", "font_size_title", 12, 30),
            ("Заголовок в шапке", "font_size_header", 12, 30),
            ("Заголовки секций", "font_size_section", 12, 30),
            ("Основные кнопки", "font_size_button_primary", 12, 30),
            ("Вторичные кнопки", "font_size_button_secondary", 12, 30),
            ("Метки", "font_size_label", 10, 24),
            ("Значения", "font_size_value", 10, 24),
            ("Статус", "font_size_status", 10, 24),
            ("Лог", "font_size_log", 10, 24),
        ]
        for label, key, mn, mx in font_keys:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager,
                tooltip_text=f"Размер шрифта: {label}",
                tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=2)

    def _update_preview(self):
        """Обновляет превью при смене семейства."""
        family = self._family_var.get()
        size = self.config.get("font_size_header", 16)
        self.preview_label.configure(
            font=ctk.CTkFont(family=family, size=int(size))
        )

    def get_pending_font_family(self):
        return self._family_var.get()