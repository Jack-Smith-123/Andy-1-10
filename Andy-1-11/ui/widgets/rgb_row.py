"""
Виджет RGB с HEX-полем, превью цвета и двумя галочками.
Layout:
  [Название] [HEX поле] [Квадратик цвета]
  [Галочка Вкл] [Галочка Показать]
  R [ползунок] [поле]
  G [ползунок] [поле]
  B [ползунок] [поле]
"""
import customtkinter as ctk
from .hints import Tooltip


def _rgb_to_hex(r, g, b):
    return f"#{int(r):02X}{int(g):02X}{int(b):02X}"


def _hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    if len(hex_str) != 6:
        return 128, 128, 128
    try:
        return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))
    except ValueError:
        return 128, 128, 128


class RGBRow(ctk.CTkFrame):
    """RGB настройка с HEX, превью и двумя галочками."""

    def __init__(self, parent, label_text, config, theme, font_manager,
                 enable_key, show_key,
                 r_key, g_key, b_key,
                 on_change=None, tooltip_text=None, tooltip_delay=1.0):
        super().__init__(parent, fg_color=theme.get("bg_main", "#1a1f2e"), corner_radius=6)
        self.config = config
        self.on_change = on_change
        self.enable_key = enable_key
        self.show_key = show_key
        self.r_key = r_key
        self.g_key = g_key
        self.b_key = b_key
        self.theme = theme
        self.font_manager = font_manager

        # === Верхняя строка: Название + HEX + Превью ===
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=5, pady=5)

        # Название
        lbl = ctk.CTkLabel(
            top_frame, text=label_text,
            font=font_manager.get_font("font_size_label", "bold"),
            text_color=theme.get("text_primary", "#e0e0e0"),
            width=120, anchor="w"
        )
        lbl.pack(side="left", padx=5)
        if tooltip_text:
            Tooltip(lbl, tooltip_text, theme, delay=tooltip_delay)

        # HEX поле
        self.hex_entry = ctk.CTkEntry(
            top_frame, width=90,
            font=font_manager.get_font("font_size_value", "bold"),
            fg_color=theme.get("bg_panel", "#2a3142"),
            text_color=theme.get("text_primary", "#e0e0e0")
        )
        r = config.get(r_key, 128)
        g = config.get(g_key, 128)
        b = config.get(b_key, 128)
        self.hex_entry.insert(0, _rgb_to_hex(r, g, b))
        self.hex_entry.pack(side="left", padx=5)
        self.hex_entry.bind("<Return>", lambda e: self._on_hex_change())
        self.hex_entry.bind("<FocusOut>", lambda e: self._on_hex_change())

        # Квадратик превью цвета
        self.color_preview = ctk.CTkFrame(
            top_frame, width=30, height=30,
            fg_color=_rgb_to_hex(r, g, b), corner_radius=4
        )
        self.color_preview.pack(side="left", padx=5)
        self.color_preview.pack_propagate(False)

        # === Средняя строка: две галочки ===
        mid_frame = ctk.CTkFrame(self, fg_color="transparent")
        mid_frame.pack(fill="x", padx=5, pady=2)

        # Галочка Вкл (бот видит/не видит)
        self.enable_var = ctk.BooleanVar(value=config.get(enable_key, True))
        self.enable_cb = ctk.CTkCheckBox(
            mid_frame, text="Вкл (бот)", variable=self.enable_var,
            command=self._on_toggle, width=90,
            fg_color=theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=theme.get("bg_button_primary_hover", "#1a5a8a"),
            font=font_manager.get_font("font_size_label")
        )
        self.enable_cb.pack(side="left", padx=5)

        # Галочка Показать (я вижу/не вижу в Display)
        self.show_var = ctk.BooleanVar(value=config.get(show_key, True))
        self.show_cb = ctk.CTkCheckBox(
            mid_frame, text="Показать (Display)", variable=self.show_var,
            command=self._on_toggle, width=130,
            fg_color=theme.get("bg_button_secondary", "#2c3e50"),
            hover_color=theme.get("bg_button_secondary_hover", "#34495e"),
            font=font_manager.get_font("font_size_label")
        )
        self.show_cb.pack(side="left", padx=5)

        # === RGB каналы вертикально ===
        self._make_channel("R", r_key, r, theme, font_manager)
        self._make_channel("G", g_key, g, theme, font_manager)
        self._make_channel("B", b_key, b, theme, font_manager)

    def _make_channel(self, channel_name, key, value, theme, font_manager):
        """Один канал R/G/B: название + ползунок + поле. С колёсиком мыши."""
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=1)

        ctk.CTkLabel(
            row, text=channel_name, width=15,
            font=font_manager.get_font("font_size_value", "bold"),
            text_color=theme.get("text_primary", "#e0e0e0")
        ).pack(side="left", padx=5)

        slider = ctk.CTkSlider(
            row, from_=0, to=255, width=150,
            button_color=theme.get("bg_button_primary", "#1f6aa5"),
            progress_color=theme.get("bg_button_primary", "#1f6aa5"),
            fg_color=theme.get("bg_slider", "#3a4152")
        )
        slider.set(value)
        slider.pack(side="left", padx=5)

        entry = ctk.CTkEntry(
            row, width=50,
            font=font_manager.get_font("font_size_value", "bold"),
            fg_color=theme.get("bg_panel", "#2a3142"),
            text_color=theme.get("text_primary", "#e0e0e0")
        )
        entry.insert(0, str(int(value)))
        entry.pack(side="left", padx=5)

        def on_slider(v, k=key, e=entry):
            ival = int(float(v))
            e.delete(0, "end")
            e.insert(0, str(ival))
            self.config[k] = ival
            self._update_preview()
            if self.on_change:
                self.on_change()

        def on_entry(ev, k=key, s=slider):
            try:
                ival = int(float(entry.get()))
                ival = max(0, min(255, ival))
                s.set(ival)
                self.config[k] = ival
                self._update_preview()
                if self.on_change:
                    self.on_change()
            except ValueError:
                pass

        # 🆕 Колёсико мыши (шаг = 1 для RGB)
        def on_scroll(direction, k=key, s=slider, e=entry):
            try:
                current = int(float(s.get()))
                new_val = max(0, min(255, current + direction))
                s.set(new_val)
                e.delete(0, "end")
                e.insert(0, str(new_val))
                self.config[k] = new_val
                self._update_preview()
                if self.on_change:
                    self.on_change()
            except Exception:
                pass

        def on_mousewheel(event, k=key):
            direction = 1 if event.delta > 0 else -1
            on_scroll(direction, k=k)

        slider.configure(command=on_slider)
        entry.bind("<Return>", on_entry)
        entry.bind("<FocusOut>", on_entry)
        
        # Linux (X11)
        slider.bind("<Button-4>", lambda e, k=key: on_scroll(1, k=k))
        slider.bind("<Button-5>", lambda e, k=key: on_scroll(-1, k=k))
        entry.bind("<Button-4>", lambda e, k=key: on_scroll(1, k=key))
        entry.bind("<Button-5>", lambda e, k=key: on_scroll(-1, k=key))
        
        # Windows/macOS
        slider.bind("<MouseWheel>", on_mousewheel)
        entry.bind("<MouseWheel>", on_mousewheel)

    def _update_preview(self):
        """Обновляет HEX поле и квадратик цвета."""
        r = self.config.get(self.r_key, 0)
        g = self.config.get(self.g_key, 0)
        b = self.config.get(self.b_key, 0)
        hex_color = _rgb_to_hex(r, g, b)
        self.color_preview.configure(fg_color=hex_color)
        # Обновляем HEX поле только если пользователь не редактирует его сейчас
        if self.hex_entry.cget("state") != "disabled":
            current_hex = self.hex_entry.get().strip()
            if current_hex.upper() != hex_color.upper():
                self.hex_entry.delete(0, "end")
                self.hex_entry.insert(0, hex_color)

    def _on_hex_change(self):
        """Парсинг HEX в RGB."""
        hex_str = self.hex_entry.get().strip()
        r, g, b = _hex_to_rgb(hex_str)
        self.config[self.r_key] = r
        self.config[self.g_key] = g
        self.config[self.b_key] = b
        self.color_preview.configure(fg_color=hex_str)
        if self.on_change:
            self.on_change()

    def _on_toggle(self):
        """Сохраняем состояние галочек в конфиг."""
        self.config[self.enable_key] = self.enable_var.get()
        self.config[self.show_key] = self.show_var.get()
        if self.on_change:
            self.on_change()

    def get_enable(self):
        return self.enable_var.get()

    def get_show(self):
        return self.show_var.get()