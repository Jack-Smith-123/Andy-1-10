"""
Определение системной темы Linux и генерация палитры.
Поддержка: GNOME (gsettings), KDE (kreadconfig5), GTK_THEME env, settings.ini.
"""
import os
import subprocess


def _run_cmd(cmd):
    """Запускает команду и возвращает stdout или пустую строку."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=2
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _hex_to_rgb(hex_color):
    """'#rrggbb' -> (r, g, b)."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return (128, 128, 128)
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(r, g, b):
    """(r, g, b) -> '#rrggbb'."""
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return f"#{r:02x}{g:02x}{b:02x}"


def _lighten(hex_color, amount):
    r, g, b = _hex_to_rgb(hex_color)
    return _rgb_to_hex(r + amount, g + amount, b + amount)


def _darken(hex_color, amount):
    r, g, b = _hex_to_rgb(hex_color)
    return _rgb_to_hex(r - amount, g - amount, b - amount)


def _detect_dark_mode():
    """Определяет, используется ли тёмный режим в системе."""
    # 1. GNOME 42+: color-scheme
    out = _run_cmd(["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"])
    if out:
        low = out.lower().strip("'\"")
        if "dark" in low:
            return True
        if "light" in low:
            return False

    # 2. GTK_THEME env
    gtk_theme = os.environ.get("GTK_THEME", "").lower()
    if gtk_theme:
        if "dark" in gtk_theme:
            return True
        if "light" in gtk_theme:
            return False

    # 3. settings.ini (gtk-3.0 и gtk-4.0)
    for rel_path in [".config/gtk-3.0/settings.ini", ".config/gtk-4.0/settings.ini"]:
        path = os.path.expanduser(f"~/{rel_path}")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()
                    for line in content.split("\n"):
                        if "gtk-theme" in line:
                            if "dark" in line:
                                return True
                            if "light" in line:
                                return False
            except Exception:
                pass

    # 4. KDE Plasma
    out = _run_cmd(["kreadconfig5", "--group", "General", "--key", "ColorScheme"])
    if out and "dark" in out.lower():
        return True

    # 5. Fallback: тёмная тема (по скриншотам пользователя)
    return True


def _detect_accent_color():
    """Пытается определить акцентный цвет системы."""
    # GNOME 43+: accent-color
    out = _run_cmd(["gsettings", "get", "org.gnome.desktop.interface", "accent-color"])
    if out:
        color = out.strip().strip("'\"")
        if color and len(color) == 7 and color.startswith("#"):
            return color

    # KDE: AccentColor
    out = _run_cmd(["kreadconfig5", "--group", "Colors:Window", "--key", "ForegroundNormal"])
    if out:
        parts = out.strip().split(",")
        if len(parts) == 3:
            try:
                r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
                return _rgb_to_hex(r, g, b)
            except Exception:
                pass

    return None


def detect_system_theme():
    """
    Определяет системную тему Linux и возвращает полную палитру.
    Возвращает dict в формате THEMES.
    """
    is_dark = _detect_dark_mode()
    accent = _detect_accent_color()

    # Если акцент не определился — используем дефолтный для режима
    if not accent:
        accent = "#8b6f47" if is_dark else "#1f6aa5"

    if is_dark:
        return {
            "name": "Системная (тёмная)",
            "description": "Автоопределена из Linux",
            "bg_main": "#2b2b2b",
            "bg_panel": "#353535",
            "bg_panel_transparent": "transparent",
            "bg_button_primary": accent,
            "bg_button_primary_hover": _lighten(accent, 20),
            "bg_button_secondary": "#3d3d3d",
            "bg_button_secondary_hover": "#4a4a4a",
            "bg_button_close": "#6c757d",
            "bg_button_close_hover": "#5a6268",
            "bg_slider": "#404040",
            "text_primary": "#d4d4d4",
            "text_secondary": "#a0a0a0",
            "text_accent": _lighten(accent, 30),
            "indicator_off": "#5a5a5a",
            "indicator_on": "#7fb069",
            "status_text": "#a0a0a0",
            "status_active": "#7fb069",
        }
    else:
        return {
            "name": "Системная (светлая)",
            "description": "Автоопределена из Linux",
            "bg_main": "#f0f0f0",
            "bg_panel": "#ffffff",
            "bg_panel_transparent": "transparent",
            "bg_button_primary": accent,
            "bg_button_primary_hover": _darken(accent, 20),
            "bg_button_secondary": "#e0e0e0",
            "bg_button_secondary_hover": "#d0d0d0",
            "bg_button_close": "#6c757d",
            "bg_button_close_hover": "#5a6268",
            "bg_slider": "#d0d0d0",
            "text_primary": "#2b2b2b",
            "text_secondary": "#666666",
            "text_accent": _darken(accent, 10),
            "indicator_off": "#aaaaaa",
            "indicator_on": "#4a9e3f",
            "status_text": "#666666",
            "status_active": "#4a9e3f",
        }


def apply_system_theme(themes_dict):
    """
    Определяет системную тему, добавляет её в themes_dict под ключом 'system_theme'
    и возвращает ключ.
    """
    palette = detect_system_theme()
    themes_dict["system_theme"] = palette
    print(f"[SYSTEM_THEME] ✓ Определена: {palette['name']} (акцент: {palette['bg_button_primary']})")
    return "system_theme"
