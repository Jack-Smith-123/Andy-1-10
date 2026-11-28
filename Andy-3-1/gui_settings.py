import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from config import load_config, save_config
from logger import log_manager
from utils import rgb_to_hex, hex_to_rgb
from tooltip import Tooltip

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Настройки")
        self.geometry("380x700")
        self.resizable(False, False)
        self.parent_ref = parent
        self.config = load_config()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.tooltips = []

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_app = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_app, text="  Приложение  ")
        self.setup_app_tab()

        self.tab_bot = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_bot, text="  Бот  ")
        self.setup_bot_tabs()

        log_manager.add_flag_listener(self._on_log_flag_change)

    def setup_app_tab(self):
        ctk.CTkLabel(self.tab_app, text="Настройки приложения", font=("Arial", 14, "bold")).pack(pady=20)

        # Галочка Лог
        self.var_log = tk.BooleanVar(value=log_manager.enabled)
        log_cb = ctk.CTkCheckBox(self.tab_app, text="Лог (поток информации)", variable=self.var_log,
                                 command=self._toggle_log)
        log_cb.pack(pady=5)
        Tooltip(log_cb, "Включить/выключить сбор логов", self.config.get("app", {}).get("tooltip_delay", 1000))

        # Размер шрифта
        font_size = self.config.get("app", {}).get("font_size", 12)
        self.var_font_size = tk.IntVar(value=font_size)
        font_frame = ctk.CTkFrame(self.tab_app, fg_color="transparent")
        font_frame.pack(fill="x", padx=10, pady=10)
        
        font_label = ctk.CTkLabel(font_frame, text="Размер шрифта", width=110, anchor="w")
        font_label.pack(side="left", padx=2)
        Tooltip(font_label, "Размер текста в интерфейсе (8-24)", self.config.get("app", {}).get("tooltip_delay", 1000))
        
        slider = ctk.CTkSlider(font_frame, from_=8, to=24, variable=self.var_font_size,
                               command=lambda v: self.on_font_size_change(v))
        slider.pack(side="left", fill="x", expand=True, padx=2)
        Tooltip(slider, "Перетащите для изменения размера шрифта", self.config.get("app", {}).get("tooltip_delay", 1000))
        
        self.entry_font_size = ctk.CTkEntry(font_frame, width=55)
        self.entry_font_size.insert(0, str(font_size))
        self.entry_font_size.pack(side="right", padx=2)
        Tooltip(self.entry_font_size, "Введите размер шрифта (8-24)", self.config.get("app", {}).get("tooltip_delay", 1000))
        self.entry_font_size.bind("<Return>", lambda e: self.on_font_size_entry(e))

        # Задержка подсказок
        tooltip_delay = self.config.get("app", {}).get("tooltip_delay", 1000)
        self.var_tooltip_delay = tk.IntVar(value=tooltip_delay)
        tooltip_frame = ctk.CTkFrame(self.tab_app, fg_color="transparent")
        tooltip_frame.pack(fill="x", padx=10, pady=10)
        
        tooltip_label = ctk.CTkLabel(tooltip_frame, text="Задержка подсказок (мс)", width=110, anchor="w")
        tooltip_label.pack(side="left", padx=2)
        Tooltip(tooltip_label, "Время перед показом подсказки в миллисекундах", self.config.get("app", {}).get("tooltip_delay", 1000))
        
        tooltip_slider = ctk.CTkSlider(tooltip_frame, from_=100, to=3000, variable=self.var_tooltip_delay,
                                       command=lambda v: self.on_tooltip_delay_change(v))
        tooltip_slider.pack(side="left", fill="x", expand=True, padx=2)
        Tooltip(tooltip_slider, "Перетащите для изменения задержки (100-3000 мс)", self.config.get("app", {}).get("tooltip_delay", 1000))
        
        self.entry_tooltip_delay = ctk.CTkEntry(tooltip_frame, width=55)
        self.entry_tooltip_delay.insert(0, str(tooltip_delay))
        self.entry_tooltip_delay.pack(side="right", padx=2)
        Tooltip(self.entry_tooltip_delay, "Введите задержку в мс (100-3000)", self.config.get("app", {}).get("tooltip_delay", 1000))
        self.entry_tooltip_delay.bind("<Return>", lambda e: self.on_tooltip_delay_entry(e))

    def _toggle_log(self):
        log_manager.set_enabled(self.var_log.get())

    def _on_log_flag_change(self, value):
        self.var_log.set(value)

    def on_font_size_change(self, value):
        value = int(round(float(value)))
        self.config.setdefault("app", {})["font_size"] = value
        self.entry_font_size.delete(0, "end")
        self.entry_font_size.insert(0, str(value))
        save_config(self.config)
        self.parent_ref.apply_font_size(value)

    def on_font_size_entry(self, event):
        try:
            value = int(self.entry_font_size.get())
            value = max(8, min(24, value))
            self.config.setdefault("app", {})["font_size"] = value
            self.var_font_size.set(value)
            self.entry_font_size.delete(0, "end")
            self.entry_font_size.insert(0, str(value))
            save_config(self.config)
            self.parent_ref.apply_font_size(value)
        except ValueError:
            pass

    def on_tooltip_delay_change(self, value):
        value = int(round(float(value)))
        self.config.setdefault("app", {})["tooltip_delay"] = value
        self.entry_tooltip_delay.delete(0, "end")
        self.entry_tooltip_delay.insert(0, str(value))
        save_config(self.config)
        # Обновляем все tooltips
        for tooltip in self.tooltips:
            tooltip.update_delay(value)

    def on_tooltip_delay_entry(self, event):
        try:
            value = int(self.entry_tooltip_delay.get())
            value = max(100, min(3000, value))
            self.config.setdefault("app", {})["tooltip_delay"] = value
            self.var_tooltip_delay.set(value)
            self.entry_tooltip_delay.delete(0, "end")
            self.entry_tooltip_delay.insert(0, str(value))
            save_config(self.config)
            for tooltip in self.tooltips:
                tooltip.update_delay(value)
        except ValueError:
            pass

    def setup_bot_tabs(self):
        self.bot_notebook = ttk.Notebook(self.tab_bot)
        self.bot_notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_bot_general = ctk.CTkFrame(self.bot_notebook)
        self.bot_notebook.add(self.tab_bot_general, text="  Общая  ")
        self.setup_bot_general_tab()

        self.tab_bot_zone = ctk.CTkFrame(self.bot_notebook)
        self.bot_notebook.add(self.tab_bot_zone, text="  Зона  ")
        self.setup_bot_zone_tab()

    def setup_bot_general_tab(self):
        ctk.CTkLabel(self.tab_bot_general, text="Общие настройки", font=("Arial", 13, "bold")).pack(pady=(10, 5))
        
        window_label = ctk.CTkLabel(self.tab_bot_general, text="Окно: Albion Online Client")
        window_label.pack(pady=2)
        Tooltip(window_label, "Название окна игры для захвата", self.config.get("app", {}).get("tooltip_delay", 1000))

        fps = self.config.get("bot", {}).get("fps", 20)
        self.var_fps = tk.IntVar(value=fps)
        fps_frame = ctk.CTkFrame(self.tab_bot_general, fg_color="transparent")
        fps_frame.pack(fill="x", padx=10, pady=10)
        
        fps_label = ctk.CTkLabel(fps_frame, text="FPS захвата", width=110, anchor="w")
        fps_label.pack(side="left", padx=2)
        Tooltip(fps_label, "Частота захвата кадров (1-100)", self.config.get("app", {}).get("tooltip_delay", 1000))
        
        slider = ctk.CTkSlider(fps_frame, from_=1, to=100, variable=self.var_fps,
                               command=lambda v: self.on_fps_change(v))
        slider.pack(side="left", fill="x", expand=True, padx=2)
        Tooltip(slider, "Перетащите для изменения FPS", self.config.get("app", {}).get("tooltip_delay", 1000))
        
        self.entry_fps = ctk.CTkEntry(fps_frame, width=55)
        self.entry_fps.insert(0, str(fps))
        self.entry_fps.pack(side="right", padx=2)
        Tooltip(self.entry_fps, "Введите FPS (1-100)", self.config.get("app", {}).get("tooltip_delay", 1000))
        self.entry_fps.bind("<Return>", lambda e: self.on_fps_entry(e))

    def on_fps_change(self, value):
        value = int(round(float(value)))
        self.config.setdefault("bot", {})["fps"] = value
        self.entry_fps.delete(0, "end")
        self.entry_fps.insert(0, str(value))
        save_config(self.config)
        self.parent_ref.update_fps(value)

    def on_fps_entry(self, event):
        try:
            value = int(self.entry_fps.get())
            value = max(1, min(100, value))
            self.config.setdefault("bot", {})["fps"] = value
            self.var_fps.set(value)
            self.entry_fps.delete(0, "end")
            self.entry_fps.insert(0, str(value))
            save_config(self.config)
            self.parent_ref.update_fps(value)
        except ValueError:
            pass

    def setup_bot_zone_tab(self):
        zone = self.config["zone"]
        ctk.CTkLabel(self.tab_bot_zone, text="Зоны поиска", font=("Arial", 13, "bold")).pack(pady=(10, 5))

        self.var_enabled = tk.BooleanVar(value=zone["enabled"])
        self.var_show = tk.BooleanVar(value=zone["show"])
        cb_frame = ctk.CTkFrame(self.tab_bot_zone, fg_color="transparent")
        cb_frame.pack(fill="x", padx=10, pady=5)
        
        enabled_cb = ctk.CTkCheckBox(cb_frame, text="Вкл", variable=self.var_enabled,
                                     command=self.on_config_change)
        enabled_cb.pack(side="left", padx=5)
        Tooltip(enabled_cb, "Включить детекцию зон", self.config.get("app", {}).get("tooltip_delay", 1000))
        
        show_cb = ctk.CTkCheckBox(cb_frame, text="Показать", variable=self.var_show,
                                  command=self.on_config_change)
        show_cb.pack(side="left", padx=5)
        Tooltip(show_cb, "Показывать зоны на видео", self.config.get("app", {}).get("tooltip_delay", 1000))

        self.create_slider_row("Размер квадрата", "square_size", 10, 200, "Размер зоны поиска в пикселях")
        self.create_slider_row("Расстояние", "distance", 50, 300, "Расстояние между зонами")

        ctk.CTkLabel(self.tab_bot_zone, text="Цвет рамки", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        self.create_slider_row("Красный (R)", "color_r", 0, 255, "Красный компонент цвета (0-255)")
        self.create_slider_row("Зеленый (G)", "color_g", 0, 255, "Зеленый компонент цвета (0-255)")
        self.create_slider_row("Синий (B)", "color_b", 0, 255, "Синий компонент цвета (0-255)")

        hex_frame = ctk.CTkFrame(self.tab_bot_zone, fg_color="transparent")
        hex_frame.pack(fill="x", padx=10, pady=10)
        
        self.hex_entry = ctk.CTkEntry(hex_frame, width=100)
        self.hex_entry.insert(0, rgb_to_hex(zone["color_r"], zone["color_g"], zone["color_b"]))
        self.hex_entry.pack(side="left", padx=5)
        Tooltip(self.hex_entry, "HEX код цвета (например, #FF0000)", self.config.get("app", {}).get("tooltip_delay", 1000))
        self.hex_entry.bind("<Return>", self.on_hex_change)
        self.hex_entry.bind("<FocusOut>", self.on_hex_change)
        
        self.color_preview = ctk.CTkFrame(hex_frame, width=40, height=30,
                                          fg_color=rgb_to_hex(zone["color_r"], zone["color_g"], zone["color_b"]))
        self.color_preview.pack(side="right", padx=5)
        self.color_preview.pack_propagate(False)
        Tooltip(self.color_preview, "Предпросмотр выбранного цвета", self.config.get("app", {}).get("tooltip_delay", 1000))

    def create_slider_row(self, label, key, min_val, max_val, tooltip_text):
        frame = ctk.CTkFrame(self.tab_bot_zone, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=3)
        
        lbl = ctk.CTkLabel(frame, text=label, width=110, anchor="w")
        lbl.pack(side="left", padx=2)
        Tooltip(lbl, tooltip_text, self.config.get("app", {}).get("tooltip_delay", 1000))
        
        var = tk.DoubleVar(value=self.config["zone"][key])
        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, variable=var,
                               command=lambda v: self.on_slider_change(key, v))
        slider.pack(side="left", fill="x", expand=True, padx=2)
        Tooltip(slider, tooltip_text, self.config.get("app", {}).get("tooltip_delay", 1000))
        
        entry = ctk.CTkEntry(frame, width=55)
        entry.insert(0, str(int(self.config["zone"][key])))
        entry.pack(side="right", padx=2)
        Tooltip(entry, f"Введите значение ({min_val}-{max_val})", self.config.get("app", {}).get("tooltip_delay", 1000))
        entry.bind("<Return>", lambda e: self.on_entry_change(key, entry))
        
        setattr(self, f"var_{key}", var)
        setattr(self, f"entry_{key}", entry)

    def on_slider_change(self, key, value):
        value = int(round(float(value)))
        self.config["zone"][key] = value
        entry = getattr(self, f"entry_{key}")
        entry.delete(0, "end")
        entry.insert(0, str(value))
        if key in ("color_r", "color_g", "color_b"):
            self.update_color_preview()
        self.on_config_change()

    def on_entry_change(self, key, entry):
        try:
            value = int(entry.get())
            value = max(-999, min(999, value))
            self.config["zone"][key] = value
            var = getattr(self, f"var_{key}")
            var.set(value)
            entry.delete(0, "end")
            entry.insert(0, str(value))
            if key in ("color_r", "color_g", "color_b"):
                self.update_color_preview()
            self.on_config_change()
        except ValueError:
            pass

    def on_hex_change(self, event=None):
        rgb = hex_to_rgb(self.hex_entry.get())
        if rgb:
            r, g, b = rgb
            self.config["zone"]["color_r"] = r
            self.config["zone"]["color_g"] = g
            self.config["zone"]["color_b"] = b
            self.var_color_r.set(r)
            self.var_color_g.set(g)
            self.var_color_b.set(b)
            self.entry_color_r.delete(0, "end"); self.entry_color_r.insert(0, str(r))
            self.entry_color_g.delete(0, "end"); self.entry_color_g.insert(0, str(g))
            self.entry_color_b.delete(0, "end"); self.entry_color_b.insert(0, str(b))
            self.update_color_preview()
            self.on_config_change()

    def update_color_preview(self):
        r = int(self.var_color_r.get())
        g = int(self.var_color_g.get())
        b = int(self.var_color_b.get())
        hex_color = rgb_to_hex(r, g, b)
        self.color_preview.configure(fg_color=hex_color)
        self.hex_entry.delete(0, "end")
        self.hex_entry.insert(0, hex_color)

    def on_config_change(self):
        self.config["zone"]["enabled"] = self.var_enabled.get()
        self.config["zone"]["show"] = self.var_show.get()
        save_config(self.config)

    def on_close(self):
        log_manager.remove_flag_listener(self._on_log_flag_change)
        self.parent_ref.settings_window = None
        self.destroy()
