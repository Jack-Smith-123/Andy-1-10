"""
Всплывающие подсказки с задержкой.
"""
import customtkinter as ctk


class Tooltip:
    """Всплывающая подсказка при наведении с задержкой."""

    def __init__(self, widget, text, theme=None, delay=1.0):
        self.widget = widget
        self.text = text
        self.theme = theme or {}
        self.delay = delay  # Задержка в секундах
        self.tooltip = None
        self._after_id = None
        
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<Button-1>", self._on_leave)  # Скрыть при клике

    def _on_enter(self, event=None):
        """Начало наведения — запускаем таймер."""
        if self._after_id:
            self.widget.after_cancel(self._after_id)
        self._after_id = self.widget.after(int(self.delay * 1000), self.show)

    def _on_leave(self, event=None):
        """Уход курсора — отменяем показ и скрываем."""
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        self.hide()

    def show(self, event=None):
        """Показать подсказку."""
        if self.tooltip:
            return
        
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        
        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        self.tooltip.attributes("-topmost", True)
        
        label = ctk.CTkLabel(
            self.tooltip, text=self.text,
            font=ctk.CTkFont(size=11),
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            corner_radius=4,
            wraplength=250
        )
        label.pack(ipadx=8, ipady=5, padx=5, pady=5)

    def hide(self, event=None):
        """Скрыть подсказку."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None