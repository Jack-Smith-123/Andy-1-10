"""
Вкладка "Поплавок" — три подвкладки: Общее, HSV, Поиск.
В начале каждой подвкладки — главная галочка "Вкл".
"""
import customtkinter as ctk
from ..widgets.sliders import SliderRow
from ..widgets.checkbox_row import CheckboxRow
from ..widgets.rgb_row import RGBRow


def _make_scrollable(parent, theme):
    """Создаёт прокручиваемый контейнер."""
    return ctk.CTkScrollableFrame(
        parent,
        fg_color=theme.get("bg_panel", "#2a3142"),
        corner_radius=8,
        scrollbar_button_color=theme.get("bg_slider", "#3a4152"),
        scrollbar_button_hover_color=theme.get("bg_button_secondary_hover", "#34495e"),
    )


class BobberTab:
    """Вкладка Поплавок с подвкладками Общее, HSV и Поиск."""

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
        # Переключатель подвкладок
        tabs_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tabs_frame.pack(fill="x", padx=0, pady=0)

        self.subtab_switcher = ctk.CTkSegmentedButton(
            tabs_frame,
            values=["Общее", "HSV", "Поиск"],
            command=self._switch_subtab,
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
        self.subtab_switcher.pack(side="left", padx=10, pady=5)

        # Контент подвкладок
        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.general_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.hsv_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.search_frame = ctk.CTkFrame(content_frame, fg_color="transparent")

        self._build_general(self.general_frame)
        self._build_hsv(self.hsv_frame)
        self._build_search(self.search_frame)

        self._switch_subtab("Общее")

    def _switch_subtab(self, name):
        """Переключение между подвкладками."""
        self.general_frame.pack_forget()
        self.hsv_frame.pack_forget()
        self.search_frame.pack_forget()
        if name == "Общее":
            self.general_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "HSV":
            self.hsv_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "Поиск":
            self.search_frame.pack(fill="both", expand=True, padx=0, pady=0)

    # ================================================================
    # ПОДВКЛАДКА "ОБЩЕЕ"
    # ================================================================
    def _build_general(self, parent):
        """Подвкладка "Общее" — главная галочка + методы поиска + RGB маски."""
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="🎯 Настройки поплавка",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # 🆕 Главная галочка "Вкл" в самом верху
        CheckboxRow(
            scroll, "Вкл — поиск поплавка", "enable_bobber_search",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Полностью включить/выключить поиск поплавка ботом.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        # Методы поиска
        ctk.CTkLabel(
            scroll, text="Методы поиска",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(15, 5))

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
        ).pack(fill="x", padx=10, pady=(3, 15))

        # Отображение
        ctk.CTkLabel(
            scroll, text="Отображение",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(0, 5))

        CheckboxRow(
            scroll, "Показать маску поплавка", "show_bobber_mask",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Отображать маску поплавка в окне Display.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        # RGB цвет маски
        ctk.CTkLabel(
            scroll, text="Цвет маски поплавка",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(15, 5))

        RGBRow(
            scroll, "Маска поплавка", self.config, self.theme, self.font_manager,
            enable_key="enable_bobber_color", show_key="show_bobber_mask",
            r_key="bobber_mask_r", g_key="bobber_mask_g", b_key="bobber_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет маски поплавка в окне Display.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

    # ================================================================
    # ПОДВКЛАДКА "HSV"
    # ================================================================
    def _build_hsv(self, parent):
        """Подвкладка "HSV" — главная галочка + HSV диапазон + площадь."""
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="🎨 HSV настройки поплавка",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # 🆕 Главная галочка "Вкл" в самом верху
        CheckboxRow(
            scroll, "Вкл — HSV-поиск", "enable_bobber_hsv",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Включить/выключить HSV-поиск поплавка. Если выключено — используется только шаблонный поиск.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        # HSV диапазон
        ctk.CTkLabel(
            scroll, text="HSV диапазон",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(15, 5))

        hsv_items = [
            ("H min", "bobber_h_low", 0, 180, "Минимальный оттенок (Hue)."),
            ("H max", "bobber_h_high", 0, 180, "Максимальный оттенок (Hue)."),
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

        # Площадь
        ctk.CTkLabel(
            scroll, text="Площадь поплавка",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(15, 5))

        SliderRow(
            scroll, "Мин. площадь", "bobber_min_area", 10, 2000,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Минимальная площадь поплавка в пикселях.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=2)

        SliderRow(
            scroll, "Макс. площадь", "bobber_max_area", 500, 10000,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Максимальная площадь поплавка в пикселях.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=(2, 10))

    # ================================================================
    # ПОДВКЛАДКА "ПОИСК"
    # ================================================================
    def _build_search(self, parent):
        """Подвкладка "Поиск" — главная галочка + настройки 5 зон."""
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="🔍 Зоны поиска (5 квадратов)",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # 🆕 Главная галочка "Вкл" в самом верху
        CheckboxRow(
            scroll, "Вкл — зоны поиска", "enable_zone_search",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Полностью включить/выключить поиск по зонам. Если выключено — бот не ищет поплавок в зонах.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        # Общая галочка показа зон в Display
        CheckboxRow(
            scroll, "Показать зоны (Display)", "show_zones",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Отображать зоны поиска квадратами в окне Display.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        # Индивидуальные настройки для каждого из 5 квадратов
        for i in range(1, 6):
            enabled_key = f"zone_{i}_enabled"
            size_key = f"zone_{i}_size"
            
            CheckboxRow(
                scroll, f"Зона {i} — Вкл", enabled_key,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=f"Включить/выключить зону {i}.",
                tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=2)

            SliderRow(
                scroll, f"Зона {i} — Размер", size_key, 20, 200,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=f"Размер квадрата зоны {i} (20-200 px).",
                tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=2)

        # Шаг между зонами
        SliderRow(
            scroll, "Шаг между зонами", "search_step", 20, 200,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Расстояние между центрами зон.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=(5, 10))

        # RGB цвет зон
        RGBRow(
            scroll, "Цвет зон поиска", self.config, self.theme, self.font_manager,
            enable_key="show_zones", show_key="show_zones",
            r_key="zone_mask_r", g_key="zone_mask_g", b_key="zone_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет квадратов зон поиска.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)