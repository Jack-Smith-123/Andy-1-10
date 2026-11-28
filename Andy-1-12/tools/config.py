"""
Работа с config.json.
Содержит DEFAULT_CONFIG и класс ConfigMixin.
"""
import json
import os


DEFAULT_CONFIG = {
    # === Основные ===
    "match_threshold": 0.62,
    
    # Настройки клёва
    "bite_y_threshold": 2,           # 🆕 Снижено с 3 до 2 (очень чувствительно)
    "bite_x_threshold": 10,          # 🆕 Снижено с 15 до 10
    "missing_frames_limit": 1,       # 🆕 Снижено с 2 до 1 (мгновенная реакция)
    "min_seen_frames": 2,            # 🆕 Снижено с 3 до 2 (быстрее переход в HOOK)
    "hook_timeout": 20.0,
    "bobber_lost_timeout": 5.0,
    "max_x_jump": 60,
    "hook_search_expansion": 1.5,
    
    # Настройки плавного погружения
    "sink_threshold": 1,             # 🆕 Снижено с 2 до 1
    "sink_frames_needed": 3,         # 🆕 Снижено с 5 до 3
    
    # 🆕 Задержка перед началом поиска поплавка
    "hook_initial_delay": 2.0,
    
    # 🆕 Порог белой части (процент от предыдущего кадра)
    "white_part_loss_threshold": 0.5,  # Если белая часть уменьшилась на 50%+

    "bite_window_size": 10,
    "bite_min_seen_frames": 4,
    "bite_missing_frames_limit": 3,
    "bite_max_x_jump": 60,
    "theme": "albion_dark",
    "font_size": 13,
    "font_family": "Arial",

    # === Вода ===
    "water_h_low": 90, "water_h_high": 140,
    "water_s_low": 30, "water_s_high": 255,
    "water_v_low": 30, "water_v_high": 255,
    "water_min_area": 5000,
    "water_blue_ratio": 1.1,
    "water_check_interval": 2.0,

    # === Поплавок (HSV) ===
    "bobber_h_low": 0, "bobber_h_high": 20,
    "bobber_s_low": 100, "bobber_s_high": 255,
    "bobber_v_low": 100, "bobber_v_high": 255,
    "bobber_min_area": 50,
    "bobber_max_area": 2000,

    # === Поиск ===
    "search_radius": 150,
    "search_step": 80,
    "search_zones_count": 5,

    # === Зоны поиска (5 штук) — включение и размер ===
    "zone_1_enabled": True, "zone_1_size": 60,
    "zone_2_enabled": True, "zone_2_size": 60,
    "zone_3_enabled": True, "zone_3_size": 60,
    "zone_4_enabled": True, "zone_4_size": 60,
    "zone_5_enabled": True, "zone_5_size": 60,

    # RGB цвета масок и элементов
    "water_mask_r": 0, "water_mask_g": 255, "water_mask_b": 0,
    "bobber_mask_r": 255, "bobber_mask_g": 0, "bobber_mask_b": 255,
    "zone_mask_r": 127, "zone_mask_g": 66, "zone_mask_b": 127,
    "cursor_mask_r": 0, "cursor_mask_g": 200, "cursor_mask_b": 255,
    
    # 🆕 Цвет линии поиска (желтая по умолчанию)
    "line_mask_r": 255, "line_mask_g": 255, "line_mask_b": 0,
    
    # 🆕 Цвет центра воды (крест + квадрат зоны заброса)
    "water_cross_r": 255, "water_cross_g": 255, "water_cross_b": 0,
    "water_zone_r": 255, "water_zone_g": 255, "water_zone_b": 0,
    
    # 🆕 Цвет рамки поплавка в разных состояниях
    "bobber_found_r": 0, "bobber_found_g": 255, "bobber_found_b": 0,
    "bobber_checking_r": 0, "bobber_checking_g": 200, "bobber_checking_b": 200,
    "bobber_not_found_r": 255, "bobber_not_found_g": 0, "bobber_not_found_b": 0,

    # === Визуал — включение функций для бота ===
    "enable_water": True,
    "enable_cursor": True,
    "enable_zone_search": True,
    "enable_bobber_color": True,

    # === Визуал — отображение в окне Display ===
    "show_water": True,
    "show_zones": True,
    "show_cursor": True,
    "show_bobber_mask": False,

    # === Поиск поплавка ===
    "enable_bobber_search": True,
    "enable_bobber_color": True,
    "enable_bobber_template": True,
    "combine_bobber_methods": False,
    "enable_bobber_hsv": True,

    # === Заброс ===
    "click_delay": 0.5,
    "cast_delay": 4.0,
    "cast_hold_min": 0.8,
    "cast_hold_max": 2.0,
    "cast_hold_jitter": 0.3,
    "hook_delay": 1.0,
    "restart_delay": 2.0,
    "float_timeout": 10.0,
    "max_cast_attempts": 3,

    # === Мини-игра ===
    "mini_game_sensitivity": 0.5,
    "mini_game_max_time": 15.0,

    # === Кадр ===
    "capture_fps": 20,
    "window_title": "Albion Online Client",

    # === Подсказки ===
    "tooltip_delay": 1.0,
}


class ConfigMixin:
    """Миксин для работы с config.json."""

    CONFIG_PATH = "config.json"

    def load_config(self):
        """Загружает конфиг из config.json или создаёт дефолтный."""
        if os.path.exists(self.CONFIG_PATH):
            try:
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self.config = {**DEFAULT_CONFIG, **loaded}
                print("✓ Настройки загружены из config.json")
            except Exception as e:
                print(f"⚠ Ошибка загрузки конфига: {e}. Использую дефолт.")
                self.config = DEFAULT_CONFIG.copy()
        else:
            self.config = DEFAULT_CONFIG.copy()
            self._save_config()

    def _save_config(self):
        """Сохраняет конфиг в config.json."""
        try:
            with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠ Ошибка сохранения конфига: {e}")

    def get(self, key, default=None):
        """Получить значение из конфига."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Установить значение и сохранить."""
        self.config[key] = value
        self._save_config()