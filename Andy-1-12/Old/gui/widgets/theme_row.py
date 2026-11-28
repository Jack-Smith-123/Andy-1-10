"""
Строка темы: "Радиокнопка + Название + Палитра из 5 цветов".
Шрифты через FontManager.
"""
import customtkinter as ctk


class ThemeRow:
    def __init__(self, parent, theme_key, theme_data, theme_var, on_select_callback,
                 font_size=13, theme=None, font_manager=None):
        self.theme_key = theme_key
        self.theme_data = theme_data
        self.theme_var = theme_var
        self.on_select = on_select_callback
        self.font_size = font_size
        self.current_theme = theme or {}
        self.font_manager = font_manager

        self.frame = ctk.CTkFrame(parent, fg_color=self.current_theme.get("bg_panel", "#2a3142"))
        self.frame.pack(pady=3, padx=5, fill="x")

        self.radio = ctk.CTkRadioButton(
            self.frame, text="",
            variable=theme_var, value=theme_key,
            command=lambda: on_select_callback(theme_key),
            fg_color=self.current_theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=self.current_theme.get("bg_button_primary_hover", "#1a5a8a"),
        )
        self.radio.pack(side="left", padx=(10, 2), pady=8)

        self.name_label = ctk.CTkLabel(
            self.frame, text=theme_data.get("name", theme_key),
            font=self._get_font("font_size_theme_name", "bold"),
            text_color=self.current_theme.get("text_primary", "#e0e0e0")
        )
        self.name_label.pack(side="left", padx=(0, 5))

        palette_frame = ctk.CTkFrame(self.frame, fg_color="transparent", width=110, height=28)
        palette_frame.pack(side="right", padx=10, pady=5)
        palette_frame.pack_propagate(False)

        palette_colors = [
            theme_data.get("bg_main", "#1a1f2e"),
            theme_data.get("bg_panel", "#2a3142"),
            theme_data.get("bg_button_primary", "#1f6aa5"),
            theme_data.get("text_accent", "#d4a843"),
            theme_data.get("indicator_on", "#4ade80"),
        ]

        self.squares = []
        for color in palette_colors:
            sq = ctk.CTkFrame(palette_frame, width=18, height=18, fg_color=color, corner_radius=3)
            sq.pack(side="left", padx=1)
            self.squares.append(sq)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def destroy(self):
        self.frame.destroy()
