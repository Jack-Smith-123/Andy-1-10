"""
Универсальная всплывающая подсказка (tooltip).
Шрифт через FontManager (font_size_tooltip).
"""
import customtkinter as ctk
import tkinter as tk


class Tooltip:
    def __init__(self, widget, text, delay_show=400, delay_hide=800, theme=None, font_manager=None):
        self.widget = widget
        self.text = text
        self.delay_show = delay_show
        self.delay_hide = delay_hide
        self.theme = theme or {}
        self.font_manager = font_manager

        self.tooltip = None
        self._after_id = None
        self._fade_id = None
        self._alpha = 0.0

        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)

    def _get_font(self, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font("font_size_tooltip", weight)
        return ctk.CTkFont(size=13, weight=weight)

    def _on_enter(self, event):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        self._after_id = self.widget.after(self.delay_show, self._show)

    def _on_leave(self, event):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        self._after_id = self.widget.after(self.delay_hide, self._hide)

    def _show(self):
        if not self.text:
            return

        if self.tooltip:
            self._position_tooltip()
            return

        bg_color = self.theme.get("bg_panel", "#2c3e50")
        text_color = self.theme.get("text_primary", "#e0e0e0")
        border_color = self.theme.get("text_accent", "#d4a843")

        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.configure(fg_color=bg_color)

        try:
            self.tooltip.attributes("-alpha", 0.0)
            self.tooltip.attributes("-topmost", True)
        except Exception:
            pass

        border_frame = ctk.CTkFrame(self.tooltip, fg_color=border_color, corner_radius=8)
        border_frame.pack(padx=1, pady=1, fill="both", expand=True)

        inner_frame = ctk.CTkFrame(border_frame, fg_color=bg_color, corner_radius=6)
        inner_frame.pack(padx=2, pady=2, fill="both", expand=True)

        label = ctk.CTkLabel(
            inner_frame,
            text=self.text,
            font=self._get_font(),
            text_color=text_color,
            justify="left"
        )
        label.pack(padx=12, pady=10)

        self._position_tooltip()

        self._alpha = 0.0
        self._fade_in()

    def _fade_in(self):
        if not self.tooltip:
            return
        self._alpha += 0.15
        if self._alpha >= 1.0:
            self._alpha = 1.0
            try:
                self.tooltip.attributes("-alpha", 1.0)
            except Exception:
                pass
            return
        try:
            self.tooltip.attributes("-alpha", self._alpha)
        except Exception:
            pass
        self._fade_id = self.tooltip.after(30, self._fade_in)

    def _fade_out(self):
        if not self.tooltip:
            return
        self._alpha -= 0.15
        if self._alpha <= 0.0:
            self._alpha = 0.0
            self._destroy_tooltip()
            return
        try:
            self.tooltip.attributes("-alpha", self._alpha)
        except Exception:
            pass
        self._fade_id = self.tooltip.after(30, self._fade_out)

    def _position_tooltip(self):
        if not self.tooltip:
            return
        try:
            x = self.widget.winfo_rootx() + 15
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8

            screen_w = self.widget.winfo_screenwidth()
            screen_h = self.widget.winfo_screenheight()
            self.tooltip.update_idletasks()
            tw = self.tooltip.winfo_width()
            th = self.tooltip.winfo_height()

            if x + tw > screen_w - 10:
                x = screen_w - tw - 10
            if y + th > screen_h - 10:
                y = self.widget.winfo_rooty() - th - 8

            self.tooltip.wm_geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _hide(self):
        if self.tooltip:
            self._fade_out()

    def _destroy_tooltip(self):
        if self._fade_id:
            try:
                self.tooltip.after_cancel(self._fade_id)
            except Exception:
                pass
            self._fade_id = None
        if self.tooltip:
            try:
                self.tooltip.destroy()
            except Exception:
                pass
            self.tooltip = None
        self._alpha = 0.0
