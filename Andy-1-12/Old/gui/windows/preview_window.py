"""
Окно превью видео с кнопками "Подробно" и "Настройки".
🆕 Панели увеличивают окно вниз (pack), а не всплывают поверх.
🆕 Окно всегда привязано к левому нижнему углу экрана.
🆕 Отступ от нижнего края берётся из конфига (preview_bottom_margin).
🆕 При изменении размера окно "притягивается" обратно к нижнему краю.
"""
import customtkinter as ctk
from PIL import Image, ImageTk


class PreviewWindow(ctk.CTkToplevel):
    # Фиксированные размеры
    BASE_WIDTH = 500
    BASE_HEIGHT = 380
    PANEL_HEIGHT = 130  # Высота одной панели

    def __init__(self, parent, font_size=13, theme=None, font_manager=None,
                 on_close_callback=None, app=None):
        super().__init__(parent)
        self.title("🎥 Видео — Andy-1.8")
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self.on_close_callback = on_close_callback
        self.app = app
        self.is_open = True
        self._detail_open = False
        self._settings_open = False

        # 🆕 Отступ из конфига (по умолчанию 60px — покрывает панель задач Linux)
        self.bottom_margin = self._get_config_value("preview_bottom_margin", 60)

        # Позиционируем в левом нижнем углу при создании
        self._anchor_to_bottom_left(self.BASE_HEIGHT)

        self.resizable(False, False)
        self.configure(fg_color=self.theme.get("bg_main", "#1a1f2e"))

        # === Верхняя панель: кнопки ===
        btn_frame = ctk.CTkFrame(self, fg_color=self.theme.get("bg_panel", "#2a3142"))
        btn_frame.pack(pady=5, padx=10, fill="x")

        self.detail_btn = ctk.CTkButton(
            btn_frame, text="🔍 Подробно", width=120, height=30,
            font=self._get_font("font_size_button_secondary"),
            fg_color=self.theme.get("bg_button_secondary", "#2c3e50"),
            hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._toggle_detail
        )
        self.detail_btn.pack(side="left", padx=5)

        self.settings_btn = ctk.CTkButton(
            btn_frame, text="⚙ Настройки", width=120, height=30,
            font=self._get_font("font_size_button_secondary"),
            fg_color=self.theme.get("bg_button_secondary", "#2c3e50"),
            hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._toggle_settings
        )
        self.settings_btn.pack(side="left", padx=5)

        self.fps_label = ctk.CTkLabel(
            btn_frame, text="FPS: 0",
            font=self._get_font("font_size_preview_fps", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        )
        self.fps_label.pack(side="right", padx=10)

        # === Контейнер для изображения ===
        self.image_container = ctk.CTkFrame(self, fg_color="transparent")
        self.image_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.image_label = ctk.CTkLabel(
            self.image_container, text="Ожидание видео...",
            font=self._get_font("font_size_preview_fps"),
            text_color=self.theme.get("text_secondary", "#a0a8b8")
        )
        self.image_label.pack(fill="both", expand=True)

        # === Панель "Подробно" (скрыта) ===
        self.detail_panel = ctk.CTkFrame(
            self,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            corner_radius=6,
            border_width=1,
            border_color=self.theme.get("border_color", "#3a4152")
        )

        ctk.CTkLabel(
            self.detail_panel, text="📊 Статистика",
            font=self._get_font("font_size_section", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(8, 4))

        self.stats_label = ctk.CTkLabel(
            self.detail_panel, text="Загрузка...",
            font=self._get_font("font_size_preview_stats"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            justify="left"
        )
        self.stats_label.pack(padx=10, pady=(0, 10), fill="x")

        # === Панель "Настройки" (скрыта) ===
        self.settings_panel = ctk.CTkFrame(
            self,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            corner_radius=6,
            border_width=1,
            border_color=self.theme.get("border_color", "#3a4152")
        )

        settings_header = ctk.CTkFrame(self.settings_panel, fg_color="transparent")
        settings_header.pack(fill="x", padx=10, pady=(8, 4))
        ctk.CTkLabel(
            settings_header, text="👁 Визуализация",
            font=self._get_font("font_size_section", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(side="left")

        self.vis_vars = {}
        vis_items = [
            ("vis_water_show", "💧 Маска воды"),
            ("vis_bobber_show", "🎣 Маска поплавка"),
            ("vis_zones_show", "🟪 Зоны поиска"),
            ("vis_line_show", "📏 Линия поиска"),
            ("vis_cursor_show", "🖱 Курсор"),
        ]
        for key, label in vis_items:
            row = ctk.CTkFrame(self.settings_panel, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)

            var = ctk.BooleanVar(value=self._get_config_value(key, True))
            self.vis_vars[key] = var

            ctk.CTkCheckBox(
                row, text=label, variable=var,
                font=self._get_font("font_size_label"),
                text_color=self.theme.get("text_primary", "#e0e0e0"),
                fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
                hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
                command=lambda k=key: self._on_vis_changed(k)
            ).pack(side="left", padx=5)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _get_config_value(self, key, default):
        if self.app and hasattr(self.app, 'config'):
            return self.app.config.get(key, default)
        return default

    def _set_config_value(self, key, value):
        if self.app and hasattr(self.app, 'config'):
            self.app.config[key] = value
            if hasattr(self.app, 'fishing') and self.app.fishing:
                self.app.fishing._last_water_check_time = 0

    def _on_vis_changed(self, key):
        value = self.vis_vars[key].get()
        self._set_config_value(key, value)

    def _anchor_to_bottom_left(self, height):
        """🆕 Привязывает окно к левому нижнему углу экрана с учётом панели задач."""
        screen_h = self.winfo_screenheight()
        # 🆕 Отступ из конфига (по умолчанию 60px)
        y_pos = max(10, screen_h - height - self.bottom_margin)
        self.geometry(f"{self.BASE_WIDTH}x{height}+0+{y_pos}")

    def _update_window_size(self):
        """🆕 Пересчитывает размер и привязывает к левому нижнему углу."""
        extra = 0
        if self._detail_open:
            extra += self.PANEL_HEIGHT
        if self._settings_open:
            extra += self.PANEL_HEIGHT
        new_height = self.BASE_HEIGHT + extra
        self._anchor_to_bottom_left(new_height)

    def _toggle_detail(self):
        """🆕 Переключает панель 'Подробно' — окно увеличивается/уменьшается."""
        self._detail_open = not self._detail_open
        if self._detail_open:
            self.detail_panel.pack(fill="x", padx=10, pady=5, after=self.image_container)
            self.detail_btn.configure(
                text="🔍 Скрыть",
                fg_color=self.theme.get("bg_button_primary", "#1f6aa5")
            )
        else:
            self.detail_panel.pack_forget()
            self.detail_btn.configure(
                text="🔍 Подробно",
                fg_color=self.theme.get("bg_button_secondary", "#2c3e50")
            )
        self._update_window_size()

    def _toggle_settings(self):
        """🆕 Переключает панель настроек — окно увеличивается/уменьшается."""
        self._settings_open = not self._settings_open
        if self._settings_open:
            for key, var in self.vis_vars.items():
                var.set(self._get_config_value(key, True))
            self.settings_panel.pack(fill="x", padx=10, pady=5)
            self.settings_btn.configure(
                text="⚙ Скрыть",
                fg_color=self.theme.get("bg_button_primary", "#1f6aa5")
            )
        else:
            self.settings_panel.pack_forget()
            self.settings_btn.configure(
                text="⚙ Настройки",
                fg_color=self.theme.get("bg_button_secondary", "#2c3e50")
            )
        self._update_window_size()

    def update_frame(self, tk_image):
        """Обновляет изображение превью."""
        try:
            self.image_label.configure(image=tk_image, text="")
            self._current_image = tk_image
        except Exception:
            pass

    def update_stats(self, state, score, cursor_pos, has_water, water_percent, water_center):
        """Обновляет статистику в панели 'Подробно'."""
        if not self._detail_open:
            return
        cursor_str = f"({cursor_pos[0]}, {cursor_pos[1]})" if cursor_pos else "—"
        water_str = f"{water_percent:.1f}%" if has_water else "—"
        text = (
            f"📊 Состояние: {state}\n"
            f"🎯 Score: {score:.3f}\n"
            f"🖱 Курсор: {cursor_str}\n"
            f"💧 Вода: {water_str}\n"
        )
        self.stats_label.configure(text=text)

    def _on_close(self):
        self.is_open = False
        if self.on_close_callback:
            try:
                self.on_close_callback()
            except Exception:
                pass
        try:
            self.destroy()
        except Exception:
            pass
