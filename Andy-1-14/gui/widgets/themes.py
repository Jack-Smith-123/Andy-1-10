"""
Виджет строки выбора темы.
"""
import customtkinter as ctk


class ThemeRow(ctk.CTkFrame):
    """Строка: Радиокнопка + Название темы + Палитра."""

    def __init__(self, parent, theme_key, theme_data, selected_var, 
                 on_select, font_manager, theme, font_size=13):
        super().__init__(parent, fg_color="transparent")
        self.theme_key = theme_key
        
        # Радиокнопка
        self.radio = ctk.CTkRadioButton(
            self, text="", variable=selected_var, value=theme_key,
            command=lambda: on_select(theme_key),
            fg_color=theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=theme.get("bg_button_primary_hover", "#1a5a8a")
        )
        self.radio.pack(side="left", padx=(0, 10))

        # Название
        ctk.CTkLabel(
            self, text=theme_data.get("name", theme_key),
            font=font_manager.get_font("font_size_theme_name", "bold"),
            text_color=theme.get("text_primary", "#e0e0e0"),
            anchor="w"
        ).pack(side="left", padx=(0, 15))

        # Палитра (цветные квадратики)
        palette_frame = ctk.CTkFrame(self, fg_color="transparent")
        palette_frame.pack(side="left")
        
        colors = [
            theme_data.get("bg_main", "#1a1f2e"),
            theme_data.get("bg_button_primary", "#1f6aa5"),
            theme_data.get("text_accent", "#d4a843"),
            theme_data.get("indicator_on", "#4ade80"),
        ]
        for color in colors:
            ctk.CTkFrame(
                palette_frame, width=16, height=16,
                fg_color=color, corner_radius=3
            ).pack(side="left", padx=2)