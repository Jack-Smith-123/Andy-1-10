"""
Вкладка "RGB" — цвета и галочки Вкл/Показать для каждого элемента.
"""
import customtkinter as ctk
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


class VisualizerTab:
    """Вкладка RGB — настройки цветов и видимости всех элементов."""

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
            scroll, text="🎨 RGB настройки",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 10))

        ctk.CTkLabel(
            scroll,
            text="Вкл (бот) — включить/выключить функцию для бота.\n"
                 "Показать (Display) — показывать/скрыть в окне Display.",
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_secondary", "#a0a8b8"),
            justify="left"
        ).pack(anchor="w", padx=10, pady=(0, 15))

        # === ВОДА ===
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
            tooltip_text="Цвет маски воды.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        RGBRow(
            scroll, "Крест центра воды", self.config, self.theme, self.font_manager,
            enable_key="enable_water", show_key="show_water",
            r_key="water_cross_r", g_key="water_cross_g", b_key="water_cross_b",
            on_change=self.on_change,
            tooltip_text="Цвет крестика в центре воды.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        RGBRow(
            scroll, "Зона заброса", self.config, self.theme, self.font_manager,
            enable_key="enable_water", show_key="show_water",
            r_key="water_zone_r", g_key="water_zone_g", b_key="water_zone_b",
            on_change=self.on_change,
            tooltip_text="Цвет квадрата зоны заброса вокруг центра воды.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        # === КУРСОР ===
        ctk.CTkLabel(
            scroll, text="Курсор",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(15, 5))

        RGBRow(
            scroll, "Круг курсора", self.config, self.theme, self.font_manager,
            enable_key="enable_cursor", show_key="show_cursor",
            r_key="cursor_mask_r", g_key="cursor_mask_g", b_key="cursor_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет круга курсора.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        # === ЛИНИЯ ПОИСКА ===
        ctk.CTkLabel(
            scroll, text="Линия поиска",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(15, 5))

        RGBRow(
            scroll, "Линия", self.config, self.theme, self.font_manager,
            enable_key="show_zones", show_key="show_zones",
            r_key="line_mask_r", g_key="line_mask_g", b_key="line_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет линии от центра через курсор.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        # === ЗОНЫ ПОИСКА ===
        ctk.CTkLabel(
            scroll, text="Зоны поиска",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(15, 5))

        RGBRow(
            scroll, "Квадраты зон", self.config, self.theme, self.font_manager,
            enable_key="enable_zone_search", show_key="show_zones",
            r_key="zone_mask_r", g_key="zone_mask_g", b_key="zone_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет квадратов зон поиска.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        # === ПОПЛАВОК ===
        ctk.CTkLabel(
            scroll, text="Поплавок",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(15, 5))

        RGBRow(
            scroll, "Маска поплавка", self.config, self.theme, self.font_manager,
            enable_key="enable_bobber_color", show_key="show_bobber_mask",
            r_key="bobber_mask_r", g_key="bobber_mask_g", b_key="bobber_mask_b",
            on_change=self.on_change,
            tooltip_text="Цвет маски поплавка.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        RGBRow(
            scroll, "Рамка (найден)", self.config, self.theme, self.font_manager,
            enable_key="enable_bobber_color", show_key="show_bobber_mask",
            r_key="bobber_found_r", g_key="bobber_found_g", b_key="bobber_found_b",
            on_change=self.on_change,
            tooltip_text="Цвет рамки когда поплавок найден.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        RGBRow(
            scroll, "Рамка (проверка)", self.config, self.theme, self.font_manager,
            enable_key="enable_bobber_color", show_key="show_bobber_mask",
            r_key="bobber_checking_r", g_key="bobber_checking_g", b_key="bobber_checking_b",
            on_change=self.on_change,
            tooltip_text="Цвет рамки при проверке поплавка.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        RGBRow(
            scroll, "Рамка (не найден)", self.config, self.theme, self.font_manager,
            enable_key="enable_bobber_color", show_key="show_bobber_mask",
            r_key="bobber_not_found_r", g_key="bobber_not_found_g", b_key="bobber_not_found_b",
            on_change=self.on_change,
            tooltip_text="Цвет рамки когда поплавок не найден.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=(3, 10))