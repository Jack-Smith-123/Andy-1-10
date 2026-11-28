"""
Вкладка "Вода" — настройки детекта воды.
"""
from .base_panel import BaseTab
from ..widgets.sliders import SliderRow
from ..widgets.checkbox_row import CheckboxRow
from ..widgets.rgb_row import RGBRow


class WaterTab(BaseTab):
    """Настройки детекта воды и HSV-диапазонов."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build()
    
    def _build(self):
        scroll = self._make_scrollable(self.parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._add_header(scroll, "Настройки воды", "💧")
        
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
        self._add_section(scroll, "HSV диапазон")
        
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
        self._add_section(scroll, "Цвет маски воды (RGB)")
        
        RGBRow(
            scroll, "Маска воды", self.config, self.theme, self.font_manager,
            enable_key="enable_water", show_key="show_water",
            r_key="water_mask_r", g_key="water_mask_g", b_key="water_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет, которым рисуется маска воды.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)