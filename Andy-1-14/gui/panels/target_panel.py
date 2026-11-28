"""
Вкладка "Поплавок" — настройки детекта поплавка.
"""
from .base_panel import BaseTab
from ..widgets.sliders import SliderRow
from ..widgets.checkbox_row import CheckboxRow
from ..widgets.rgb_row import RGBRow


class BobberTab(BaseTab):
    """Настройки детекта поплавка: HSV, шаблоны, методы поиска."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build()
    
    def _build(self):
        scroll = self._make_scrollable(self.parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._add_header(scroll, "Настройки поплавка", "🎯")
        
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
        self._add_section(scroll, "HSV диапазон")
        
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
        self._add_section(scroll, "Цвет маски поплавка (RGB)")
        
        RGBRow(
            scroll, "Маска поплавка", self.config, self.theme, self.font_manager,
            enable_key="enable_bobber_color", show_key="show_bobber_mask",
            r_key="bobber_mask_r", g_key="bobber_mask_g", b_key="bobber_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет маски поплавка.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)