"""
Вкладка "Общее" — две подвкладки: Общее и Заброс.
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


class GeneralTab:
    """Вкладка Общее с подвкладками Общее и Заброс."""

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
            values=["Общее", "Заброс"],
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
        self.cast_frame = ctk.CTkFrame(content_frame, fg_color="transparent")

        self._build_general(self.general_frame)
        self._build_cast(self.cast_frame)

        self._switch_subtab("Общее")

    def _switch_subtab(self, name):
        """Переключение между подвкладками Общее и Заброс."""
        self.general_frame.pack_forget()
        self.cast_frame.pack_forget()
        if name == "Общее":
            self.general_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "Заброс":
            self.cast_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def _build_general(self, parent):
        """Подвкладка "Общее" — пороги, задержки, мини-игра."""
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="⚙ Общие настройки",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 10))

        items = [
            ("Порог совпадения", "match_threshold", 0.30, 0.95,
             "Минимальное совпадение шаблона (0.30-0.95). Чем выше — тем строже поиск."),
            ("Рывок по Y (клёв)", "bite_y_threshold", 1, 100,
             "Порог движения поплавка по Y для определения клёва. Меньше = чувствительнее."),
            ("Задержка клика (с)", "click_delay", 0.1, 3.0,
             "Пауза между кликами мыши."),
            ("Задержка подсечки (с)", "hook_delay", 0.1, 3.0,
             "Пауза перед подсечкой после обнаружения клёва."),
            ("Задержка перезапуска (с)", "restart_delay", 0.5, 5.0,
             "Пауза перед новым забросом после завершения рыбалки."),
            ("Таймаут ожидания поплавка (с)", "float_timeout", 3.0, 30.0,
             "Максимальное время ожидания появления поплавка."),
            ("Чувствительность мини-игры", "mini_game_sensitivity", 0.1, 2.0,
             "Скорость реакции в мини-игре."),
            ("Макс. время мини-игры (с)", "mini_game_max_time", 5.0, 30.0,
             "Таймаут мини-игры."),
        ]
        for label, key, mn, mx, tip in items:
            SliderRow(
                scroll, label, key, mn, mx,
                self.config, self.theme, self.font_manager, self.on_change,
                tooltip_text=tip, tooltip_delay=self.config.get("tooltip_delay", 1.0)
            ).pack(fill="x", padx=10, pady=3)

    def _build_cast(self, parent):
        """Подвкладка "Заброс" — время удержания ЛКМ и джиттер."""
        scroll = _make_scrollable(parent, self.theme)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="🎣 Настройки заброса",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 10))

        ctk.CTkLabel(
            scroll,
            text="Бот зажимает ЛКМ на случайное время между min и max,\n"
                 "плюс джиттер (±) для имитации человека.",
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_secondary", "#a0a8b8"),
            justify="left"
        ).pack(anchor="w", padx=10, pady=(0, 15))

        SliderRow(
            scroll, "Задержка перед забросом (с)", "cast_delay", 0.5, 10.0,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Пауза перед началом заброса.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        SliderRow(
            scroll, "Мин. время удержания (с)", "cast_hold_min", 0.1, 5.0,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Минимальное время зажатия ЛКМ при забросе.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        SliderRow(
            scroll, "Макс. время удержания (с)", "cast_hold_max", 0.1, 5.0,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Максимальное время зажатия ЛКМ при забросе.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        SliderRow(
            scroll, "Джиттер удержания (±с)", "cast_hold_jitter", 0.0, 2.0,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Случайное отклонение ± к времени удержания для имитации человека.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)

        SliderRow(
            scroll, "Макс. попыток заброса", "max_cast_attempts", 1, 10,
            self.config, self.theme, self.font_manager, self.on_change,
            tooltip_text="Сколько раз пытаться забросить удочку перед остановкой.",
            tooltip_delay=self.config.get("tooltip_delay", 1.0)
        ).pack(fill="x", padx=10, pady=3)