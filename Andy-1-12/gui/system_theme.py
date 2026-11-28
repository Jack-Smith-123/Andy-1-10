"""
Определение системной темы Linux.
"""
import os


def detect_system_theme():
    """Пытается определить системную тему (GNOME/KDE)."""
    # GNOME
    try:
        import subprocess
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            theme = result.stdout.strip().strip("'\"")
            if "dark" in theme.lower():
                return "dark"
            return "light"
    except Exception:
        pass

    # KDE / settings.ini fallback
    settings_ini = os.path.expanduser("~/.config/gtk-3.0/settings.ini")
    if os.path.exists(settings_ini):
        try:
            with open(settings_ini, "r") as f:
                content = f.read().lower()
                if "dark" in content:
                    return "dark"
                if "light" in content:
                    return "light"
        except Exception:
            pass

    return "dark"  # По умолчанию тёмная