"""
Менеджер шрифтов с кэшированием.
"""
import customtkinter as ctk

# Список доступных шрифтов (можно расширить)
AVAILABLE_FONTS = [
    "Arial", "Helvetica", "Times", "Courier", "Verdana",
    "Georgia", "Palatino", "Garamond", "Bookman", "Comic Sans MS",
    "Trebuchet MS", "Arial Black", "Impact"
]


class FontManager:
    """Управляет шрифтами и их кэширует."""

    def __init__(self, config):
        self.config = config
        self._cache = {}

    def get_font(self, key, weight="normal"):
        """Возвращает шрифт по ключу из конфига."""
        cache_key = (key, weight)
        if cache_key in self._cache:
            return self._cache[cache_key]

        size = self.config.get(key, 13)
        family = self.config.get("font_family", "Arial")
        
        # customtkinter использует CTkFont
        font = ctk.CTkFont(family=family, size=int(size), weight=weight)
        self._cache[cache_key] = font
        return font

    def clear_cache(self):
        """Очищает кэш шрифтов (нужно при смене темы/размера)."""
        self._cache.clear()