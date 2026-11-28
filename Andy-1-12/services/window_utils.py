"""
Поиск окна игры (Albion Online Client) в Linux/X11.
Основной путь: wmctrl + xwininfo. Fallback: xdotool.
Возвращает dict {left, top, width, height, id, title} или None.
"""
import re
import subprocess

# Подсказка заголовка окна — можно переопределить из конфига
DEFAULT_TITLE_HINT = "Albion Online Client"


def _run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout
    except Exception:
        return ""


def _find_by_wmctrl(title_hint):
    """wmctrl -l -> найти ID -> xwininfo -> геометрия."""
    out = _run(["wmctrl", "-l"])
    if not out:
        return None
    window_id, window_title = None, ""
    for line in out.splitlines():
        if title_hint.lower() in line.lower():
            window_id = line.split()[0]
            parts = line.split(None, 3)
            if len(parts) > 3:
                window_title = parts[3]
            break
    if not window_id:
        return None

    info = _run(["xwininfo", "-id", window_id])
    x = re.search(r"Absolute upper-left X:\s+(-?\d+)", info)
    y = re.search(r"Absolute upper-left Y:\s+(-?\d+)", info)
    w = re.search(r"Width:\s+(\d+)", info)
    h = re.search(r"Height:\s+(\d+)", info)
    if not all([x, y, w, h]):
        return None
    return {
        "left": int(x.group(1)), "top": int(y.group(1)),
        "width": int(w.group(1)), "height": int(h.group(1)),
        "id": window_id, "title": window_title,
    }


def _find_by_xdotool(title_hint):
    """Fallback через xdotool search."""
    out = _run(["xdotool", "search", "--name", title_hint])
    if not out.strip():
        return None
    win_id = out.strip().splitlines()[0]
    geo = _run(["xdotool", "getwindowgeometry", "--shell", win_id])
    x = re.search(r"X=(-?\d+)", geo)
    y = re.search(r"Y=(-?\d+)", geo)
    w = re.search(r"WIDTH=(\d+)", geo)
    h = re.search(r"HEIGHT=(\d+)", geo)
    if not all([x, y, w, h]):
        return None
    return {
        "left": int(x.group(1)), "top": int(y.group(1)),
        "width": int(w.group(1)), "height": int(h.group(1)),
        "id": win_id, "title": title_hint,
    }


def find_game_window(title_hint=None):
    hint = title_hint or DEFAULT_TITLE_HINT
    geo = _find_by_wmctrl(hint) or _find_by_xdotool(hint)
    if geo:
        print(f"✓ Окно найдено: '{geo['title']}' "
              f"{geo['width']}x{geo['height']} @ ({geo['left']}, {geo['top']})")
        return geo
    print(f"❌ Окно '{hint}' не найдено. Проверь, что игра запущена "
          f"и wmctrl/xdotool установлены.")
    return None


if __name__ == "__main__":
    print(find_game_window())