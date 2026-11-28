"""
Конфигурация Andy-1.8 (рыбалка). Загрузка/сохранение JSON.
"""
import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    # --- Окно ---
    "window_title_hint": "Albion Online Client",

    # --- Шаблоны поплавков ---
    "bobber_water_dir": "templates/bobber_in_water",
    "bobber_minigame_dir": "templates/bobber_minigame",
    "bobber_max_templates": 10,
    "bobber_log_best_match": True,
    "bobber_search_width": 150,
    "bobber_water_path": "templates/bobber_in_water.png",
    "bobber_minigame_path": "templates/bobber_minigame.png",

    # --- Цветовой детектор поплавка (RGB) ---
    "bobber_red_min": 120,
    "bobber_green_max": 90,
    "bobber_blue_max": 90,
    "bobber_white_threshold": 180,
    "bobber_min_area": 20,
    "bobber_exclude_radius": 150,
    "bobber_exclude_offset_x": 0,
    "bobber_exclude_offset_y": -60,
    "bobber_require_both_colors": False,

    # --- HSV детектор поплавка ---
    "bobber_hsv_enabled": True,
    "bobber_h_min": 0,
    "bobber_h_max": 25,
    "bobber_s_min": 60,
    "bobber_s_max": 255,
    "bobber_v_min": 60,
    "bobber_v_max": 255,

    # --- Настройки поиска поплавка ---
    "bobber_template_search_enabled": True,
    "bobber_cursor_zone_enabled": True,
    "bobber_cursor_zone_radius": 150,
    "bobber_line_search_enabled": True,
    "bobber_line_search_width": 150,
    "bobber_color_validation_enabled": True,
    "bobber_match_threshold": 0.62,
    "bobber_bite_y_threshold": 7,

    # --- Пороги рыбалки (общие) ---
    "match_threshold": 0.62,
    "bite_y_threshold": 7,
    "missing_frames_limit": 4,
    "min_seen_frames": 4,
    "max_x_jump": 80,

    # --- Зоны мини-игры ---
    "minigame_pull_x": 130,
    "minigame_release_x": 158,

    # --- Зона клика по воде ---
    "water_click_radius": 40,

    # --- Заброс ---
    "cast_hold_min": 0.8,
    "cast_hold_max": 2.0,
    "cast_hold_jitter": 0.3,

    # --- Поведение при старте ---
    "bobber_skip_cast_if_present": True,
    "hook_timeout": 15.0,
    "bobber_lost_timeout": 8.0,
    "hook_initial_delay": 6.0,

    # --- Мини-игра ---
    "minigame_lost_timeout": 1.0,
    "minigame_max_duration": 12.0,

    # --- Режимное поведение мыши ---
    "jitter_burst_min": 0.5,
    "jitter_burst_max": 2.0,
    "jitter_pause_min": 1.0,
    "jitter_pause_max": 5.0,
    "jitter_burst_chance": 0.4,

    # --- Захват / FPS ---
    "capture_fps": 20,
    "bot_fps": 20,

    # --- Человечность ---
    "miss_chance": 0.15,
    "idle_jitter_enabled": True,

    # --- Горячая клавиша ---
    "hotkey_toggle": "f1",

    # --- 🆕 Окно превью ---
    "preview_bottom_margin": 60,

    # --- Отладка ---
    "debug_vision": False,
    "font_size": 13,

    # --- Шрифты ---
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

    # --- Тема оформления ---
    "theme": "albion_dark",

    # --- Детект воды ---
    "water_enabled": True,
    "water_threshold_percent": 8.0,
    "water_check_interval": 2.0,
    "water_h_min": 95,
    "water_h_max": 135,
    "water_s_min": 30,
    "water_v_min": 30,
    "water_v_max": 220,
    "water_blue_red_diff": 20,
    "water_exclude_center_radius": 50,

    # --- Визуализация ---
    "vis_water_enabled": True,
    "vis_water_show": True,
    "vis_water_color": "#00ff00",
    "vis_bobber_enabled": True,
    "vis_bobber_show": True,
    "vis_bobber_color": "#ff69ff",
    "vis_zones_show": True,
    "vis_zones_color": "#b400b4",
    "vis_line_show": True,
    "vis_line_color": "#ffff00",
    "vis_cursor_show": True,
    "vis_cursor_color": "#00ffff",
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
        return DEFAULT_CONFIG.copy()

    def _save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠ Не удалось сохранить настройки: {e}")
