import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "app": {"font_size": 12, "tooltip_delay": 1000},
    "bot": {"fps": 20},
    "log": {"enabled": True, "max_lines": 1000},
    "zone": {
        "enabled": True,
        "show": True,
        "square_size": 50,
        "distance": 100,
        "color_r": 255,
        "color_g": 255,
        "color_b": 0
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            for k, v in data.items():
                if isinstance(v, dict) and isinstance(merged.get(k), dict):
                    merged[k] = {**merged[k], **v}
                else:
                    merged[k] = v
            return merged
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
