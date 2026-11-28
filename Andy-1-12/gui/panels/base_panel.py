"""
Базовый класс для всех вкладок настроек.
"""
import customtkinter as ctk


class BaseTab:
    """Базовый класс с общими методами для вкладок."""
    
    def __init__(self, parent, config, on_change_callback=None, font_size=13,
                 theme=None, font_manager=None):
        self.parent = parent
        self.config = config
        self.on_change = on_change_callback
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        
    def _get_font(self, key, weight="normal"):
        """Получить шрифт с учётом менеджера шрифтов."""
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)
    
    def _make_scrollable(self, parent, theme=None):
        """Создать прокручиваемый контейнер."""
        theme = theme or self.theme
        return ctk.CTkScrollableFrame(
            parent,
            fg_color=theme.get("bg_panel", "#2a3142"),
            corner_radius=8,
            scrollbar_button_color=theme.get("bg_slider", "#3a4152"),
            scrollbar_button_hover_color=theme.get("bg_button_secondary_hover", "#34495e"),
        )
    
    def _add_header(self, parent, text, icon=""):
        """Добавить заголовок вкладки."""
        label = ctk.CTkLabel(
            parent, text=f"{icon} {text}" if icon else text,
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        )
        label.pack(anchor="w", padx=10, pady=(10, 10))
        return label
    
    def _add_section(self, parent, text):
        """Добавить заголовок секции."""
        label = ctk.CTkLabel(
            parent, text=text,
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        )
        label.pack(anchor="w", padx=10, pady=(15, 5))
        return label
    
    def build(self):
        """Метод для переопределения в дочерних классах."""
        raise NotImplementedError("Subclasses must implement build()")