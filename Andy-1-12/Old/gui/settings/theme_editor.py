"""
Редактор пользовательских тем.
Двухколоночный layout: слева настройки, справа фиксированное превью.
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser
import json
import os
from ..widgets.color_row import ColorRow


class ThemeEditorWindow(ctk.CTkToplevel):
    def __init__(self, parent, config, on_save_callback, font_size=13, theme=None):
        super().__init__(parent)
        self.title("🎨 Создать свою тему")
        self.geometry("820x700")
        self.resizable(False, False)
        self.is_open = True
        self.config = config
        self.on_save = on_save_callback
        self.font_size = font_size
        self.theme = theme or {}
        
        # Загружаем текущую тему
        current_theme_key = config.get("theme", "albion_dark")
        from ..themes import THEMES
        current_theme = THEMES.get(current_theme_key, {})
        
        self._colors = {
            "bg_main": current_theme.get("bg_main", "#1a1f2e"),
            "bg_panel": current_theme.get("bg_panel", "#2a3142"),
            "bg_button_primary": current_theme.get("bg_button_primary", "#1f6aa5"),
            "bg_button_primary_hover": current_theme.get("bg_button_primary_hover", "#1a5a8a"),
            "bg_button_secondary": current_theme.get("bg_button_secondary", "#2c3e50"),
            "bg_button_secondary_hover": current_theme.get("bg_button_secondary_hover", "#34495e"),
            "bg_button_close": current_theme.get("bg_button_close", "#6c757d"),
            "bg_button_close_hover": current_theme.get("bg_button_close_hover", "#5a6268"),
            "bg_slider": current_theme.get("bg_slider", "#3a4152"),
            "text_primary": current_theme.get("text_primary", "#e0e0e0"),
            "text_secondary": current_theme.get("text_secondary", "#a0a8b8"),
            "text_accent": current_theme.get("text_accent", "#d4a843"),
            "indicator_off": current_theme.get("indicator_off", "#5a6a5a"),
            "indicator_on": current_theme.get("indicator_on", "#4ade80"),
            "status_text": current_theme.get("status_text", "#a0a8b8"),
            "status_active": current_theme.get("status_active", "#4ade80"),
        }
        
        self._font_size = int(current_theme.get("font_size", config.get("font_size", 13)))
        
        self.configure(fg_color=self._colors["bg_main"])
        
        # Шапка с кнопками
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=10, padx=15, fill="x")
        ctk.CTkLabel(
            header, text="🎨 Создать свою тему",
            font=ctk.CTkFont(size=self._font_size + 4, weight="bold"),
            text_color=self._colors["text_primary"]
        ).pack(side="left")
        
        save_btn = ctk.CTkButton(
            header, text="💾 Сохранить",
            font=ctk.CTkFont(size=self._font_size - 1, weight="bold"),
            height=32, width=110,
            fg_color=self._colors["bg_button_primary"],
            hover_color=self._colors["bg_button_primary_hover"],
            text_color=self._colors["text_primary"],
            command=self._save_theme
        )
        save_btn.pack(side="right", padx=5)
        
        cancel_btn = ctk.CTkButton(
            header, text="✕ Отмена",
            font=ctk.CTkFont(size=self._font_size - 1),
            height=32, width=90,
            fg_color=self._colors["bg_button_close"],
            hover_color=self._colors["bg_button_close_hover"],
            text_color=self._colors["text_primary"],
            command=self._on_close
        )
        cancel_btn.pack(side="right", padx=5)
        
        # Основной layout
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(padx=15, pady=5, fill="both", expand=True)
        
        # Левая колонка: прокручиваемые настройки
        left_frame = ctk.CTkFrame(main_frame, fg_color=self._colors["bg_panel"], corner_radius=8)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        canvas = tk.Canvas(left_frame, bg=self._colors["bg_panel"], highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(left_frame, command=canvas.yview, width=14)
        self._scrollable_frame = ctk.CTkFrame(canvas, fg_color=self._colors["bg_panel"])
        
        self._scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self._scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Правая колонка: фиксированное превью
        right_frame = ctk.CTkFrame(main_frame, fg_color=self._colors["bg_panel"], corner_radius=8, width=320)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            right_frame, text="👁 Превью",
            font=ctk.CTkFont(size=self._font_size + 1, weight="bold"),
            text_color=self._colors["text_accent"]
        ).pack(anchor="w", padx=10, pady=(15, 5))
        
        self._build_preview(right_frame)
        
        # Заполняем левую колонку
        self._color_rows = []
        
        self._add_section_label(self._scrollable_frame, "🖼 Фоны")
        self._add_color_row("bg_main", "Фон окна", "Основной фон всего окна приложения")
        self._add_color_row("bg_panel", "Фон панели", "Фон панелей настроек и кнопок")
        self._add_color_row("bg_slider", "Фон ползунка", "Фон дорожки ползунков")
        
        self._add_section_label(self._scrollable_frame, "🔘 Кнопки")
        self._add_color_row("bg_button_primary", "Основная", "Цвет кнопок Старт/Стоп/Действует")
        self._add_color_row("bg_button_primary_hover", "Основная (hover)", "Цвет при наведении на основную кнопку")
        self._add_color_row("bg_button_secondary", "Вторичная", "Цвет кнопок Видео/Лог/Настройки")
        self._add_color_row("bg_button_secondary_hover", "Вторичная (hover)", "Цвет при наведении на вторичную кнопку")
        self._add_color_row("bg_button_close", "Закрытия", "Цвет кнопки X и Закрыть")
        self._add_color_row("bg_button_close_hover", "Закрытия (hover)", "Цвет при наведении на кнопку закрытия")
        
        self._add_section_label(self._scrollable_frame, "📝 Текст и шрифт")
        self._add_font_size_row()
        self._add_color_row("text_primary", "Основной", "Основной цвет текста")
        self._add_color_row("text_secondary", "Вторичный", "Цвет второстепенного текста")
        self._add_color_row("text_accent", "Акцент", "Цвет акцентного текста (заголовки секций)")
        
        self._add_section_label(self._scrollable_frame, "🟢 Индикаторы")
        self._add_color_row("indicator_off", "Выключен", "Цвет индикатора в неактивном состоянии")
        self._add_color_row("indicator_on", "Включен", "Цвет индикатора в активном состоянии")
        self._add_color_row("status_text", "Статус текст", "Цвет текста статуса")
        self._add_color_row("status_active", "Статус активен", "Цвет текста активного статуса")
        
        ctk.CTkFrame(self._scrollable_frame, fg_color="transparent", height=20).pack(fill="x")
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _add_section_label(self, parent, text):
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(size=self._font_size, weight="bold"),
            text_color=self._colors["text_accent"]
        ).pack(anchor="w", padx=12, pady=(15, 5))
    
    def _add_font_size_row(self, parent=None):
        if parent is None:
            parent = self._scrollable_frame
        row = ctk.CTkFrame(parent, fg_color=self._colors["bg_main"], corner_radius=6)
        row.pack(pady=3, padx=10, fill="x")
        
        ctk.CTkLabel(
            row, text="🔤 Размер шрифта:",
            font=ctk.CTkFont(size=self._font_size - 1),
            text_color=self._colors["text_primary"],
            width=130, anchor="w"
        ).pack(side="left", padx=5, pady=8)
        
        self._font_size_slider = ctk.CTkSlider(
            row, from_=10, to=24, number_of_steps=14, width=120,
            button_color=self._colors["bg_button_primary"],
            progress_color=self._colors["bg_button_primary"],
            fg_color=self._colors["bg_slider"]
        )
        self._font_size_slider.set(self._font_size)
        self._font_size_slider.pack(side="left", padx=5)
        
        self._font_size_label = ctk.CTkLabel(
            row, text=str(int(self._font_size)),
            font=ctk.CTkFont(size=self._font_size, weight="bold"),
            width=30, text_color=self._colors["text_primary"]
        )
        self._font_size_label.pack(side="left", padx=5)
        
        self._font_size_slider.configure(command=self._on_font_size_changed)
    
    def _add_color_row(self, key, label, tooltip=""):
        row = ColorRow(
            self._scrollable_frame, key, label, self._colors,
            self._font_size, self.theme, tooltip
        )
        row.set_change_callback(lambda k, v: self._update_preview())
        self._color_rows.append(row)
    
    def _build_preview(self, parent):
        """Фиксированное превью в правой колонке."""
        # Кнопки
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(pady=10, padx=10, fill="x")
        
        self._preview_primary = ctk.CTkButton(
            btn_frame, text="Основная", height=32,
            fg_color=self._colors["bg_button_primary"],
            hover_color=self._colors["bg_button_primary_hover"],
            text_color=self._colors["text_primary"],
            font=ctk.CTkFont(size=self._font_size)
        )
        self._preview_primary.pack(pady=3, fill="x")
        
        self._preview_secondary = ctk.CTkButton(
            btn_frame, text="Вторичная", height=32,
            fg_color=self._colors["bg_button_secondary"],
            hover_color=self._colors["bg_button_secondary_hover"],
            text_color=self._colors["text_primary"],
            font=ctk.CTkFont(size=self._font_size)
        )
        self._preview_secondary.pack(pady=3, fill="x")
        
        self._preview_close = ctk.CTkButton(
            btn_frame, text="Закрыть", height=32,
            fg_color=self._colors["bg_button_close"],
            hover_color=self._colors["bg_button_close_hover"],
            text_color=self._colors["text_primary"],
            font=ctk.CTkFont(size=self._font_size)
        )
        self._preview_close.pack(pady=3, fill="x")
        
        # Разделитель
        ctk.CTkFrame(parent, height=1, fg_color=self._colors["bg_slider"]).pack(fill="x", padx=10, pady=8)
        
        # Текст
        self._preview_text_large = ctk.CTkLabel(
            parent, text="Крупный текст",
            font=ctk.CTkFont(size=self._font_size + 4, weight="bold"),
            text_color=self._colors["text_primary"]
        )
        self._preview_text_large.pack(anchor="w", padx=10, pady=2)
        
        self._preview_text_normal = ctk.CTkLabel(
            parent, text="Обычный текст",
            font=ctk.CTkFont(size=self._font_size),
            text_color=self._colors["text_primary"]
        )
        self._preview_text_normal.pack(anchor="w", padx=10, pady=2)
        
        self._preview_text_small = ctk.CTkLabel(
            parent, text="Мелкий текст",
            font=ctk.CTkFont(size=self._font_size - 2),
            text_color=self._colors["text_secondary"]
        )
        self._preview_text_small.pack(anchor="w", padx=10, pady=2)
        
        self._preview_text_accent = ctk.CTkLabel(
            parent, text="Акцентный текст",
            font=ctk.CTkFont(size=self._font_size, weight="bold"),
            text_color=self._colors["text_accent"]
        )
        self._preview_text_accent.pack(anchor="w", padx=10, pady=2)
        
        # Разделитель
        ctk.CTkFrame(parent, height=1, fg_color=self._colors["bg_slider"]).pack(fill="x", padx=10, pady=8)
        
        # Индикаторы
        ind_row = ctk.CTkFrame(parent, fg_color="transparent")
        ind_row.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(
            ind_row, text="●", font=ctk.CTkFont(size=18),
            text_color=self._colors["indicator_on"]
        ).pack(side="left", padx=3)
        ctk.CTkLabel(
            ind_row, text="Активен", font=ctk.CTkFont(size=self._font_size),
            text_color=self._colors["status_active"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            ind_row, text="●", font=ctk.CTkFont(size=18),
            text_color=self._colors["indicator_off"]
        ).pack(side="left", padx=(10, 3))
        ctk.CTkLabel(
            ind_row, text="Выключен", font=ctk.CTkFont(size=self._font_size),
            text_color=self._colors["status_text"]
        ).pack(side="left")
    
    def _on_font_size_changed(self, value):
        self._font_size = int(value)
        self._font_size_label.configure(text=str(self._font_size),
                                        font=ctk.CTkFont(size=self._font_size, weight="bold"))
        self._update_preview()
    
    def _update_preview(self):
        if not hasattr(self, '_preview_primary'):
            return
        self._preview_primary.configure(
            fg_color=self._colors["bg_button_primary"],
            hover_color=self._colors["bg_button_primary_hover"],
            text_color=self._colors["text_primary"],
            font=ctk.CTkFont(size=self._font_size)
        )
        self._preview_secondary.configure(
            fg_color=self._colors["bg_button_secondary"],
            hover_color=self._colors["bg_button_secondary_hover"],
            text_color=self._colors["text_primary"],
            font=ctk.CTkFont(size=self._font_size)
        )
        self._preview_close.configure(
            fg_color=self._colors["bg_button_close"],
            hover_color=self._colors["bg_button_close_hover"],
            text_color=self._colors["text_primary"],
            font=ctk.CTkFont(size=self._font_size)
        )
        
        self._preview_text_large.configure(
            text_color=self._colors["text_primary"],
            font=ctk.CTkFont(size=self._font_size + 4, weight="bold")
        )
        self._preview_text_normal.configure(
            text_color=self._colors["text_primary"],
            font=ctk.CTkFont(size=self._font_size)
        )
        self._preview_text_small.configure(
            text_color=self._colors["text_secondary"],
            font=ctk.CTkFont(size=self._font_size - 2)
        )
        self._preview_text_accent.configure(
            text_color=self._colors["text_accent"],
            font=ctk.CTkFont(size=self._font_size, weight="bold")
        )
    
    def _save_theme(self):
        theme_name = f"custom_{len(self.config.get('custom_themes', [])) + 1}"
        if "custom_themes" not in self.config:
            self.config["custom_themes"] = {}
        
        theme_data = self._colors.copy()
        theme_data["font_size"] = self._font_size
        theme_data["name"] = theme_name
        theme_data["description"] = f"Пользовательская (шрифт: {self._font_size})"
        
        self.config["custom_themes"][theme_name] = theme_data
        
        custom_themes_file = "custom_themes.json"
        try:
            existing = {}
            if os.path.exists(custom_themes_file):
                with open(custom_themes_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            existing[theme_name] = theme_data
            with open(custom_themes_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            print(f"[THEME] ✓ Тема сохранена: {theme_name} (шрифт: {self._font_size})")
        except Exception as e:
            print(f"[THEME] ⚠ Ошибка сохранения: {e}")
        
        if self.on_save:
            self.on_save(theme_name, theme_data)
        self._on_close()
    
    def _on_close(self):
        try:
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")
        except Exception:
            pass
        self.is_open = False
        self.destroy()
