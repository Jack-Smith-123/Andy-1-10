"""
Вкладка "Поплавок" в окне настроек.
🆕 Подвкладки: Поиск, Цвет, HSV.
🆕 "Поиск" включает: шаблон, курсор, линия, порог, рывок.
🆕 "Курсор" удалён (всё перенесено в "Поиск").
"""
import customtkinter as ctk
from ..widgets.slider_row import SliderRow


class BobberTab:
    def __init__(self, parent, config, on_water_change, font_size=14, theme=None, font_manager=None):
        self.config = config
        self.theme = theme or {}
        self.font_manager = font_manager
        self.on_change = on_water_change
        self.font_size = font_size

        tabs_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tabs_frame.pack(fill="x", padx=0, pady=(0, 5))
        self.tab_switcher = ctk.CTkSegmentedButton(
            tabs_frame,
            values=["🔍 Поиск", "🎨 Цвет", "🌈 HSV"],
            command=self._switch_tab,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            selected_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            selected_hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            unselected_color=self.theme.get("bg_slider", "#3a4152"),
            unselected_hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            corner_radius=8,
            border_width=0,
            font=ctk.CTkFont(size=self.font_size - 1, weight="bold")
        )
        self.tab_switcher.pack(side="left", padx=10, pady=5)

        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.search_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.color_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.hsv_frame = ctk.CTkFrame(content_frame, fg_color="transparent")

        self._build_search_tab()
        self._build_color_tab()
        self._build_hsv_tab()

        self._switch_tab("🔍 Поиск")

    def _build_search_tab(self):
        """🆕 Вкладка "Поиск": шаблон, курсор, линия, порог, рывок."""
        # Галочка: поиск по шаблону
        check1 = ctk.CTkFrame(self.search_frame, fg_color=self.theme.get("bg_panel_transparent", "transparent"))
        check1.pack(pady=5, padx=10, fill="x")
        self.template_var = ctk.BooleanVar(value=self.config.get("bobber_template_search_enabled", True))
        ctk.CTkCheckBox(
            check1, text="🎯 Поиск по шаблону", variable=self.template_var,
            font=ctk.CTkFont(size=self.font_size, weight="bold"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            command=lambda: self._on_check_changed("bobber_template_search_enabled", self.template_var)
        ).pack(side="left", padx=5)

        # Галочка: поиск вокруг курсора
        check2 = ctk.CTkFrame(self.search_frame, fg_color=self.theme.get("bg_panel_transparent", "transparent"))
        check2.pack(pady=5, padx=10, fill="x")
        self.cursor_var = ctk.BooleanVar(value=self.config.get("bobber_cursor_zone_enabled", True))
        ctk.CTkCheckBox(
            check2, text="🔍 Поиск вокруг курсора", variable=self.cursor_var,
            font=ctk.CTkFont(size=self.font_size, weight="bold"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            command=lambda: self._on_check_changed("bobber_cursor_zone_enabled", self.cursor_var)
        ).pack(side="left", padx=5)

        # Радиус зоны курсора
        self._add_slider(self.search_frame, "📏 Радиус зоны курсора (px):", "bobber_cursor_zone_radius", 50, 400, 35, 150, "{:d}", int,
            "Радиус квадрата вокруг курсора для поиска поплавка.")

        # Галочка: поиск по линии
        check3 = ctk.CTkFrame(self.search_frame, fg_color=self.theme.get("bg_panel_transparent", "transparent"))
        check3.pack(pady=5, padx=10, fill="x")
        self.line_var = ctk.BooleanVar(value=self.config.get("bobber_line_search_enabled", True))
        ctk.CTkCheckBox(
            check3, text="📏 Поиск по линии", variable=self.line_var,
            font=ctk.CTkFont(size=self.font_size, weight="bold"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            command=lambda: self._on_check_changed("bobber_line_search_enabled", self.line_var)
        ).pack(side="left", padx=5)

        # Ширина зоны линии
        self._add_slider(self.search_frame, "📏 Ширина зоны линии (px):", "bobber_line_search_width", 50, 300, 25, 150, "{:d}", int,
            "Ширина квадратов поиска вдоль линии.")

        # Разделитель
        sep = ctk.CTkFrame(self.search_frame, height=2, fg_color=self.theme.get("bg_panel", "#2a3142"))
        sep.pack(fill="x", padx=10, pady=10)

        # Порог совпадения (перенесён с главного окна)
        self._add_slider(self.search_frame, "🎯 Порог совпадения:", "bobber_match_threshold", 0.30, 0.95, 65, 0.62, "{:.2f}", float,
            "Минимальный score шаблона для детекта поплавка.\nНиже = больше ложных срабатываний, выше = надёжнее.")

        # Рывок по Y (перенесён с главного окна)
        self._add_slider(self.search_frame, "⬇️ Рывок по Y (клёв):", "bobber_bite_y_threshold", 1, 100, 99, 7, "{:d}", int,
            "Сколько пикселей должен дёрнуться поплавок вниз для детекта клёва.")

        # Цветовая валидация
        check4 = ctk.CTkFrame(self.search_frame, fg_color=self.theme.get("bg_panel_transparent", "transparent"))
        check4.pack(pady=5, padx=10, fill="x")
        self.validation_var = ctk.BooleanVar(value=self.config.get("bobber_color_validation_enabled", True))
        ctk.CTkCheckBox(
            check4, text="🎨 Цветовая валидация", variable=self.validation_var,
            font=ctk.CTkFont(size=self.font_size, weight="bold"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            command=lambda: self._on_check_changed("bobber_color_validation_enabled", self.validation_var)
        ).pack(side="left", padx=5)

    def _on_check_changed(self, key, var):
        self.config[key] = var.get()
        if self.on_change:
            self.on_change(key, var.get())

    def _add_slider(self, parent, label, key, from_, to, steps, default, fmt, cast, tooltip):
        current = self.config.get(key, default)
        slider = SliderRow(
            parent, label, key, from_, to, steps, current,
            fmt=fmt, cast=cast, instant=True,
            on_change_callback=self.on_change,
            tooltip_text=tooltip, theme=self.theme,
            font_size=self.font_size, font_manager=self.font_manager
        )
        slider.bind_change(self.config)

    def _build_color_tab(self):
        sliders = [
            ("🎨 Красный min:", "bobber_red_min", 0, 255, 25, 120, "{:d}", int, "Минимальное значение красного канала."),
            ("🎨 Зелёный max:", "bobber_green_max", 0, 150, 15, 90, "{:d}", int, "Максимальное значение зелёного канала."),
            ("🎨 Синий max:", "bobber_blue_max", 0, 150, 15, 90, "{:d}", int, "Максимальное значение синего канала."),
            ("⚪ Белый порог:", "bobber_white_threshold", 100, 255, 15, 180, "{:d}", int, "Порог для белых пикселей."),
            ("📏 Мин. площадь (px):", "bobber_min_area", 5, 150, 14, 20, "{:d}", int, "Минимальная площадь кластера для детекта."),
            ("🚫 Радиус исключения (px):", "bobber_exclude_radius", 50, 350, 30, 150, "{:d}", int, "Радиус зоны вокруг персонажа."),
            ("↔ Смещение X (px):", "bobber_exclude_offset_x", -150, 150, 30, 0, "{:+d}", int, "Сдвиг зоны исключения по горизонтали."),
            ("↕ Смещение Y (px):", "bobber_exclude_offset_y", -150, 150, 30, -60, "{:+d}", int, "Сдвиг зоны исключения по вертикали."),
            ("🔀 Требовать оба цвета:", "bobber_require_both_colors", 0, 1, 1, 0, "{:d}", int, "0 = красный ИЛИ белый, 1 = оба."),
        ]
        for label, key, from_, to, steps, default, fmt, cast, tooltip in sliders:
            self._add_slider(self.color_frame, label, key, from_, to, steps, default, fmt, cast, tooltip)

    def _build_hsv_tab(self):
        """🆕 Подвкладка HSV для поплавка."""
        check_frame = ctk.CTkFrame(self.hsv_frame, fg_color=self.theme.get("bg_panel_transparent", "transparent"))
        check_frame.pack(pady=10, padx=10, fill="x")

        self.hsv_enabled_var = ctk.BooleanVar(value=self.config.get("bobber_hsv_enabled", True))
        ctk.CTkCheckBox(
            check_frame,
            text="🌈 Вкл.",
            variable=self.hsv_enabled_var,
            font=ctk.CTkFont(size=self.font_size, weight="bold"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            command=lambda: self._on_check_changed("bobber_hsv_enabled", self.hsv_enabled_var)
        ).pack(side="left", padx=5)

        sliders = [
            ("🌈 H min (оттенок):", "bobber_h_min", 0, 30, 30, 0, "{:d}", int, "Минимальный оттенок (Hue). 0-10 = красный, 10-25 = оранжевый."),
            ("🌈 H max (оттенок):", "bobber_h_max", 0, 30, 30, 25, "{:d}", int, "Максимальный оттенок (Hue)."),
            ("🌈 S min (насыщенность):", "bobber_s_min", 0, 255, 25, 60, "{:d}", int, "Минимальная насыщенность (Saturation)."),
            ("🌈 V min (яркость):", "bobber_v_min", 0, 255, 25, 60, "{:d}", int, "Минимальная яркость (Value)."),
        ]
        for label, key, from_, to, steps, default, fmt, cast, tooltip in sliders:
            self._add_slider(self.hsv_frame, label, key, from_, to, steps, default, fmt, cast, tooltip)

    def _switch_tab(self, name):
        self.search_frame.pack_forget()
        self.color_frame.pack_forget()
        self.hsv_frame.pack_forget()

        if name == "🔍 Поиск":
            self.search_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "🎨 Цвет":
            self.color_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "🌈 HSV":
            self.hsv_frame.pack(fill="both", expand=True, padx=0, pady=0)
