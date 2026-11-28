"""
Вкладка "Визуал" в окне настроек.
🆕 Рабочая прокрутка колесиком мыши для Linux и Windows.
🆕 Галочки "Вкл." и "Видео" снизу под RGB.
🆕 Две колонки + прокрутка.
"""
import customtkinter as ctk
from ..widgets.tooltip import Tooltip


class VisualizerTab:
    def __init__(self, parent, config, on_change, font_size=14, theme=None, font_manager=None):
        self.config = config
        self.theme = theme or {}
        self.font_manager = font_manager
        self.on_change = on_change
        self.font_size = font_size
        self._rows = []
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _build(self, parent):
        # Заголовок
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(5, 2))
        ctk.CTkLabel(
            header, text="👁 Визуал",
            font=self._get_font("font_size_section", "bold"),
            text_color=self.theme.get("text_accent", "#d4a843")
        ).pack(side="left")

        # 🆕 Canvas с прокруткой
        self._canvas = ctk.CTkCanvas(
            parent,
            bg=self.theme.get("bg_main", "#1a1f2e"),
            highlightthickness=0,
            borderwidth=0
        )
        self._canvas.pack(fill="both", expand=True, padx=10, pady=2)

        # Внутренний фрейм для колонок
        self._columns_frame = ctk.CTkFrame(self._canvas, fg_color=self.theme.get("bg_main", "#1a1f2e"))
        self._canvas.create_window((0, 0), window=self._columns_frame, anchor="nw")

        left_column = ctk.CTkFrame(self._columns_frame, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))

        right_column = ctk.CTkFrame(self._columns_frame, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Визуализаторы (все 5)
        visualizers = [
            ("vis_water", "💧 Маска воды", "#00ff00", True, True, True),
            ("vis_bobber", "🎣 Маска поплавка", "#ff69ff", True, True, True),
            ("vis_zones", "🟪 Зоны поиска", "#b400b4", True, True, False),
            ("vis_line", "📏 Линия поиска", "#ffff00", True, True, False),
            ("vis_cursor", "🖱 Курсор", "#00ffff", True, True, False),
        ]

        # Первые 2 в левую колонку, остальные 3 в правую
        for i, (prefix, label, default_color, default_enabled, default_show, has_tool) in enumerate(visualizers):
            target = left_column if i < 2 else right_column
            row = VisualizerRow(
                target, prefix, label, default_color,
                default_enabled, default_show, has_tool,
                self.config, self.on_change,
                self.font_size, self.theme, self.font_manager
            )
            self._rows.append(row)

        # 🆕 Обновляем размер canvas после заполнения
        self._columns_frame.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

        # 🆕 Прокрутка колесиком — Linux (Button-4/5) и Windows (MouseWheel)
        def _on_mousewheel(event):
            # Linux: Button-4 = вверх, Button-5 = вниз
            if event.num == 4:
                self._canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self._canvas.yview_scroll(1, "units")

        def _on_mousewheel_win(event):
            # Windows
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # 🆕 Привязываем к родителю (главному окну), чтобы работало везде
        parent.bind("<Button-4>", _on_mousewheel)
        parent.bind("<Button-5>", _on_mousewheel)
        parent.bind("<MouseWheel>", _on_mousewheel_win)

        # Также привязываем к canvas и всем дочерним фреймам
        self._canvas.bind("<Button-4>", _on_mousewheel)
        self._canvas.bind("<Button-5>", _on_mousewheel)
        self._canvas.bind("<MouseWheel>", _on_mousewheel_win)
        left_column.bind("<Button-4>", _on_mousewheel)
        left_column.bind("<Button-5>", _on_mousewheel)
        right_column.bind("<Button-4>", _on_mousewheel)
        right_column.bind("<Button-5>", _on_mousewheel)

        # 🆕 Обновление scrollregion при изменении размера
        def _on_frame_configure(event):
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._columns_frame.bind("<Configure>", _on_frame_configure)

    def destroy(self):
        """Очистка привязок при закрытии."""
        try:
            parent = self._canvas.master
            parent.unbind("<Button-4>")
            parent.unbind("<Button-5>")
            parent.unbind("<MouseWheel>")
        except Exception:
            pass


class VisualizerRow:
    def __init__(self, parent, key_prefix, label, default_color,
                 default_enabled, default_show, has_tool_toggle,
                 config, on_change, font_size, theme, font_manager):
        self.key_prefix = key_prefix
        self.config = config
        self.on_change = on_change
        self.theme = theme or {}
        self.font_size = font_size
        self.font_manager = font_manager
        self.has_tool_toggle = has_tool_toggle

        # === Основной фрейм блока ===
        self.frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            corner_radius=6
        )
        self.frame.pack(fill="x", pady=3)
        self.frame.configure(height=180)
        self.frame.pack_propagate(False)

        # === Верхняя строка: название слева + HEX справа ===
        top_row = ctk.CTkFrame(self.frame, fg_color="transparent")
        top_row.pack(fill="x", padx=8, pady=(6, 0))

        ctk.CTkLabel(
            top_row, text=label,
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            anchor="w"
        ).pack(side="left", padx=3)

        # HEX поле справа
        color = config.get(f"{key_prefix}_color", default_color)
        self.hex_entry = ctk.CTkEntry(
            top_row, width=70, height=22,
            font=self._get_font("font_size_value"),
            fg_color=self.theme.get("bg_slider", "#3a4152"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            border_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            border_width=1, corner_radius=4, justify="center"
        )
        self.hex_entry.insert(0, color.upper())
        self.hex_entry.pack(side="right", padx=3)
        self.hex_entry.bind("<Return>", self._on_hex_submit)
        self.hex_entry.bind("<FocusOut>", self._on_hex_submit)

        # === Средняя часть: RGB ползунки от края до края ===
        r, g, b = self._hex_to_rgb(color)
        rgb_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        rgb_frame.pack(fill="x", padx=8, pady=2)

        self.sliders = {}
        for ch, val, color_ch in [("R", r, "#ff4444"), ("G", g, "#44ff44"), ("B", b, "#4444ff")]:
            ch_row = ctk.CTkFrame(rgb_frame, fg_color="transparent")
            ch_row.pack(fill="x", pady=0)

            ctk.CTkLabel(
                ch_row, text=ch,
                font=self._get_font("font_size_label", "bold"),
                text_color=color_ch, width=12
            ).pack(side="left", padx=1)

            slider = ctk.CTkSlider(
                ch_row, from_=0, to=255, number_of_steps=255,
                button_color="#888888", progress_color="#888888",
                fg_color=self.theme.get("bg_slider", "#3a4152"),
                height=14
            )
            slider.set(val)
            slider.pack(side="left", fill="x", expand=True, padx=2)
            slider.configure(command=lambda v, ch=ch: self._on_rgb_changed(ch, v))
            self.sliders[ch] = slider

        # === Spacer — минимальный ===
        spacer = ctk.CTkFrame(self.frame, fg_color="transparent", height=10)
        spacer.pack(fill="x")
        spacer.pack_propagate(False)

        # === Нижняя строка: галочки Вкл и Видео ===
        checks_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        checks_frame.pack(fill="x", padx=8, pady=(0, 6))

        # Галочка "Вкл." с текстом (только для воды и поплавка)
        if has_tool_toggle:
            self.enabled_var = ctk.BooleanVar(
                value=config.get(f"{key_prefix}_enabled", default_enabled)
            )
            self.check_enabled = ctk.CTkCheckBox(
                checks_frame, text="Вкл.", variable=self.enabled_var, width=60,
                fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
                hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
                font=self._get_font("font_size_label"),
                text_color=self.theme.get("text_primary", "#e0e0e0"),
                command=self._on_enabled_changed
            )
            self.check_enabled.pack(side="left", padx=3)
            Tooltip(self.check_enabled, "Включить как инструмент детекта",
                    theme=self.theme, font_manager=self.font_manager)
        else:
            ctk.CTkFrame(checks_frame, width=60, height=24, fg_color="transparent").pack(side="left", padx=3)
            self.enabled_var = None
            self.check_enabled = None

        # Галочка "Видео" с текстом
        self.show_var = ctk.BooleanVar(
            value=config.get(f"{key_prefix}_show", default_show)
        )
        self.check_show = ctk.CTkCheckBox(
            checks_frame, text="Видео", variable=self.show_var, width=60,
            fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._on_show_changed
        )
        self.check_show.pack(side="left", padx=3)
        Tooltip(self.check_show, "Показывать в окне видео",
                theme=self.theme, font_manager=self.font_manager)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _hex_to_rgb(self, hex_val):
        h = hex_val.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, r, g, b):
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

    def _on_enabled_changed(self):
        val = self.enabled_var.get()
        self.config[f"{self.key_prefix}_enabled"] = val
        if self.on_change:
            self.on_change(f"{self.key_prefix}_enabled", val)

    def _on_show_changed(self):
        val = self.show_var.get()
        self.config[f"{self.key_prefix}_show"] = val
        if self.on_change:
            self.on_change(f"{self.key_prefix}_show", val)

    def _on_rgb_changed(self, channel, value):
        r = int(self.sliders["R"].get())
        g = int(self.sliders["G"].get())
        b = int(self.sliders["B"].get())
        if channel == "R": r = int(value)
        elif channel == "G": g = int(value)
        elif channel == "B": b = int(value)
        hex_val = self._rgb_to_hex(r, g, b)
        self.config[f"{self.key_prefix}_color"] = hex_val
        self.hex_entry.delete(0, "end")
        self.hex_entry.insert(0, hex_val.upper())
        if self.on_change:
            self.on_change(f"{self.key_prefix}_color", hex_val)

    def _on_hex_submit(self, event=None):
        hex_val = self.hex_entry.get().strip()
        if hex_val.startswith("#") and len(hex_val) == 7:
            try:
                int(hex_val[1:], 16)
                r, g, b = self._hex_to_rgb(hex_val)
                self.sliders["R"].set(r)
                self.sliders["G"].set(g)
                self.sliders["B"].set(b)
                self.config[f"{self.key_prefix}_color"] = hex_val
                if self.on_change:
                    self.on_change(f"{self.key_prefix}_color", hex_val)
            except ValueError:
                pass
