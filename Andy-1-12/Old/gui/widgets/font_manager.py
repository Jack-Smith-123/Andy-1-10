"""
Менеджер шрифтов Andy-1-3.
Централизованное управление шрифтами для всего приложения.
"""
import customtkinter as ctk


# Доступные семейства шрифтов
AVAILABLE_FONTS = [
    "Arial",
    "Helvetica",
    "Georgia",
    "Times New Roman",
    "Courier New",
    "Consolas",
    "Verdana",
    "Tahoma",
    "Trebuchet MS",
    "Impact",
    "Comic Sans MS",
    "Monospace",
]


class FontManager:
    def __init__(self, config):
        """
        config: словарь конфигурации с настройками шрифтов
        """
        self.config = config
        self._cache = {}
        
        # Настройки по умолчанию
        self.defaults = {
            "font_family": "Arial",
            "font_size_title": 19,
            "font_size_header": 17,
            "font_size_button_primary": 17,
            "font_size_button_secondary": 15,
            "font_size_button_action": 15,
            "font_size_button_close": 15,
            "font_size_label": 14,
            "font_size_value": 14,
            "font_size_status": 13,
            "font_size_tooltip": 13,
            "font_size_log": 13,
            "font_size_preview_fps": 15,
            "font_size_preview_stats": 12,
            "font_size_theme_name": 14,
            "font_size_theme_desc": 11,
            "font_size_section": 15,
            "font_size_slider_label": 14,
        }
    
    def get_font(self, key, weight="normal"):
        """
        Получает шрифт по ключу.
        key: ключ настройки (например, "font_size_title")
        weight: "normal" или "bold"
        """
        cache_key = f"{key}_{weight}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        family = self.config.get("font_family", self.defaults["font_family"])
        size = self.config.get(key, self.defaults.get(key, 13))
        
        font = ctk.CTkFont(family=family, size=size, weight=weight)
        self._cache[cache_key] = font
        return font
    
    def get_family(self):
        """Возвращает текущее семейство шрифта."""
        return self.config.get("font_family", self.defaults["font_family"])
    
    def get_size(self, key):
        """Возвращает размер шрифта по ключу."""
        return self.config.get(key, self.defaults.get(key, 13))
    
    def clear_cache(self):
        """Очищает кэш шрифтов (при смене темы/шрифта)."""
        self._cache.clear()
    
    def update_config(self, key, value):
        """Обновляет настройку шрифта и очищает кэш."""
        self.config[key] = value
        self.clear_cache()
    
    def get_all_sizes(self):
        """Возвращает все настройки размеров шрифтов."""
        return {k: v for k, v in self.defaults.items() if k.startswith("font_size")}
    
    def get_available_fonts(self):
        """Возвращает список доступных шрифтов."""
        return AVAILABLE_FONTS
