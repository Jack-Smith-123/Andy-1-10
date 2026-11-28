"""
Виджет строки с ползунком и полем ввода числа.
Layout: [Название] [Ползунок] [Поле ввода]
🆕 Поддержка колёсика мыши (шаг настраиваемый).
"""
import customtkinter as ctk
from .hints import Tooltip


class SliderRow(ctk.CTkFrame):
    """Строка: Название + Ползунок + Поле ввода."""

    def __init__(self, parent, label_text, config_key, min_val, max_val, 
                 config, theme, font_manager, on_change=None, tooltip_text=None,
                 tooltip_delay=1.0, scroll_step=None):
        """
        Args:
            scroll_step: шаг колёсика. Если None — определяется автоматически:
                         1 для целых значений, 0.01 для дробных.
        """
        super().__init__(parent, fg_color=theme.get("bg_main", "#1a1f2e"), corner_radius=6)
        self.config = config
        self.config_key = config_key
        self.on_change = on_change
        self.min_val = min_val
        self.max_val = max_val

        current = config.get(config_key, min_val)
        is_int = isinstance(current, int)
        display_val = str(int(current)) if is_int else f"{current:.2f}"

        # Автоопределение шага колёсика
        if scroll_step is None:
            self.scroll_step = 1 if is_int else 0.01
        else:
            self.scroll_step = scroll_step

        # 1. Название (с подсказкой)
        lbl = ctk.CTkLabel(
            self, text=label_text,
            font=font_manager.get_font("font_size_slider_label"),
            text_color=theme.get("text_primary", "#e0e0e0"),
            width=180, anchor="w"
        )
        lbl.pack(side="left", padx=5, pady=5)

        if tooltip_text:
            Tooltip(lbl, tooltip_text, theme, delay=tooltip_delay)

        # 2. Ползунок
        steps = max(1, int((max_val - min_val) * 100))
        self.slider = ctk.CTkSlider(
            self, from_=min_val, to=max_val, number_of_steps=steps,
            width=120,
            button_color=theme.get("bg_button_primary", "#1f6aa5"),
            progress_color=theme.get("bg_button_primary", "#1f6aa5"),
            fg_color=theme.get("bg_slider", "#3a4152")
        )
        self.slider.set(current)
        self.slider.pack(side="left", padx=5, pady=5)

        # 3. Поле ввода числа (СПРАВА)
        self.entry = ctk.CTkEntry(
            self, width=70,
            font=font_manager.get_font("font_size_value", "bold"),
            fg_color=theme.get("bg_panel", "#2a3142"),
            text_color=theme.get("text_primary", "#e0e0e0"),
            border_color=theme.get("bg_slider", "#3a4152")
        )
        self.entry.insert(0, display_val)
        self.entry.pack(side="left", padx=5, pady=5)
        self.entry.bind("<Return>", lambda e: self._on_entry_change())
        self.entry.bind("<FocusOut>", lambda e: self._on_entry_change())

        # 4. 🆕 Привязка колёсика мыши к ползунку
        self.slider.bind("<Button-4>", lambda e: self._on_scroll(1))    # Linux: вверх
        self.slider.bind("<Button-5>", lambda e: self._on_scroll(-1))   # Linux: вниз
        self.slider.bind("<MouseWheel>", self._on_mousewheel)           # Windows/macOS

        # Также привязываем к полю ввода (чтобы колёсико работало и там)
        self.entry.bind("<Button-4>", lambda e: self._on_scroll(1))
        self.entry.bind("<Button-5>", lambda e: self._on_scroll(-1))
        self.entry.bind("<MouseWheel>", self._on_mousewheel)

        self.slider.configure(command=self._on_slider_change)

    def _on_slider_change(self, value):
        is_int = isinstance(self.config.get(self.config_key, 0), int)
        val = int(value) if is_int else float(f"{value:.2f}")
        self.entry.delete(0, "end")
        self.entry.insert(0, str(val))
        self.config[self.config_key] = val
        if self.on_change:
            self.on_change()

    def _on_entry_change(self):
        try:
            val = float(self.entry.get())
            val = max(self.min_val, min(self.max_val, val))
            is_int = isinstance(self.config.get(self.config_key, 0), int)
            val = int(val) if is_int else val
            self.slider.set(val)
            self.config[self.config_key] = val
            if self.on_change:
                self.on_change()
        except ValueError:
            pass

    def _on_scroll(self, direction):
        """
        Обработка колёсика мыши.
        direction: 1 = вверх (увеличить), -1 = вниз (уменьшить).
        """
        try:
            current = float(self.slider.get())
            new_val = current + direction * self.scroll_step
            new_val = max(self.min_val, min(self.max_val, new_val))
            
            # Округление для целых значений
            is_int = isinstance(self.config.get(self.config_key, 0), int)
            if is_int:
                new_val = round(new_val)
            else:
                new_val = round(new_val, 2)
            
            self.slider.set(new_val)
            self.entry.delete(0, "end")
            self.entry.insert(0, str(int(new_val) if is_int else f"{new_val:.2f}"))
            self.config[self.config_key] = new_val
            
            if self.on_change:
                self.on_change()
        except Exception:
            pass

    def _on_mousewheel(self, event):
        """Обработка колёсика для Windows/macOS."""
        # event.delta > 0 = вверх, < 0 = вниз
        direction = 1 if event.delta > 0 else -1
        self._on_scroll(direction)