"""
Конфигурация Andy-1-3 (рыбалка). Загрузка/сохранение JSON.
"""
import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    # --- Окно ---
    "window_title_hint": "Albion Online Client",
    # --- Шаблоны поплавков ---
    "bobber_water_path": "templates/bobber_in_water.png",
    "bobber_minigame_path": "templates/bobber_minigame.png",
    # --- Пороги рыбалки ---
    "match_threshold": 0.62,
    "bite_y_threshold": 7,
    "missing_frames_limit": 4,
    "min_seen_frames": 4,
    "max_x_jump": 80,
    # --- Зоны мини-игры ---
    "minigame_pull_x": 130,
    "minigame_release_x": 158,
    # --- Захват / FPS ---
    "capture_fps": 20,
    "bot_fps": 20,
    # --- Человечность ---
    "miss_chance": 0.15,
    "cast_hold_min": 0.4,
    "cast_hold_max": 1.2,
    "idle_jitter_enabled": True,
    # --- Горячая клавиша ---
    "hotkey_toggle": "f1",
    # --- Отладка ---
    "debug_vision": False,
    "font_size": 13,
    # --- 🆕 Детект воды ---
    "water_threshold_percent": 8.0,
    "water_check_interval": 2.0,
    "water_h_min": 95,
    "water_h_max": 135,
    "water_s_min": 30,
    "water_v_min": 30,
    "water_v_max": 220,
    "water_blue_red_diff": 20,
    "water_exclude_center_radius": 150,
}


class ConfigMixin:
    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                config = DEFAULT_CONFIG.copy()
                for key, value in loaded.items():
                    clean = key.strip()
                    if clean in DEFAULT_CONFIG:
                        config[clean] = value
                    else:
                        print(f"⚠ Неизвестный ключ (пропущен): '{key}'")
                print(f"✓ Настройки загружены из {CONFIG_FILE}")
                return config
            except Exception as e:
                print(f"⚠ Не удалось загрузить настройки: {e}")
        return DEFAULT_CONFIG.copy()

    def _save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠ Не удалось сохранить настройки: {e}")
