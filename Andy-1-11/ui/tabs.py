"""
Все вкладки настроек с прокруткой и RGB-настройками.
"""
import customtkinter as ctk
from .themes import THEMES
from .widgets.fonts import FontManager, AVAILABLE_FONTS
from .widgets.sliders import SliderRow
from .widgets.themes import ThemeRow
from .widgets.checkbox_row import CheckboxRow
from .widgets.rgb_row import RGBRow


def _make_scrollable(parent, theme):
    """Создаёт прокручиваемый контейнер."""
    return ctk.CTkScrollableFrame(
        parent,
        fg_color=theme.get("bg_panel", "#2a3142"),
        corner_radius=8,
        scrollbar_button_color=theme.get("bg_slider", "#3a4152"),
        scrollbar_button_hover_color=theme.get("bg_button_secondary_hover", "#34495e"),
    )


# ============================================================
# Вкладка "Общее" (внутри "Бот")
# ============================================================
class GeneralTab:
    def __init__(self, parent, config, on_change_callback, font_size=13,
                 theme=None, font_manager=None):
        self.config = config
        self.on_change = on_change_callback
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="⚙ Общие настройки",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 10))

        items = [
            ("Порог совпадения", "match_threshold", 0.30, 0.95,
             "Минимальное совпадение шаблона (0.30-0.95). Чем выше — тем строже поиск."),
            ("Рывок по Y (клёв)", "bite_y_threshold", 1, 100,
             "Порог движения поплавка по Y для определения клёва. Меньше = чувствительнее."),
            ("Задержка клика (с)", "click_delay", 0.1, 3.0,
             "Пауза между кликами мыши."),
            ("Задержка заброса (с)", "cast_delay", 1.0, 10.0,
             "Время ожидания после заброса удочки."),
            ("Задержка подсечки (с)", "hook_delay", 0.1, 3.0,
             "Пауза перед подсечкой после обнаружения клёва."),
            ("Задержка перезапуска (с)", "restart_delay", 0.5, 5.0,
             "Пауза перед новым забросом после завершения рыбалки."),
            ("Таймаут ожидания поплавка (с)", "float_timeout", 3.0, 30.0,
             "Максимальное время ожидания появления поплавка."),
            ("Макс. попыток заброса", "max_cast_attempts", 1, 10,
             "Сколько раз пытаться забросить удочку перед остановкой."),
            ("Чувствительность мини-игры", "mini_game_sensitivity", 0.1, 2.0,
             "Скорость реакции в мини-игре."),
            ("Макс. время мини-игры (с)", "mini_game_max_time", 5.0, 30.0,
             "Таймаут мини-игры."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)


# ============================================================
# Вкладка "Вода" (внутри "Бот")
# ============================================================
class WaterTab:
    def __init__(self, parent, config, on_change_callback, font_size=13,
                 theme=None, font_manager=None):
        self.config = config
        self.on_change = on_change_callback
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="💧 Настройки воды",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # Галочки Вкл / Показать
        CheckboxRow(
            scroll, "Включить детект воды", "enable_water",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Анализировать кадр на наличие воды.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        CheckboxRow(
            scroll, "Показать маску воды", "show_water",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Отображать маску воды поверх кадра.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        # HSV
        ctk.CTkLabel(
            scroll, text="HSV диапазон",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(15, 5))

        hsv_items = [
            ("H min", "water_h_low", 0, 180, "Минимальный оттенок (Hue)."),
            ("H max", "water_h_high", 0, 180, "Максимальный оттенок (Hue)."),
            ("S min", "water_s_low", 0, 255, "Минимальная насыщенность."),
            ("S max", "water_s_high", 0, 255, "Максимальная насыщенность."),
            ("V min", "water_v_low", 0, 255, "Минимальная яркость."),
            ("V max", "water_v_high", 0, 255, "Максимальная яркость."),
        ]
        for label, key, mn, mx, tip in hsv_items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=2)

        SliderRow(
            scroll, "Мин. площадь", "water_min_area", 1000, 50000,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Минимальная площадь воды в пикселях.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=2)

        SliderRow(
            scroll, "Коэф. синевы", "water_blue_ratio", 0.5, 2.0,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Коэффициент фильтра синевы.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=2)

        SliderRow(
            scroll, "Интервал проверки (с)", "water_check_interval", 0.5, 10.0,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Как часто проверять наличие воды.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=(2, 15))

        # RGB цвет маски
        ctk.CTkLabel(
            scroll, text="Цвет маски воды (RGB)",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(0, 5))

        RGBRow(
            scroll, "Маска воды", self.config, self.theme, self.font_manager,
            enable_key="enable_water", show_key="show_water",
            r_key="water_mask_r", g_key="water_mask_g", b_key="water_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет, которым рисуется маска воды.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)


# ============================================================
# Вкладка "Поплавок" (внутри "Бот")
# ============================================================
class BobberTab:
    def __init__(self, parent, config, on_change_callback, font_size=13,
                 theme=None, font_manager=None):
        self.config = config
        self.on_change = on_change_callback
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="🎯 Настройки поплавка",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # Галочки методов поиска
        CheckboxRow(
            scroll, "Цветовой поиск", "enable_bobber_color",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Ищет поплавок по HSV-цвету. Быстрый метод.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        CheckboxRow(
            scroll, "Поиск по шаблону", "enable_bobber_template",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Ищет поплавок по шаблону изображения. Точнее, но медленнее.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        CheckboxRow(
            scroll, "Комбинировать методы", "combine_bobber_methods",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Использовать оба метода одновременно.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        CheckboxRow(
            scroll, "Показать маску поплавка", "show_bobber_mask",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Отображать маску поплавка поверх кадра.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=(3, 15))

        # HSV
        ctk.CTkLabel(
            scroll, text="HSV диапазон",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(0, 5))

        hsv_items = [
            ("H min", "bobber_h_low", 0, 180, "Минимальный оттенок."),
            ("H max", "bobber_h_high", 0, 180, "Максимальный оттенок."),
            ("S min", "bobber_s_low", 0, 255, "Минимальная насыщенность."),
            ("S max", "bobber_s_high", 0, 255, "Максимальная насыщенность."),
            ("V min", "bobber_v_low", 0, 255, "Минимальная яркость."),
            ("V max", "bobber_v_high", 0, 255, "Максимальная яркость."),
        ]
        for label, key, mn, mx, tip in hsv_items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=2)

        SliderRow(
            scroll, "Мин. площадь", "bobber_min_area", 10, 2000,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Минимальная площадь поплавка.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=2)

        SliderRow(
            scroll, "Макс. площадь", "bobber_max_area", 500, 10000,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Максимальная площадь поплавка.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=(2, 15))

        # RGB цвет маски
        ctk.CTkLabel(
            scroll, text="Цвет маски поплавка (RGB)",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(0, 5))

        RGBRow(
            scroll, "Маска поплавка", self.config, self.theme, self.font_manager,
            enable_key="enable_bobber_color", show_key="show_bobber_mask",
            r_key="bobber_mask_r", g_key="bobber_mask_g", b_key="bobber_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет маски поплавка.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)


# ============================================================
# Вкладка "Визуал" (внутри "Бот")
# ============================================================
class VisualizerTab:
    def __init__(self, parent, config, on_change_callback, font_size=13,
                 theme=None, font_manager=None):
        self.config = config
        self.on_change = on_change_callback
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="👁 Настройки визуала",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 10))

        # Вода
        ctk.CTkLabel(
            scroll, text="Вода",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        RGBRow(
            scroll, "Маска воды", self.config, self.theme, self.font_manager,
            enable_key="enable_water", show_key="show_water",
            r_key="water_mask_r", g_key="water_mask_g", b_key="water_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет и видимость маски воды.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        # Зоны
        ctk.CTkLabel(
            scroll, text="Зоны поиска",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        CheckboxRow(
            scroll, "Показать зоны", "show_zones",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Отображать зоны поиска жёлтыми прямоугольниками.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        RGBRow(
            scroll, "Цвет зон", self.config, self.theme, self.font_manager,
            enable_key="show_zones", show_key="show_zones",
            r_key="zone_mask_r", g_key="zone_mask_g", b_key="zone_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет прямоугольников зон поиска.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        # Курсор
        ctk.CTkLabel(
            scroll, text="Курсор",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        CheckboxRow(
            scroll, "Показать курсор", "show_cursor",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Отображать положение курсора.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        RGBRow(
            scroll, "Цвет курсора", self.config, self.theme, self.font_manager,
            enable_key="show_cursor", show_key="show_cursor",
            r_key="cursor_mask_r", g_key="cursor_mask_g", b_key="cursor_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет крестика курсора.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        # Поплавок
        ctk.CTkLabel(
            scroll, text="Поплавок",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        CheckboxRow(
            scroll, "Показать маску поплавка", "show_bobber_mask",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Отображать маску поплавка.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        RGBRow(
            scroll, "Цвет маски поплавка", self.config, self.theme, self.font_manager,
            enable_key="enable_bobber_color", show_key="show_bobber_mask",
            r_key="bobber_mask_r", g_key="bobber_mask_g", b_key="bobber_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет маски поплавка.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=(3, 10))


# ============================================================
# Вкладка "Шрифты" (внутри "Приложение")
# ============================================================
class FontTab:
    def __init__(self, parent, config, font_size=13, theme=None, font_manager=None):
        self.config = config
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self._family_var = ctk.StringVar(value=config.get("font_family", "Arial"))
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Верхняя часть: семейство + превью
        top_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=(10, 10))

        left = ctk.CTkFrame(top_frame, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left, text="🔤 Семейство шрифта",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", pady=(0, 5))

        ctk.CTkOptionMenu(
            left,
            variable=self._family_var,
            values=AVAILABLE_FONTS,
            width=200, height=32,
            fg_color=self.theme.get("bg_button_secondary", "#2c3e50"),
            button_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=lambda v: self._update_preview()
        ).pack(anchor="w")

        # Превью справа
        right = ctk.CTkFrame(top_frame, fg_color=self.theme.get("bg_panel", "#2a3142"),
                             corner_radius=6, width=180, height=80)
        right.pack(side="right", padx=(10, 0))
        right.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(
            right, text="Пример текста\nAa Бб 0123",
            font=self._get_font("font_size_header", "normal"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            justify="center"
        )
        self.preview_label.pack(expand=True)

        # Размеры шрифтов
        ctk.CTkLabel(
            scroll, text="📏 Размеры шрифтов",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        font_keys = [
            ("Заголовок окна", "font_size_title", 12, 30),
            ("Заголовок в шапке", "font_size_header", 12, 30),
            ("Заголовки секций", "font_size_section", 12, 30),
            ("Основные кнопки", "font_size_button_primary", 12, 30),
            ("Вторичные кнопки", "font_size_button_secondary", 12, 30),
            ("Метки", "font_size_label", 10, 24),
            ("Значения", "font_size_value", 10, 24),
            ("Статус", "font_size_status", 10, 24),
            ("Лог", "font_size_log", 10, 24),
        ]
        for label, key, mn, mx in font_keys:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager,
                tooltip_text=f"Размер шрифта: {label}",
                tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=2)

    def _update_preview(self):
        """Обновляет превью при смене семейства."""
        family = self._family_var.get()
        size = self.config.get("font_size_header", 16)
        self.preview_label.configure(
            font=ctk.CTkFont(family=family, size=int(size))
        )

    def get_pending_font_family(self):
        return self._family_var.get()


# ============================================================
# Вкладка "Темы" (внутри "Приложение")
# ============================================================
class ThemeTab:
    def __init__(self, parent, config, font_size=13, theme=None, font_manager=None,
                 on_theme_editor=None):
        self.config = config
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self.on_theme_editor = on_theme_editor
        self._theme_var = ctk.StringVar(value=config.get("theme", "albion_dark"))
        self._theme_rows = []
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="🎨 Тема оформления",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 10))

        themes_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        themes_frame.pack(fill="x", padx=10)

        self._rebuild_theme_list(themes_frame)

        if self.on_theme_editor:
            ctk.CTkButton(
                scroll, text="✨ Создать свою тему",
                font=self._get_font("font_size_button_primary", "bold"),
                height=40,
                fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
                hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
                text_color=self.theme.get("text_primary", "#e0e0e0"),
                command=self.on_theme_editor
            ).pack(pady=15, padx=10, fill="x")

    def _rebuild_theme_list(self, parent):
        for row in self._theme_rows:
            row.destroy()
        self._theme_rows.clear()

        for theme_key, theme_data in THEMES.items():
            row = ThemeRow(
                parent, theme_key, theme_data,
                self._theme_var, self._on_theme_selected,
                self.font_manager, self.theme, self.font_size
            )
            row.pack(fill="x", pady=4)
            self._theme_rows.append(row)

    def _on_theme_selected(self, theme_key):
        self.config["theme"] = theme_key

    def get_pending_theme(self):
        return self._theme_var.get()


# ============================================================
# Вкладка "Подсказки" (внутри "Приложение")
# ============================================================
class TipsTab:
    def __init__(self, parent, config, font_size=13, theme=None, font_manager=None):
        self.config = config
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="💡 Настройки подсказок",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 10))

        SliderRow(
            scroll, "Задержка показа (сек)", "tooltip_delay", 0.1, 5.0,
            self.config, self.theme, self.font_manager,
            tooltip_text="Время задержки перед показом подсказки."
        ).pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(
            scroll,
            text="Подсказки появляются при наведении курсора на любую настройку.\n"
                 "Они исчезают при уходе курсора или клике.",
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_secondary", "#a0a8b8"),
            justify="left"
        ).pack(anchor="w", padx=10, pady=(20, 10))


# ============================================================
# Вкладка "Приложение" (внешняя, содержит "Темы", "Шрифты", "Подсказки")
# ============================================================
class AppTab:
    def __init__(self, parent, config, font_size=13, theme=None, font_manager=None,
                 on_theme_editor=None):
        self.config = config
        self.font_size = font_size
        self.theme = theme or {}
        self.font_manager = font_manager
        self.on_theme_editor = on_theme_editor
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        tabs_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tabs_frame.pack(fill="x", padx=0, pady=0)

        self.inner_switcher = ctk.CTkSegmentedButton(
            tabs_frame,
            values=["Темы", "Шрифты", "Подсказки"],
            command=self._switch_inner_tab,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            selected_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            selected_hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            unselected_color=self.theme.get("bg_slider", "#3a4152"),
            unselected_hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            corner_radius=8,
            border_width=0,
            font=self._get_font("font_size_button_secondary", "bold")
        )
        self.inner_switcher.pack(side="left", padx=10, pady=5)

        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.themes_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.fonts_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.tips_frame = ctk.CTkFrame(content_frame, fg_color="transparent")

        self.theme_tab = ThemeTab(
            self.themes_frame, self.config, self.font_size, self.theme,
            self.font_manager, on_theme_editor=self.on_theme_editor
        )
        self.font_tab = FontTab(
            self.fonts_frame, self.config, self.font_size, self.theme, self.font_manager
        )
        self.tips_tab = TipsTab(
            self.tips_frame, self.config, self.font_size, self.theme, self.font_manager
        )

        self._switch_inner_tab("Темы")

    def _switch_inner_tab(self, name):
        self.themes_frame.pack_forget()
        self.fonts_frame.pack_forget()
        self.tips_frame.pack_forget()
        if name == "Темы":
            self.themes_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "Шрифты":
            self.fonts_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "Подсказки":
            self.tips_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def get_pending_theme(self):
        return self.theme_tab.get_pending_theme()

    def get_pending_font_family(self):
        return self.font_tab.get_pending_font_family()