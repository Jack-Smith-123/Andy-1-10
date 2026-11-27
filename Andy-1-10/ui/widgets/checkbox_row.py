"""
Виджет строки с чекбоксом.
"""
import customtkinter as ctk
from .hints import Tooltip


class CheckboxRow(ctk.CTkFrame):
    """Строка: Чекбокс + Название + Подсказка."""

    def __init__(self, parent, label_text, config_key, config, theme, 
                 font_manager, on_change=None, tooltip_text=None, tooltip_delay=1.0):
        super().__init__(parent, fg_color=theme.get("bg_main", "#1a1f2e"), corner_radius=6)
        self.config = config
        self.config_key = config_key
        self.on_change = on_change

        # Чекбокс
        self.var = ctk.BooleanVar(value=config.get(config_key, True))
        self.checkbox = ctk.CTkCheckBox(
            self, text="",
            variable=self.var,
            command=self._on_change,
            fg_color=theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=theme.get("bg_button_primary_hover", "#1a5a8a"),
            width=24, height=24
        )
        self.checkbox.pack(side="left", padx=5, pady=5)

        # Название
        lbl = ctk.CTkLabel(
            self, text=label_text,
            font=font_manager.get_font("font_size_label"),
            text_color=theme.get("text_primary", "#e0e0e0"),
            anchor="w"
        )
        lbl.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        # Подсказка
        if tooltip_text:
            Tooltip(lbl, tooltip_text, theme, delay=tooltip_delay)

    def _on_change(self):
        self.config[self.config_key] = self.var.get()
        if self.on_change:
            self.on_change()