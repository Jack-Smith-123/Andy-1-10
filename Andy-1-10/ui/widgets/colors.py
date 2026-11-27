"""
Виджет выбора цвета (HSV).
"""
import customtkinter as ctk


class ColorRow(ctk.CTkFrame):
    """Строка: Название + 3 ползунка HSV + Значение."""

    def __init__(self, parent, label_text, config_keys, min_vals, max_vals,
                 config, theme, font_manager, on_change=None):
        super().__init__(parent, fg_color=theme.get("bg_main", "#1a1f2e"), corner_radius=6)
        self.config = config
        self.config_keys = config_keys
        self.on_change = on_change

        ctk.CTkLabel(
            self, text=label_text,
            font=font_manager.get_font("font_size_slider_label"),
            text_color=theme.get("text_primary", "#e0e0e0"),
            width=150, anchor="w"
        ).pack(side="left", padx=5, pady=5)

        self.sliders = []
        self.labels = []
        
        for i, (key, mn, mx) in enumerate(zip(config_keys, min_vals, max_vals)):
            val = config.get(key, mn)
            
            slider = ctk.CTkSlider(
                self, from_=mn, to=mx, width=60,
                button_color=theme.get("bg_button_primary", "#1f6aa5"),
                progress_color=theme.get("bg_button_primary", "#1f6aa5"),
                fg_color=theme.get("bg_slider", "#3a4152")
            )
            slider.set(val)
            slider.pack(side="left", padx=2)

            lbl = ctk.CTkLabel(
                self, text=str(int(val)),
                font=font_manager.get_font("font_size_value", "bold"), width=30,
                text_color=theme.get("text_primary", "#e0e0e0")
            )
            lbl.pack(side="left", padx=2)

            def make_handler(k=key, l=lbl):
                return lambda v: self._update(k, v, l)
            
            slider.configure(command=make_handler())
            self.sliders.append(slider)
            self.labels.append(lbl)

    def _update(self, key, value, label):
        val = int(float(value))
        label.configure(text=str(val))
        self.config[key] = val
        if self.on_change:
            self.on_change()