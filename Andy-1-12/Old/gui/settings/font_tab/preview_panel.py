"""
Компактное превью шрифтов.
Без внутренних отступов — выравнивание контролируется на уровне font_tab.py.
"""
import customtkinter as ctk
from ...widgets.font_manager import AVAILABLE_FONTS


class PreviewPanel:
    def __init__(self, parent, config, theme=None, font_manager=None, on_change_callback=None):
        self.config = config
        self.theme = theme or {}
        self.font_manager = font_manager
        self.on_change = on_change_callback
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=13, weight=weight)

    def _build(self, parent):
        # Основной контейнер (прозрачный, без отступов)
        cols = ctk.CTkFrame(parent, fg_color="transparent")
        cols.pack(fill="both", expand=True, padx=0, pady=8)  # ✅ Убран padx

        # === Левая большая рамка "Превью:" ===
        preview_frame = ctk.CTkFrame(
            cols,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            corner_radius=6
        )
        preview_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # --- Заголовок "Превью:" ---
        ctk.CTkLabel(
            preview_frame, text="Превью:",
            font=self._get_font("font_size_slider_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843"),
            anchor="w"
        ).pack(anchor="w", padx=8, pady=(6, 4))

        # --- Нижняя часть: 2 колонки ---
        inner_cols = ctk.CTkFrame(preview_frame, fg_color="transparent")
        inner_cols.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        # Левая колонка: кнопки
        left_col = ctk.CTkFrame(inner_cols, fg_color="transparent")
        left_col.pack(side="left", fill="y", padx=(0, 8))

        self.btn_primary = ctk.CTkButton(
            left_col, text="Основная",
            font=self._get_font("font_size_button_primary", "bold"),
            height=28, width=110,
            fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            text_color=self.theme.get("text_primary", "#e0e0e0")
        )
        self.btn_primary.pack(pady=3)

        self.btn_secondary = ctk.CTkButton(
            left_col, text="Вторичная",
            font=self._get_font("font_size_button_secondary"),
            height=28, width=110,
            fg_color=self.theme.get("bg_button_secondary", "#2c3e50"),
            hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0")
        )
        self.btn_secondary.pack(pady=3)

        # Правая колонка: текст в один столбик
        mid_col = ctk.CTkFrame(inner_cols, fg_color="transparent")
        mid_col.pack(side="left", fill="both", expand=True)

        self.title_label = ctk.CTkLabel(
            mid_col, text="Заголовок",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            anchor="w", justify="left"
        )
        self.title_label.pack(anchor="w", pady=(0, 2))

        self.normal_label = ctk.CTkLabel(
            mid_col, text="Обычный текст",
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            anchor="w", justify="left"
        )
        self.normal_label.pack(anchor="w", pady=2)

        self.small_label = ctk.CTkLabel(
            mid_col, text="Мелкий текст",
            font=self._get_font("font_size_status"),
            text_color=self.theme.get("text_secondary", "#a0a8b8"),
            anchor="w", justify="left"
        )
        self.small_label.pack(anchor="w", pady=2)

        self.log_label = ctk.CTkLabel(
            mid_col, text="[12:34] Лог",
            font=self._get_font("font_size_log"),
            text_color=self.theme.get("text_secondary", "#a0a8b8"),
            anchor="w", justify="left"
        )
        self.log_label.pack(anchor="w", pady=(2, 0))

        # === Правая отдельная рамка "Семейство шрифта:" ===
        right_frame = ctk.CTkFrame(
            cols,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            corner_radius=6
        )
        right_frame.pack(side="right", fill="y", padx=(8, 0))

        ctk.CTkLabel(
            right_frame, text="Семейство шрифта:",
            font=self._get_font("font_size_slider_label", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843"),
            anchor="w"
        ).pack(anchor="w", padx=8, pady=(6, 2))

        current_family = self.config.get("font_family", "Arial")
        self._family_var = ctk.StringVar(value=current_family)

        self.family_menu = ctk.CTkOptionMenu(
            right_frame,
            variable=self._family_var,
            values=AVAILABLE_FONTS,
            width=110, height=28,
            fg_color=self.theme.get("bg_button_secondary", "#2c3e50"),
            button_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0")
        )
        self.family_menu.pack(anchor="w", padx=8, pady=(2, 6))

    def _on_family_changed(self, value):
        self.config["font_family"] = value
        if self.font_manager:
            self.font_manager.clear_cache()
        if self.on_change:
            self.on_change()

    def update_fonts(self):
        self.btn_primary.configure(font=self._get_font("font_size_button_primary", "bold"))
        self.btn_secondary.configure(font=self._get_font("font_size_button_secondary"))
        self.title_label.configure(font=self._get_font("font_size_header", "bold"))
        self.normal_label.configure(font=self._get_font("font_size_label"))
        self.small_label.configure(font=self._get_font("font_size_status"))
        self.log_label.configure(font=self._get_font("font_size_log"))

    def get_pending_font_family(self):
        return self._family_var.get()
