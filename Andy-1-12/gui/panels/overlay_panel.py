"""
Вкладка "RGB/Визуал" — настройки отображения масок и зон.
"""
from .base_panel import BaseTab
from ..widgets.checkbox_row import CheckboxRow
from ..widgets.rgb_row import RGBRow


class VisualizerTab(BaseTab):
    """Настройки визуализации: маски воды, поплавка, зон, курсора."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build()
    
    def _build(self):
        scroll = self._make_scrollable(self.parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._add_header(scroll, "Настройки визуала", "👁")
        
        # === Вода ===
        self._add_section(scroll, "Вода")
        
        RGBRow(
            scroll, "Маска воды", self.config, self.theme, self.font_manager,
            enable_key="enable_water", show_key="show_water",
            r_key="water_mask_r", g_key="water_mask_g", b_key="water_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет и видимость маски воды.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)
        
        # === Зоны ===
        self._add_section(scroll, "Зоны поиска")
        
        CheckboxRow(
            scroll, "Показать зоны", "show_zones",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Отображать зоны поиска фиолетовыми прямоугольниками.",
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
        
        # === Курсор ===
        self._add_section(scroll, "Курсор")
        
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
        
        # === Поплавок ===
        self._add_section(scroll, "Поплавок")
        
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