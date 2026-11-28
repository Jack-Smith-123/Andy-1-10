"""
Вкладка "Зоны" — настройки зон поиска поплавка вдоль линии заброса.
"""
import customtkinter as ctk
from .base_panel import BaseTab
from ..widgets.sliders import SliderRow
from ..widgets.checkbox_row import CheckboxRow


class ZonesTab(BaseTab):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build()

    def _build(self):
        scroll = self._make_scrollable(self.parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        self._add_header(scroll, "Настройки зон поиска", "📍")

        # === Общие параметры ===
        self._add_section(scroll, "Общие параметры")

        CheckboxRow(
            scroll, "Включить поиск по зонам", "enable_zone_search",
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Искать поплавок ТОЛЬКО внутри фиолетовых квадратов.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        items = [
            ("Количество зон", "zone_count", 1, 10,
             "Максимальное количество квадратов вдоль линии заброса."),
            ("Расстояние между зонами (px)", "zone_spacing", 10, 300,
             "Шаг между центрами соседних квадратов."),
            ("Начальное смещение (px)", "zone_start_distance", 0, 500,
             "Расстояние от центра окна до первого квадрата."),
            ("Базовый размер зоны (px)", "zone_size", 20, 300,
             "Размер квадрата по умолчанию (если индивидуальный выключен)."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)

        # === Индивидуальные зоны ===
        self._add_section(scroll, "Индивидуальные настройки зон")

        hint_text = "Вкл. — включить/отключить зону. Инд. — использовать свой размер."
        ctk.CTkLabel(
            scroll,
            text=hint_text,
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_secondary", "#a0a8b8"),
            justify="left"
        ).pack(anchor="w", padx=10, pady=(0, 5))

        for i in range(1, 11):
            zone_frame = ctk.CTkFrame(
                scroll,
                fg_color=self.theme.get("bg_panel", "#2a3142"),
                corner_radius=6
            )
            zone_frame.pack(fill="x", padx=10, pady=3)

            # Верхняя строка: "Зона N" + "Вкл." + "Инд."
            top_row = ctk.CTkFrame(zone_frame, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(5, 0))

            # Название зоны
            ctk.CTkLabel(
                top_row,
                text=f"Зона {i}",
                font=self._get_font("font_size_label", "bold"),
                text_color=self.theme.get("text_primary", "#e0e0e0"),
                width=70,
                anchor="w"
            ).pack(side="left", padx=(0, 10))

            # Галочка "Вкл."
            CheckboxRow(
                top_row,
                "Вкл.",
                f"zone_{i}_active",
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=f"Включить зону {i} для поиска поплавка.",
                tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(side="left", padx=5)

            # Галочка "Инд."
            CheckboxRow(
                top_row,
                "Инд.",
                f"zone_{i}_enabled",
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=f"Использовать свой размер для зоны {i}.",
                tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(side="left", padx=5)

            # Слайдер размера зоны
            SliderRow(
                zone_frame,
                f"Размер зоны {i} (px)",
                f"zone_{i}_size",
                20, 300,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=f"Размер зоны {i} в пикселях.",
                tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)
