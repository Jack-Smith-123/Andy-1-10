"""
Темы оформления Andy-1-3.
Все цвета централизованы здесь.
"""

THEMES = {
    # --- Albion Dark (по умолчанию) ---
    "albion_dark": {
        "name": "🎣 Albion Dark",
        "description": "Тёмная тема в стиле Albion Online",
        "bg_main": "#1a1f2e",
        "bg_panel": "#2a3142",
        "bg_panel_transparent": "#1a1f2e",
        "bg_slider": "#3a4152",
        "bg_button_primary": "#1f6aa5",
        "bg_button_primary_hover": "#1a5a8a",
        "bg_button_secondary": "#2c3e50",
        "bg_button_secondary_hover": "#34495e",
        "bg_button_action": "#1f6aa5",
        "bg_button_action_hover": "#1a5a8a",
        "bg_button_close": "#6c757d",
        "bg_button_close_hover": "#5a6268",
        "text_primary": "#e0e0e0",
        "text_secondary": "#a0a8b8",
        "text_accent": "#d4a843",
        "indicator_on": "#2ecc71",
        "indicator_off": "#6c757d",
        "status_text": "#a0a8b8",
        "status_active": "#2ecc71",
        "border_color": "#3a4152",
    },

    # --- Midnight Blue ---
    "midnight_blue": {
        "name": "🌙 Midnight Blue",
        "description": "Глубокий синий с холодными акцентами",
        "bg_main": "#0f1923",
        "bg_panel": "#1a2733",
        "bg_panel_transparent": "#0f1923",
        "bg_slider": "#243442",
        "bg_button_primary": "#2c5f8a",
        "bg_button_primary_hover": "#3a7ab3",
        "bg_button_secondary": "#1e3a52",
        "bg_button_secondary_hover": "#2a4a66",
        "bg_button_action": "#2c5f8a",
        "bg_button_action_hover": "#3a7ab3",
        "bg_button_close": "#4a1f1f",
        "bg_button_close_hover": "#6a2a2a",
        "text_primary": "#d0e0f0",
        "text_secondary": "#8899aa",
        "text_accent": "#5dade2",
        "indicator_on": "#58d68d",
        "indicator_off": "#4a5a6a",
        "status_text": "#8899aa",
        "status_active": "#58d68d",
        "border_color": "#243442",
    },

    # --- Forest Green ---
    "forest_green": {
        "name": "🌲 Forest Green",
        "description": "Зелёная тема в стиле леса",
        "bg_main": "#1a2420",
        "bg_panel": "#2a3530",
        "bg_panel_transparent": "#1a2420",
        "bg_slider": "#3a4540",
        "bg_button_primary": "#4a7c59",
        "bg_button_primary_hover": "#5a9a6a",
        "bg_button_secondary": "#3a5a45",
        "bg_button_secondary_hover": "#4a6a55",
        "bg_button_action": "#4a7c59",
        "bg_button_action_hover": "#5a9a6a",
        "bg_button_close": "#6a2a2a",
        "bg_button_close_hover": "#8a3a3a",
        "text_primary": "#d0e8d8",
        "text_secondary": "#88a898",
        "text_accent": "#7fb069",
        "indicator_on": "#7fb069",
        "indicator_off": "#4a5a50",
        "status_text": "#88a898",
        "status_active": "#7fb069",
        "border_color": "#3a4540",
    },

    # --- 🆕 Earth Brown (на основе Thunar и терминала Linux) ---
    "earth_brown": {
        "name": "🌍 Earth Brown",
        "description": "Тёплые коричневые тона в стиле Thunar и терминала Linux",
        "bg_main": "#2d2a27",
        "bg_panel": "#3a3530",
        "bg_panel_transparent": "#2d2a27",
        "bg_slider": "#4a4540",
        "bg_button_primary": "#8b6f47",
        "bg_button_primary_hover": "#a0825a",
        "bg_button_secondary": "#4a4540",
        "bg_button_secondary_hover": "#5a5550",
        "bg_button_action": "#6b5a3e",
        "bg_button_action_hover": "#8b7a5e",
        "bg_button_close": "#5a3a2a",
        "bg_button_close_hover": "#7a4a3a",
        "text_primary": "#e8e4df",
        "text_secondary": "#a8a29c",
        "text_accent": "#c4956a",
        "indicator_on": "#7fb069",
        "indicator_off": "#6b5a4a",
        "status_text": "#a8a29c",
        "status_active": "#7fb069",
        "border_color": "#5a5550",
    },
}


def get_theme(name):
    """Возвращает тему по имени. Если не найдена — возвращает albion_dark."""
    if name in THEMES:
        return THEMES[name]
    print(f"[THEMES] ⚠ Тема '{name}' не найдена, используется albion_dark")
    return THEMES["albion_dark"]


def get_theme_names():
    """Возвращает список имён тем для отображения в UI."""
    return [THEMES[k]["name"] for k in THEMES]


def get_theme_by_name(display_name):
    """Возвращает ключ темы по её отображаемому имени."""
    for key, data in THEMES.items():
        if data["name"] == display_name:
            return key
    return "albion_dark"
