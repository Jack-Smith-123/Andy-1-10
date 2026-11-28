"""
Вкладка "Поклевка" — параметры обнаружения и тайминги.
"""
import customtkinter as ctk
from ..widgets.sliders import SliderRow


def _make_scrollable(parent, theme):
    """Создаёт прокручиваемый контейнер."""
    return ctk.CTkScrollableFrame(
        parent,
        fg_color=theme.get("bg_panel", "#2a3142"),
        corner_radius=8,
        scrollbar_button_color=theme.get("bg_slider", "#3a4152"),
        scrollbar_button_hover_color=theme.get("bg_button_secondary_hover", "#34495e"),
    )


class BiteTab:
    """Вкладка Поклевка с подвкладками Обнаружение и Тайминги."""

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
            values=["Обнаружение", "Тайминги"],
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

        self.detection_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.timing_frame = ctk.CTkFrame(content_frame, fg_color="transparent")

        self._build_detection(self.detection_frame)
        self._build_timing(self.timing_frame)

        self._switch_subtab("Обнаружение")

    def _switch_subtab(self, name):
        """Переключение между подвкладками."""
        self.detection_frame.pack_forget()
        self.timing_frame.pack_forget()
        if name == "Обнаружение":
            self.detection_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "Тайминги":
            self.timing_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def _build_detection(self, parent):
        """Подвкладка Обнаружение."""
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="🎯 Обнаружение поклевки",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 10))

        # Порог вертикального движения
        SliderRow(
            scroll, "Рывок вниз (px)", "bite_y_threshold",
            self.config, self.theme, self.font_manager,
            from_=1, to=20, step=1,
            on_change=self.on_change,
            tooltip_text="Минимальное смещение поплавка вниз для срабатывания поклевки",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        )

        # Порог горизонтального движения
        SliderRow(
            scroll, "Рывок в сторону (px)", "bite_x_threshold",
            self.config, self.theme, self.font_manager,
            from_=5, to=50, step=1,
            on_change=self.on_change,
            tooltip_text="Минимальное смещение поплавка в сторону для срабатывания поклевки",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        )

        # Лимит пропущенных кадров
        SliderRow(
            scroll, "Пропущено кадров", "missing_frames_limit",
            self.config, self.theme, self.font_manager,
            from_=1, to=10, step=1,
            on_change=self.on_change,
            tooltip_text="Сколько кадров поплавок может отсутствовать перед срабатыванием поклевки",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        )

        # Максимальный скачок по X
        SliderRow(
            scroll, "Макс. скачок X (px)", "max_x_jump",
            self.config, self.theme, self.font_manager,
            from_=30, to=200, step=5,
            on_change=self.on_change,
            tooltip_text="Если поплавок прыгнул дальше этого значения, история сбрасывается",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        )

        # Порог погружения
        SliderRow(
            scroll, "Погружение (px)", "sink_threshold",
            self.config, self.theme, self.font_manager,
            from_=1, to=10, step=1,
            on_change=self.on_change,
            tooltip_text="Минимальное погружение за кадр для подсчета плавного погружения",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        )

        # Кадров погружения
        SliderRow(
            scroll, "Кадров погружения", "sink_frames_needed",
            self.config, self.theme, self.font_manager,
            from_=1, to=10, step=1,
            on_change=self.on_change,
            tooltip_text="Сколько кадров подряд поплавок должен погружаться для срабатывания",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        )

        # Порог исчезновения белой части
        SliderRow(
            scroll, "Белая часть (%)", "white_part_loss_threshold",
            self.config, self.theme, self.font_manager,
            from_=0.1, to=1.0, step=0.05,
            on_change=self.on_change,
            tooltip_text="Процент исчезновения белой части поплавка для срабатывания поклевки (0.5 = 50%)",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        )

        # Минимум кадров подтверждения
        SliderRow(
            scroll, "Мин. кадров подтверждения", "min_seen_frames",
            self.config, self.theme, self.font_manager,
            from_=1, to=10, step=1,
            on_change=self.on_change,
            tooltip_text="Сколько кадров подряд поплавок должен быть виден перед переходом в HOOK",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        )

    def _build_timing(self, parent):
        """Подвкладка Тайминги."""
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="⏱ Тайминги",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 10))

        # Задержка перед анализом
        SliderRow(
            scroll, "Задержка старта (сек)", "hook_initial_delay",
            self.config, self.theme, self.font_manager,
            from_=0.5, to=10.0, step=0.1,
            on_change=self.on_change,
            tooltip_text="Задержка перед началом анализа поплавка после его обнаружения",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        )

        # Таймаут ожидания поклевки
        SliderRow(
            scroll, "Таймаут ожидания (сек)", "hook_timeout",
            self.config, self.theme, self.font_manager,
            from_=10.0, to=120.0, step=1.0,
            on_change=self.on_change,
            tooltip_text="Максимальное время ожидания поклевки перед перезапуском",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        )

        # Таймаут потери поплавка
        SliderRow(
            scroll, "Таймаут потери (сек)", "bobber_lost_timeout",
            self.config, self.theme, self.font_manager,
            from_=1.0, to=20.0, step=0.5,
            on_change=self.on_change,
            tooltip_text="Через сколько секунд без поплавка перезапускать цикл",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        )