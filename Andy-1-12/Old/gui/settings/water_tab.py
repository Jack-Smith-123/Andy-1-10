"""
Вкладка "Вода" в окне настроек.
🆕 Галочка "Включить детект воды".
"""
import customtkinter as ctk
from ..widgets.slider_row import SliderRow


class WaterTab:
    def __init__(self, parent, config, on_water_change, font_size=14, theme=None, font_manager=None):
        self.config = config
        self.theme = theme or {}
        self.font_manager = font_manager
        self.on_change = on_water_change
        self.font_size = font_size
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        # 🆕 Галочка включения детекта воды
        check_frame = ctk.CTkFrame(parent, fg_color=self.theme.get("bg_panel_transparent", "transparent"))
        check_frame.pack(pady=10, padx=10, fill="x")

        self.enabled_var = ctk.BooleanVar(
            value=self.config.get("water_enabled", True)
        )
        self.check_enabled = ctk.CTkCheckBox(
            check_frame,
            text="💧 Включить детект воды",
            variable=self.enabled_var,
            font=ctk.CTkFont(size=self.font_size, weight="bold"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            command=self._on_enabled_changed
        )
        self.check_enabled.pack(side="left", padx=5)

        sliders = [
            ("🌊 Порог % воды:", "water_threshold_percent", 1.0, 30.0, 29, 8.0, "{:.1f}", float,
             "Минимальный процент воды на экране для начала рыбалки."),
            ("⏱ Интервал проверки (сек):", "water_check_interval", 0.5, 5.0, 9, 2.0, "{:.1f}", float,
             "Как часто проверять наличие воды."),
            ("🎨 HSV H min:", "water_h_min", 0, 180, 18, 95, "{:d}", int,
             "Минимальный оттенок (Hue) для воды."),
            ("🎨 HSV H max:", "water_h_max", 0, 180, 18, 135, "{:d}", int,
             "Максимальный оттенок (Hue) для воды."),
            ("🎨 HSV S min:", "water_s_min", 0, 255, 25, 30, "{:d}", int,
             "Минимальная насыщенность (Saturation) для воды."),
            ("🎨 HSV V min:", "water_v_min", 0, 255, 25, 30, "{:d}", int,
             "Минимальная яркость (Value) для воды."),
            ("🎨 HSV V max:", "water_v_max", 0, 255, 25, 220, "{:d}", int,
             "Максимальная яркость (Value) для воды."),
            ("💙 Фильтр синевы (B-R):", "water_blue_red_diff", 0, 100, 10, 20, "{:d}", int,
             "Минимальная разница B-R для фильтрации травы."),
            ("⭕ Радиус центра (px):", "water_exclude_center_radius", 0, 300, 30, 50, "{:d}", int,
             "Радиус зоны вокруг центра экрана (персонаж) для исключения."),
        ]
        self._add_sliders(parent, sliders)

    def _on_enabled_changed(self):
        """Сохраняем состояние галочки в конфиг."""
        self.config["water_enabled"] = self.enabled_var.get()
        if self.on_change:
            self.on_change("water_enabled", self.enabled_var.get())

    def _add_sliders(self, parent, sliders):
        for label, key, from_, to, steps, default, fmt, cast, tooltip in sliders:
            current = self.config.get(key, default)
            slider = SliderRow(
                parent, label, key, from_, to, steps, current,
                fmt=fmt, cast=cast, instant=True,
                on_change_callback=self.on_change,
                tooltip_text=tooltip, theme=self.theme,
                font_size=self.font_size, font_manager=self.font_manager
            )
            slider.bind_change(self.config)
