"""
Вкладка "Темы" — выбор темы оформления.
"""
import customtkinter as ctk
from ..themes import THEMES
from ..widgets.themes import ThemeRow


def _make_scrollable(parent, theme):
    return ctk.CTkScrollableFrame(
        parent,
        fg_color=theme.get("bg_panel", "#2a3142"),
        corner_radius=8,
        scrollbar_button_color=theme.get("bg_slider", "#3a4152"),
        scrollbar_button_hover_color=theme.get("bg_button_secondary_hover", "#34495e"),
    )


class ThemeTab:
    def __init__(self, parent, config, font_size=13, theme=None, font_manager=None,
                 on_theme_editor=None):
        self.config = config
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self.on_theme_editor = on_theme_editor
        self._theme_var = ctk.StringVar(value=config.get("theme", "albion_dark"))
        self._theme_rows = []
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="🎨 Тема оформления",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 10))

        themes_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        themes_frame.pack(fill="x", padx=10)

        self._rebuild_theme_list(themes_frame)

        if self.on_theme_editor:
            ctk.CTkButton(
                scroll, text="✨ Создать свою тему",
                font=self._get_font("font_size_button_primary", "bold"),
                height=40,
                fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
                hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
                text_color=self.theme.get("text_primary", "#e0e0e0"),
                command=self.on_theme_editor
            ).pack(pady=15, padx=10, fill="x")

    def _rebuild_theme_list(self, parent):
        for row in self._theme_rows:
            row.destroy()
        self._theme_rows.clear()

        for theme_key, theme_data in THEMES.items():
            row = ThemeRow(
                parent, theme_key, theme_data,
                self._theme_var, self._on_theme_selected,
                self.font_manager, self.theme, self.font_size
            )
            row.pack(fill="x", pady=4)
            self._theme_rows.append(row)

    def _on_theme_selected(self, theme_key):
        self.config["theme"] = theme_key

    def get_pending_theme(self):
        return self._theme_var.get()