"""
Индекс настроек для поиска по окну Options.
Каждая запись: label (что ищем), key (ключ в конфиге), group (группа), tab (вкладка).
"""

SEARCH_INDEX = [
    # === Поведение > Общее ===
    {"label": "FPS бота", "key": "bot_fps", "group": "🎮 Поведение", "tab": "Общее"},
    {"label": "FPS захвата", "key": "capture_fps", "group": "🎮 Поведение", "tab": "Общее"},
    {"label": "Порог совпадения", "key": "match_threshold", "group": "🎮 Поведение", "tab": "Общее"},
    {"label": "Задержка клика", "key": "click_delay", "group": "🎮 Поведение", "tab": "Общее"},
    {"label": "Задержка заброса", "key": "cast_delay", "group": "🎮 Поведение", "tab": "Общее"},
    {"label": "Задержка подсечки", "key": "hook_delay", "group": "🎮 Поведение", "tab": "Общее"},
    {"label": "Задержка перезапуска", "key": "restart_delay", "group": "🎮 Поведение", "tab": "Общее"},
    {"label": "Таймаут поплавка", "key": "float_timeout", "group": "🎮 Поведение", "tab": "Общее"},
    {"label": "Макс. попыток заброса", "key": "max_cast_attempts", "group": "🎮 Поведение", "tab": "Общее"},
    {"label": "Задержка подсказок", "key": "tooltip_delay", "group": "🎮 Поведение", "tab": "Общее"},
    # === Поведение > Заброс ===
    {"label": "Мин. время удержания", "key": "cast_hold_min", "group": "🎮 Поведение", "tab": "Заброс"},
    {"label": "Макс. время удержания", "key": "cast_hold_max", "group": "🎮 Поведение", "tab": "Заброс"},
    {"label": "Джиттер удержания", "key": "cast_hold_jitter", "group": "🎮 Поведение", "tab": "Заброс"},
    # === Поведение > Поклёвка ===
    {"label": "Порог рывка по Y", "key": "bite_y_threshold", "group": "🎮 Поведение", "tab": "Поклёвка"},
    {"label": "Порог рывка по X", "key": "bite_x_threshold", "group": "🎮 Поведение", "tab": "Поклёвка"},
    {"label": "Макс. скачок по X", "key": "max_x_jump", "group": "🎮 Поведение", "tab": "Поклёвка"},
    {"label": "Размер окна анализа", "key": "bite_window_size", "group": "🎮 Поведение", "tab": "Поклёвка"},
    {"label": "Порог потери белой части", "key": "white_part_loss_threshold", "group": "🎮 Поведение", "tab": "Поклёвка"},
    {"label": "Мин. белых пикселей", "key": "bobber_white_threshold", "group": "🎮 Поведение", "tab": "Поклёвка"},
    {"label": "Лимит пропущенных кадров", "key": "missing_frames_limit", "group": "🎮 Поведение", "tab": "Поклёвка"},
    {"label": "Мин. кадров с поплавком", "key": "min_seen_frames", "group": "🎮 Поведение", "tab": "Поклёвка"},
    {"label": "Таймаут ожидания поклевки", "key": "hook_timeout", "group": "🎮 Поведение", "tab": "Поклёвка"},
    {"label": "Таймаут потери поплавка", "key": "bobber_lost_timeout", "group": "🎮 Поведение", "tab": "Поклёвка"},
    {"label": "Задержка после заброса", "key": "hook_initial_delay", "group": "🎮 Поведение", "tab": "Поклёвка"},
    # === Поведение > Мини-игра ===
    {"label": "Чувствительность мини-игры", "key": "mini_game_sensitivity", "group": "🎮 Поведение", "tab": "Мини-игра"},
    {"label": "Скорость движения", "key": "mini_game_move_speed", "group": "🎮 Поведение", "tab": "Мини-игра"},
    {"label": "Допуск центра", "key": "mini_game_center_tolerance", "group": "🎮 Поведение", "tab": "Мини-игра"},
    {"label": "Макс. время мини-игры", "key": "mini_game_max_time", "group": "🎮 Поведение", "tab": "Мини-игра"},
    # === Поведение > Анти-чит ===
    {"label": "Вероятность пропуска", "key": "miss_chance", "group": "🎮 Поведение", "tab": "Анти-чит"},
    {"label": "Включить джиттер", "key": "idle_jitter_enabled", "group": "🎮 Поведение", "tab": "Анти-чит"},
    {"label": "Шанс джиттера", "key": "jitter_burst_chance", "group": "🎮 Поведение", "tab": "Анти-чит"},
    # === Детекция > Вода ===
    {"label": "Включить детект воды", "key": "enable_water", "group": "👁 Детекция", "tab": "Вода"},
    {"label": "Показать маску воды", "key": "show_water", "group": "👁 Детекция", "tab": "Вода"},
    {"label": "H min воды", "key": "water_h_low", "group": "👁 Детекция", "tab": "Вода"},
    {"label": "H max воды", "key": "water_h_high", "group": "👁 Детекция", "tab": "Вода"},
    {"label": "S min воды", "key": "water_s_low", "group": "👁 Детекция", "tab": "Вода"},
    {"label": "S max воды", "key": "water_s_high", "group": "👁 Детекция", "tab": "Вода"},
    {"label": "V min воды", "key": "water_v_low", "group": "👁 Детекция", "tab": "Вода"},
    {"label": "V max воды", "key": "water_v_high", "group": "👁 Детекция", "tab": "Вода"},
    {"label": "Мин. площадь воды", "key": "water_min_area", "group": "👁 Детекция", "tab": "Вода"},
    # === Детекция > Поплавок ===
    {"label": "Цветовой поиск", "key": "enable_bobber_color", "group": "👁 Детекция", "tab": "Поплавок"},
    {"label": "Поиск по шаблону", "key": "enable_bobber_template", "group": "👁 Детекция", "tab": "Поплавок"},
    {"label": "Комбинировать методы", "key": "combine_bobber_methods", "group": "👁 Детекция", "tab": "Поплавок"},
    {"label": "H min поплавка", "key": "bobber_h_low", "group": "👁 Детекция", "tab": "Поплавок"},
    {"label": "H max поплавка", "key": "bobber_h_high", "group": "👁 Детекция", "tab": "Поплавок"},
    {"label": "Мин. площадь поплавка", "key": "bobber_min_area", "group": "👁 Детекция", "tab": "Поплавок"},
    {"label": "Макс. площадь поплавка", "key": "bobber_max_area", "group": "👁 Детекция", "tab": "Поплавок"},
    # === Детекция > Зоны ===
    {"label": "Включить поиск по зонам", "key": "enable_zone_search", "group": "👁 Детекция", "tab": "Зоны"},
    {"label": "Количество зон", "key": "zone_count", "group": "👁 Детекция", "tab": "Зоны"},
    {"label": "Расстояние между зонами (px)", "key": "zone_spacing", "group": "👁 Детекция", "tab": "Зоны"},
    {"label": "Начальное смещение (px)", "key": "zone_start_distance", "group": "👁 Детекция", "tab": "Зоны"},
    {"label": "Базовый размер зоны (px)", "key": "zone_size", "group": "👁 Детекция", "tab": "Зоны"},
    # === Визуал > Оверлеи ===
    {"label": "Показать зоны", "key": "show_zones", "group": "🎨 Визуал", "tab": "Оверлеи"},
    {"label": "Показать курсор", "key": "show_pointer", "group": "🎨 Визуал", "tab": "Оверлеи"},
    {"label": "Показать линию", "key": "show_line", "group": "🎨 Визуал", "tab": "Оверлеи"},
    {"label": "Показать воду", "key": "show_environment", "group": "🎨 Визуал", "tab": "Оверлеи"},
    {"label": "Показать крест воды", "key": "show_water_cross", "group": "🎨 Визуал", "tab": "Оверлеи"},
    {"label": "Радиус клика воды", "key": "water_click_radius", "group": "🎨 Визуал", "tab": "Оверлеи"},
    # === Приложение > Темы ===
    {"label": "Тема оформления", "key": "theme", "group": "🎨 Внешний вид", "tab": "Темы"},
    # === Приложение > Шрифты ===
    {"label": "Семейство шрифта", "key": "font_family", "group": "⚙ Интерфейс", "tab": "Шрифты"},
    {"label": "Размер шрифта заголовка", "key": "font_size_title", "group": "⚙ Интерфейс", "tab": "Шрифты"},
    {"label": "Размер шрифта кнопок", "key": "font_size_button_primary", "group": "⚙ Интерфейс", "tab": "Шрифты"},
]
