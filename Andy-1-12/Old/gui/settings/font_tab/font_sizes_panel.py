"""
Прокручиваемая панель с ползунками размеров шрифтов.
Без внутренних отступов — выравнивание контролируется на уровне font_tab.py.
"""
import customtkinter as ctk
import tkinter as tk


FONT_SIZE_BLOCKS = [
    ("🏷 Заголовки", [
        ("Заголовок окна", "font_size_title", 12, 30),
        ("Заголовок в шапке", "font_size_header", 12, 30),
        ("Заголовки секций", "font_size_section", 12, 30),
    ]),
    ("🔘 Кнопки", [
        ("Основные (Старт/Стоп)", "font_size_button_primary", 12, 30),
        ("Вторичные", "font_size_button_secondary", 12, 30),
        ("Действует/Ждёт", "font_size_button_action", 12, 30),
        ("Кнопка закрытия", "font_size_button_close", 12, 30),
    ]),
    ("📝 Текст и метки", [
        ("Метки", "font_size_label", 10, 24),
        ("Значения", "font_size_value", 10, 24),
        ("Статус", "font_size_status", 10, 24),
        ("Метки ползунков", "font_size_slider_label", 10, 24),
    ]),
    ("📋 Вспомогательные", [
        ("Подсказки", "font_size_tooltip", 10, 24),
        ("Лог", "font_size_log", 10, 24),
        ("Название темы", "font_size_theme_name", 10, 24),
        ("Описание темы", "font_size_theme_desc", 8, 20),
    ]),
    ("👁 Превью", [
        ("FPS в превью", "font_size_preview_fps", 10, 24),
        ("Статистика", "font_size_preview_stats", 10, 24),
    ]),
]


class FontSizesPanel:
    def __init__(self, parent, config, theme=None, font_manager=None, on_change_callback=None):
        self.config = config
        self.theme = theme or {}
        self.font_manager = font_manager
        self.on_change = on_change_callback
        self._rows = []
        self._build(parent)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=13, weight=weight)

    def _build(self, parent):
        # Прокручиваемый контейнер (без отступов)
        canvas = tk.Canvas(
            parent,
            bg=self.theme.get("bg_panel", "#2a3142"),
            highlightthickness=0
        )
        scrollbar = ctk.CTkScrollbar(parent, command=canvas.yview, width=12)
        self._inner = ctk.CTkFrame(canvas, fg_color=self.theme.get("bg_panel", "#2a3142"))
        self._inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self._inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Блоки ползунков
        for block_title, items in FONT_SIZE_BLOCKS:
            self._add_block_label(block_title)
            self._build_block(items)

        # Отступ внизу
        ctk.CTkFrame(self._inner, fg_color="transparent", height=20).pack(fill="x")

    def _add_block_label(self, text):
        ctk.CTkLabel(
            self._inner, text=text,
            font=self._get_font("font_size_slider_label", "bold"),
            text_color=self.theme.get("text_secondary", "#a0a8b8")
        ).pack(anchor="w", padx=12, pady=(10, 3))

    def _build_block(self, items):
        for label, key, min_size, max_size in items:
            row = ctk.CTkFrame(
                self._inner,
                fg_color=self.theme.get("bg_main", "#1a1f2e"),
                corner_radius=6
            )
            row.pack(pady=3, padx=10, fill="x")  # ✅ Внутренний отступ ползунков

            ctk.CTkLabel(
                row, text=label,
                font=self._get_font("font_size_slider_label"),
                text_color=self.theme.get("text_primary", "#e0e0e0"),
                width=200, anchor="w"
            ).pack(side="left", padx=5, pady=5)

            slider = ctk.CTkSlider(
                row, from_=min_size, to=max_size,
                number_of_steps=max_size - min_size, width=100,
                button_color=self.theme.get("bg_button_primary", "#1f6aa5"),
                progress_color=self.theme.get("bg_button_primary", "#1f6aa5"),
                fg_color=self.theme.get("bg_slider", "#3a4152")
            )
            current = self.config.get(key, 13)
            slider.set(current)
            slider.pack(side="left", padx=5)

            value_lbl = ctk.CTkLabel(
                row, text=str(current),
                font=self._get_font("font_size_value", "bold"),
                width=30,
                text_color=self.theme.get("text_primary", "#e0e0e0")
            )
            value_lbl.pack(side="left", padx=5)

            def on_change(v, k=key, l=value_lbl):
                val = int(v)
                l.configure(text=str(val))
                self.config[k] = val
                if self.font_manager:
                    self.font_manager.clear_cache()
                if self.on_change:
                    self.on_change()

            slider.configure(command=on_change)
            self._rows.append({"key": key, "slider": slider, "label": value_lbl})
