"""
Вкладка "Темы" — выбор темы оформления.
"""
import customtkinter as ctk
from .base_panel import BaseTab
from ..widgets.themes import ThemeRow
from ..themes import THEMES


class ThemeTab(BaseTab):
    """Выбор темы оформления приложения."""
    
    def __init__(self, *args, on_theme_editor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_theme_editor = on_theme_editor
        self._theme_var = ctk.StringVar(value=self.config.get("theme", "albion_dark"))
        self._theme_rows = []
        self._build()
    
    def _build(self):
        scroll = self._make_scrollable(self.parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._add_header(scroll, "Тема оформления", "🎨")
        
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