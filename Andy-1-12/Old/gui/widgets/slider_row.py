"""
Строка "Метка + Поле ввода" для настроек.
Без ползунка — только числовой ввод. Любые числа без ограничений.
"""
import customtkinter as ctk
from .tooltip import Tooltip

class SliderRow:
    def __init__(self, parent, label, key, from_, to, steps, default,
                 fmt="{:.2f}", cast=float, instant=False,
                 on_change_callback=None, tooltip_text="", theme=None,
                 font_size=14, font_manager=None):
        self.key = key
        self.cast = cast
        self.instant = instant
        self.on_change = on_change_callback
        self.theme = theme or {}
        self.font_size = font_size
        self.font_manager = font_manager
        self.from_ = from_
        self.to = to
        self.fmt = fmt

        # === Общий фрейм строки ===
        self.frame = ctk.CTkFrame(parent, fg_color=self.theme.get("bg_panel_transparent", "transparent"))
        self.frame.pack(pady=4, padx=10, fill="x")

        # === Метка (слева) ===
        self.label = ctk.CTkLabel(
            self.frame, text=label,
            font=self._get_font("font_size_slider_label"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            anchor="w"
        )
        self.label.pack(side="left", padx=(0, 8))
        if tooltip_text:
            Tooltip(self.label, tooltip_text, theme=self.theme, font_manager=self.font_manager)

        # === Поле ввода (справа, фиксированная ширина) ===
        self.entry = ctk.CTkEntry(
            self.frame, width=70, height=28,
            font=self._get_font("font_size_value"),
            fg_color=self.theme.get("bg_slider", "#3a4152"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            border_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            border_width=1,
            corner_radius=5,
            justify="right"
        )
        self.entry.insert(0, fmt.format(default))
        self.entry.pack(side="right", padx=0)
        self.entry.bind("<Return>", self._on_entry_submit)
        self.entry.bind("<FocusOut>", self._on_entry_submit)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _on_entry_submit(self, event=None):
        """Обработка ввода числа вручную — БЕЗ ограничений."""
        try:
            value = self.cast(self.entry.get())
            # 🆕 Никаких ограничений — принимаем любое число
            self._update_display(value)
            if hasattr(self, '_config_dict'):
                self._config_dict[self.key] = value
            if self.on_change and self.instant:
                self.on_change(self.key, value)
        except (ValueError, TypeError):
            # Если введено не число — восстанавливаем текущее значение
            if hasattr(self, '_config_dict') and self.key in self._config_dict:
                current = self._config_dict[self.key]
            else:
                current = self.cast(self.from_)
            self._update_display(current)

    def set_value(self, value):
        self._update_display(value)

    def _update_display(self, value):
        """Обновляет поле ввода."""
        formatted = self.fmt.format(value)
        self.entry.delete(0, "end")
        self.entry.insert(0, formatted)

    def get_value(self):
        """Возвращает текущее значение из поля ввода (или из конфига)."""
        if hasattr(self, '_config_dict') and self.key in self._config_dict:
            return self._config_dict[self.key]
        try:
            return self.cast(self.entry.get())
        except (ValueError, TypeError):
            return self.cast(self.from_)

    def bind_change(self, config_dict):
        self._config_dict = config_dict
        pass
