"""
Строка "Метка + Цветной квадратик + HEX + RGB ползунки" для редактора тем.
"""
import customtkinter as ctk
from tkinter import colorchooser
from .tooltip import Tooltip


class ColorRow:
    def __init__(self, parent, key, label, colors_dict, font_size=13, theme=None, tooltip_text=""):
        self.key = key
        self.colors = colors_dict
        self.font_size = font_size
        self.theme = theme or {}
        self.on_change_callback = None
        
        self.frame = ctk.CTkFrame(parent, fg_color=self.theme.get("bg_main", "#1a1f2e"), corner_radius=6)
        self.frame.pack(pady=3, padx=10, fill="x")
        
        self.label = ctk.CTkLabel(
            self.frame, text=label,
            font=ctk.CTkFont(size=font_size - 1),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            width=130, anchor="w"
        )
        self.label.pack(side="left", padx=5, pady=6)
        
        # 🆕 Tooltip с темой
        if tooltip_text:
            Tooltip(self.label, tooltip_text, theme=self.theme)
        
        self.color_box = ctk.CTkButton(
            self.frame, text="", width=28, height=28,
            fg_color=colors_dict[key], hover_color=colors_dict[key],
            corner_radius=4, command=self._open_color_picker
        )
        self.color_box.pack(side="left", padx=3)
        
        # 🆕 Tooltip с темой
        if tooltip_text:
            Tooltip(self.color_box, tooltip_text, theme=self.theme)
        
        self.hex_entry = ctk.CTkEntry(
            self.frame, width=75, height=28,
            font=ctk.CTkFont(size=font_size - 2, family="monospace")
        )
        self.hex_entry.insert(0, colors_dict[key])
        self.hex_entry.pack(side="left", padx=3)
        self.hex_entry.bind("<Return>", self._on_hex_changed)
        self.hex_entry.bind("<FocusOut>", self._on_hex_changed)
        
        self.rgb_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.rgb_frame.pack(side="right", padx=3, fill="x", expand=True)
        
        r, g, b = self._hex_to_rgb(colors_dict[key])
        
        for channel, value, color in [("R", r, "#ff4444"), ("G", g, "#44ff44"), ("B", b, "#4444ff")]:
            ch_frame = ctk.CTkFrame(self.rgb_frame, fg_color="transparent")
            ch_frame.pack(side="top", fill="x", pady=1)
            
            ctk.CTkLabel(
                ch_frame, text=channel, width=14,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=color
            ).pack(side="left")
            
            slider = ctk.CTkSlider(
                ch_frame, from_=0, to=255, number_of_steps=255, width=90,
                button_color="#888888", progress_color="#888888",
                fg_color=self.theme.get("bg_slider", "#3a4152")
            )
            slider.set(value)
            slider.pack(side="left", padx=2)
            slider.configure(command=lambda v, ch=channel: self._on_rgb_changed(ch, v))
    
    def _open_color_picker(self):
        color = colorchooser.askcolor(title=f"Цвет: {self.key}", initialcolor=self.colors[self.key])
        if color[1]:
            self._set_color(color[1])
    
    def _on_hex_changed(self, event=None):
        hex_val = self.hex_entry.get().strip()
        if hex_val.startswith("#") and len(hex_val) == 7:
            try:
                int(hex_val[1:], 16)
                self._set_color(hex_val)
            except ValueError:
                pass
    
    def _on_rgb_changed(self, channel, value):
        r, g, b = self._hex_to_rgb(self.colors[self.key])
        if channel == "R":
            r = int(value)
        elif channel == "G":
            g = int(value)
        elif channel == "B":
            b = int(value)
        new_hex = self._rgb_to_hex(r, g, b)
        self._set_color(new_hex)
    
    def _set_color(self, hex_val):
        self.colors[self.key] = hex_val
        self.color_box.configure(fg_color=hex_val, hover_color=hex_val)
        self.hex_entry.delete(0, "end")
        self.hex_entry.insert(0, hex_val)
        if self.on_change_callback:
            self.on_change_callback(self.key, hex_val)
    
    def _hex_to_rgb(self, hex_val):
        h = hex_val.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, r, g, b):
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
    
    def set_change_callback(self, callback):
        self.on_change_callback = callback
