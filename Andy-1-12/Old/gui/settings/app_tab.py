"""
Вкладка "Приложение" в окне настроек.
🆕 Подвкладки: Тема, Шрифт, Видео.
Настройки: тема оформления, шрифт, размер шрифта, отступ окна Видео.
"""
import customtkinter as ctk
from ..themes import THEMES, get_theme_names, get_theme_by_name


class AppTab:
    def __init__(self, parent, config, font_size=14, theme=None,
                 on_theme_editor=None, font_manager=None):
        self.config = config
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self.on_theme_editor = on_theme_editor
        self._theme_rows = []
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        # === Переключатель подвкладок ===
        tabs_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tabs_frame.pack(fill="x", padx=0, pady=(0, 5))
        self.tab_switcher = ctk.CTkSegmentedButton(
            tabs_frame,
            values=["🎨 Тема", "🔤 Шрифт", "🎥 Видео"],
            command=self._switch_tab,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            selected_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            selected_hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            unselected_color=self.theme.get("bg_slider", "#3a4152"),
            unselected_hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            corner_radius=8,
            border_width=0,
            font=ctk.CTkFont(size=self.font_size - 1, weight="bold")
        )
        self.tab_switcher.pack(side="left", padx=10, pady=5)

        # === Контейнер для содержимого подвкладок ===
        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.theme_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.font_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.video_frame = ctk.CTkFrame(content_frame, fg_color="transparent")

        self._build_theme_tab()
        self._build_font_tab()
        self._build_video_tab()

        self._switch_tab("🎨 Тема")

    def _switch_tab(self, name):
        self.theme_frame.pack_forget()
        self.font_frame.pack_forget()
        self.video_frame.pack_forget()

        if name == "🎨 Тема":
            self.theme_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "🔤 Шрифт":
            self.font_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "🎥 Видео":
            self.video_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def _build_theme_tab(self):
        """Подвкладка "Тема оформления"."""
        ctk.CTkLabel(
            self.theme_frame, text="🎨 Тема оформления",
            font=self._get_font("font_size_section", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 8))

        self._theme_container = ctk.CTkFrame(self.theme_frame, fg_color=self.theme.get("bg_panel", "#2a3142"), corner_radius=6)
        self._theme_container.pack(fill="x", padx=10)
        self._rebuild_theme_list(self._theme_container)

        ctk.CTkButton(
            self.theme_frame, text="✨ Создать свою тему",
            font=self._get_font("font_size_button_secondary"),
            height=32,
            fg_color=self.theme.get("bg_button_secondary", "#2c3e50"),
            hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._open_theme_editor
        ).pack(pady=(8, 10), padx=10, fill="x")

    def _build_font_tab(self):
        """Подвкладка "Шрифт"."""
        ctk.CTkLabel(
            self.font_frame, text="🔤 Шрифт",
            font=self._get_font("font_size_section", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 8))

        font_frame = ctk.CTkFrame(self.font_frame, fg_color=self.theme.get("bg_panel", "#2a3142"), corner_radius=6)
        font_frame.pack(fill="x", padx=10)

        # Семейство шрифта
        family_row = ctk.CTkFrame(font_frame, fg_color="transparent")
        family_row.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(
            family_row, text="Семейство:",
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            width=80, anchor="w"
        ).pack(side="left")

        self.font_family_var = ctk.StringVar(
            value=self.config.get("font_family", "Arial")
        )
        self.font_family_combo = ctk.CTkComboBox(
            family_row,
            values=["Arial", "Verdana", "Tahoma", "Courier New", "Times New Roman", "Georgia"],
            variable=self.font_family_var,
            width=150, height=28,
            font=self._get_font("font_size_value"),
            fg_color=self.theme.get("bg_slider", "#3a4152"),
            button_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            button_hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            dropdown_fg_color=self.theme.get("bg_panel", "#2a3142"),
            dropdown_text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=lambda v: self.config.update({"font_family": v})
        )
        self.font_family_combo.pack(side="left", padx=5)

        # Размер шрифта
        size_row = ctk.CTkFrame(font_frame, fg_color="transparent")
        size_row.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(
            size_row, text="Размер:",
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            width=80, anchor="w"
        ).pack(side="left")

        self.font_size_var = ctk.IntVar(
            value=int(self.config.get("font_size", 13))
        )
        self.font_size_slider = ctk.CTkSlider(
            size_row, from_=10, to=20, number_of_steps=10,
            variable=self.font_size_var,
            width=120, height=20,
            button_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            progress_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            fg_color=self.theme.get("bg_slider", "#3a4152"),
            command=self._on_font_size_changed
        )
        self.font_size_slider.pack(side="left", padx=5)

        self.font_size_label = ctk.CTkLabel(
            size_row, text=str(self.font_size_var.get()),
            font=self._get_font("font_size_value", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843"),
            width=30
        )
        self.font_size_label.pack(side="left", padx=5)

        # Поле ввода размера шрифта
        self.font_size_entry = ctk.CTkEntry(
            size_row, width=50, height=26,
            font=self._get_font("font_size_value"),
            fg_color=self.theme.get("bg_slider", "#3a4152"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            border_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            border_width=1, corner_radius=4, justify="center"
        )
        self.font_size_entry.insert(0, str(self.font_size_var.get()))
        self.font_size_entry.pack(side="left", padx=5)
        self.font_size_entry.bind("<Return>", self._on_font_size_entry_submit)
        self.font_size_entry.bind("<FocusOut>", self._on_font_size_entry_submit)

    def _build_video_tab(self):
        """🆕 Подвкладка "Окно Видео"."""
        ctk.CTkLabel(
            self.video_frame, text="🎥 Окно Видео",
            font=self._get_font("font_size_section", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(anchor="w", padx=10, pady=(10, 8))

        preview_frame = ctk.CTkFrame(self.video_frame, fg_color=self.theme.get("bg_panel", "#2a3142"), corner_radius=6)
        preview_frame.pack(fill="x", padx=10)

        # Ползунок отступа
        margin_row = ctk.CTkFrame(preview_frame, fg_color="transparent")
        margin_row.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            margin_row, text="📏 Отступ от низа (px):",
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            width=150, anchor="w"
        ).pack(side="left")

        self.bottom_margin_var = ctk.IntVar(
            value=int(self.config.get("preview_bottom_margin", 60))
        )
        self.bottom_margin_slider = ctk.CTkSlider(
            margin_row, from_=20, to=150, number_of_steps=13,
            variable=self.bottom_margin_var,
            width=120, height=20,
            button_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            progress_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            fg_color=self.theme.get("bg_slider", "#3a4152"),
            command=self._on_margin_changed
        )
        self.bottom_margin_slider.pack(side="left", padx=5)

        # Метка текущего значения
        self.bottom_margin_label = ctk.CTkLabel(
            margin_row, text=str(self.bottom_margin_var.get()),
            font=self._get_font("font_size_value", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843"),
            width=30
        )
        self.bottom_margin_label.pack(side="left", padx=5)

        # Поле ввода отступа
        self.bottom_margin_entry = ctk.CTkEntry(
            margin_row, width=50, height=26,
            font=self._get_font("font_size_value"),
            fg_color=self.theme.get("bg_slider", "#3a4152"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            border_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            border_width=1, corner_radius=4, justify="center"
        )
        self.bottom_margin_entry.insert(0, str(self.bottom_margin_var.get()))
        self.bottom_margin_entry.pack(side="left", padx=5)
        self.bottom_margin_entry.bind("<Return>", self._on_margin_entry_submit)
        self.bottom_margin_entry.bind("<FocusOut>", self._on_margin_entry_submit)

        # Подсказка
        hint = ctk.CTkLabel(
            preview_frame,
            text="💡 Отступ от нижнего края экрана. Увеличь, если панель задач Linux перекрывает окно.\n"
                 "XFCE: 40-50px, GNOME/KDE: 50-60px.",
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_secondary", "#a0a8b8"),
            justify="left"
        )
        hint.pack(padx=10, pady=(0, 10), anchor="w")

    def _rebuild_theme_list(self, parent):
        """Перестраивает список тем."""
        for row in self._theme_rows:
            row.frame.destroy()
        self._theme_rows = []

        theme_names = get_theme_names()
        current_theme_key = self.config.get("theme", "albion_dark")

        for theme_name in theme_names:
            theme_key = get_theme_by_name(theme_name)
            row = ThemeRow(
                parent, theme_name, theme_key,
                theme_key == current_theme_key,
                self.theme, self.font_manager, self.font_size,
                self._on_theme_selected
            )
            self._theme_rows.append(row)

    def _on_theme_selected(self, theme_key):
        """Выбрана тема — сохраняем в pending."""
        self._pending_theme = theme_key

    def get_pending_theme(self):
        """Возвращает выбранную тему."""
        return getattr(self, '_pending_theme', self.config.get("theme", "albion_dark"))

    def get_pending_font_family(self):
        return self.font_family_var.get()

    def _on_font_size_changed(self, value):
        val = int(float(value))
        self.font_size_var.set(val)
        self.font_size_label.configure(text=str(val))
        self.font_size_entry.delete(0, "end")
        self.font_size_entry.insert(0, str(val))
        self.config["font_size"] = val

    def _on_font_size_entry_submit(self, event=None):
        try:
            val = int(self.font_size_entry.get().strip())
            val = max(10, min(20, val))
            self.font_size_var.set(val)
            self.font_size_slider.set(val)
            self.font_size_label.configure(text=str(val))
            self.font_size_entry.delete(0, "end")
            self.font_size_entry.insert(0, str(val))
            self.config["font_size"] = val
        except ValueError:
            self.font_size_entry.delete(0, "end")
            self.font_size_entry.insert(0, str(self.font_size_var.get()))

    def _on_margin_changed(self, value):
        val = int(float(value))
        self.bottom_margin_var.set(val)
        self.bottom_margin_label.configure(text=str(val))
        self.bottom_margin_entry.delete(0, "end")
        self.bottom_margin_entry.insert(0, str(val))
        self.config["preview_bottom_margin"] = val

    def _on_margin_entry_submit(self, event=None):
        try:
            val = int(self.bottom_margin_entry.get().strip())
            val = max(20, min(150, val))
            self.bottom_margin_var.set(val)
            self.bottom_margin_slider.set(val)
            self.bottom_margin_label.configure(text=str(val))
            self.bottom_margin_entry.delete(0, "end")
            self.bottom_margin_entry.insert(0, str(val))
            self.config["preview_bottom_margin"] = val
        except ValueError:
            self.bottom_margin_entry.delete(0, "end")
            self.bottom_margin_entry.insert(0, str(self.bottom_margin_var.get()))

    def _open_theme_editor(self):
        if self.on_theme_editor:
            self.on_theme_editor()


class ThemeRow:
    """Строка с темой в списке."""
    def __init__(self, parent, theme_name, theme_key, is_selected,
                 theme, font_manager, font_size, on_select):
        self.theme_key = theme_key
        self.on_select = on_select

        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.pack(fill="x", padx=10, pady=4)

        # Радио-кнопка
        self.radio_var = ctk.StringVar(value=theme_key if is_selected else "")
        self.radio = ctk.CTkRadioButton(
            self.frame, text="", variable=self.radio_var, value=theme_key,
            fg_color=theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=theme.get("bg_button_primary_hover", "#1a5a8a"),
            command=lambda: on_select(theme_key)
        )
        self.radio.pack(side="left", padx=5)

        # Название и описание
        info_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            info_frame, text=theme_name,
            font=ctk.CTkFont(size=font_size, weight="bold"),
            text_color=theme.get("text_primary", "#e0e0e0"),
            anchor="w"
        ).pack(fill="x")

        theme_data = THEMES.get(theme_key, {})
        description = theme_data.get("description", "")
        if description:
            ctk.CTkLabel(
                info_frame, text=description,
                font=ctk.CTkFont(size=font_size - 2),
                text_color=theme.get("text_secondary", "#a0a8b8"),
                anchor="w", justify="left"
            ).pack(fill="x")
