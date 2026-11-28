"""
Вкладка "Приложение" — содержит подвкладки Темы/Шрифты/Подсказки.
"""
import customtkinter as ctk
from .theme_tab import ThemeTab
from .font_tab import FontTab
from .tips_tab import TipsTab


class AppTab:
    def __init__(self, parent, config, font_size=13, theme=None, font_manager=None,
                 on_theme_editor=None):
        self.config = config
        self.font_size = font_size
        self.theme = theme or {}
        self.font_manager = font_manager
        self.on_theme_editor = on_theme_editor
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        tabs_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tabs_frame.pack(fill="x", padx=0, pady=0)

        self.inner_switcher = ctk.CTkSegmentedButton(
            tabs_frame,
            values=["Темы", "Шрифты", "Подсказки"],
            command=self._switch_inner_tab,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            selected_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            selected_hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            unselected_color=self.theme.get("bg_slider", "#3a4152"),
            unselected_hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            corner_radius=8,
            border_width=0,
            font=self._get_font("font_size_button_secondary", "bold")
        )
        self.inner_switcher.pack(side="left", padx=10, pady=5)

        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.themes_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.fonts_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.tips_frame = ctk.CTkFrame(content_frame, fg_color="transparent")

        self.theme_tab = ThemeTab(
            self.themes_frame, self.config, self.font_size, self.theme,
            self.font_manager, on_theme_editor=self.on_theme_editor
        )
        self.font_tab = FontTab(
            self.fonts_frame, self.config, self.font_size, self.theme, self.font_manager
        )
        self.tips_tab = TipsTab(
            self.tips_frame, self.config, self.font_size, self.theme, self.font_manager
        )

        self._switch_inner_tab("Темы")

    def _switch_inner_tab(self, name):
        self.themes_frame.pack_forget()
        self.fonts_frame.pack_forget()
        self.tips_frame.pack_forget()
        if name == "Темы":
            self.themes_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "Шрифты":
            self.fonts_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "Подсказки":
            self.tips_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def get_pending_theme(self):
        return self.theme_tab.get_pending_theme()

    def get_pending_font_family(self):
        return self.font_tab.get_pending_font_family()