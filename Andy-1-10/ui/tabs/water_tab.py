"""
Вкладка "Вода" — HSV воды, RGB маски с двумя галочками.
"""
import customtkinter as ctk
from ..widgets.sliders import SliderRow
from ..widgets.rgb_row import RGBRow


def _make_scrollable(parent, theme):
    return ctk.CTkScrollableFrame(
        parent,
        fg_color=theme.get("bg_panel", "#2a3142"),
        corner_radius=8,
        scrollbar_button_color=theme.get("bg_slider", "#3a4152"),
        scrollbar_button_hover_color=theme.get("bg_button_secondary_hover", "#34495e"),
    )


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
        ).pack(anchor="w", padx=10, pady=(10, 10))

        # === RGBRow с двумя галочками (Вкл + Показать) + цвет ===
        # Эти же настройки дублируются в visualizer_tab
        RGBRow(
            scroll, "Маска воды", self.config, self.theme, self.font_manager,
            enable_key="enable_water", show_key="show_water",
            r_key="water_mask_r", g_key="water_mask_g", b_key="water_mask_b",
            on_change=self.on_change,
            tooltip_text="Вкл — бот анализирует воду. Показать — отображать маску в Display.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=5)

        # === HSV диапазон ===
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
        ).pack(fill="x", padx=10, pady=(2, 10))