"""
Окно настроек с вкладками: Бот и Приложение.
Внутри "Бот" — подвкладки "Вода", "Поплавок", "Визуал".
🆕 Исправлен вызов ThemeEditorWindow (убран лишний аргумент font_manager).
🆕 Переименовано в Andy-1.8.
"""
import customtkinter as ctk
import json
import os
from ..themes import THEMES
from .water_tab import WaterTab
from .bobber_tab import BobberTab
from .visualizer_tab import VisualizerTab
from .app_tab import AppTab


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, config, on_apply_callback, on_water_change_callback,
                 font_size=13, theme=None, font_manager=None):
        super().__init__(parent)
        self.title("⚙ Настройки — Andy-1.8")
        win_width = 480
        win_height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - win_width) // 2
        y = (screen_height - win_height) // 2
        self.geometry(f"{win_width}x{win_height}+{x}+{y}")
        self.resizable(False, False)
        self.is_open = True
        self.config = config
        self.on_apply = on_apply_callback
        self.on_water_change = on_water_change_callback
        self.font_size = int(font_size) if isinstance(font_size, (int, float)) else 13
        self.theme = theme or {}
        self.font_manager = font_manager
        self._load_custom_themes()
        self.configure(fg_color=self.theme.get("bg_main", "#1a1f2e"))

        # === Заголовок ===
        ctk.CTkLabel(
            self,
            text="⚙ Настройки",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_primary", "#e0e0e0")
        ).pack(pady=10)

        # === Фрейм для кнопок (внизу) ===
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(pady=10, padx=10, fill="x", side="bottom")
        btn_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        apply_btn = ctk.CTkButton(
            btn_frame,
            text="✅ Применить",
            font=self._get_font("font_size_button_primary", "bold"),
            height=40,
            fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._apply
        )
        apply_btn.pack(side="left", padx=4, expand=True, fill="x")
        close_btn = ctk.CTkButton(
            btn_frame,
            text="✕ Закрыть",
            font=self._get_font("font_size_button_secondary"),
            height=40,
            fg_color=self.theme.get("bg_button_close", "#6c757d"),
            hover_color=self.theme.get("bg_button_close_hover", "#5a6268"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._on_close
        )
        close_btn.pack(side="right", padx=4, expand=True, fill="x")

        # === Внешние вкладки: Бот | Приложение ===
        tabs_frame = ctk.CTkFrame(self, fg_color="transparent")
        tabs_frame.pack(fill="x", padx=0, pady=0)
        self.tab_switcher = ctk.CTkSegmentedButton(
            tabs_frame,
            values=["Бот", "Приложение"],
            command=self._switch_tab,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            selected_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            selected_hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            unselected_color=self.theme.get("bg_slider", "#3a4152"),
            unselected_hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            corner_radius=8,
            border_width=0,
            font=self._get_font("font_size_button_secondary", "bold")
        )
        self.tab_switcher.pack(side="left", padx=10, pady=5)

        # === Фрейм для контента внешних вкладок ===
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # --- Фрейм "Бот" ---
        self.bot_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        bot_tabs_frame = ctk.CTkFrame(self.bot_frame, fg_color="transparent")
        bot_tabs_frame.pack(fill="x", padx=0, pady=0)
        self.bot_tab_switcher = ctk.CTkSegmentedButton(
            bot_tabs_frame,
            values=["Вода", "Поплавок", "Визуал"],
            command=self._switch_bot_subtab,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            selected_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            selected_hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            unselected_color=self.theme.get("bg_slider", "#3a4152"),
            unselected_hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            corner_radius=8,
            border_width=0,
            font=self._get_font("font_size_button_secondary", "bold")
        )
        self.bot_tab_switcher.pack(side="left", padx=10, pady=5)

        bot_content_frame = ctk.CTkFrame(self.bot_frame, fg_color="transparent")
        bot_content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.water_frame = ctk.CTkFrame(bot_content_frame, fg_color="transparent")
        self.water_tab = WaterTab(
            self.water_frame, self.config, self._on_water_changed,
            self.font_size, self.theme, self.font_manager
        )

        self.bobber_frame = ctk.CTkFrame(bot_content_frame, fg_color="transparent")
        self.bobber_tab = BobberTab(
            self.bobber_frame, self.config, self._on_water_changed,
            self.font_size, self.theme, self.font_manager
        )

        self.vis_frame = ctk.CTkFrame(bot_content_frame, fg_color="transparent")
        self.vis_tab = VisualizerTab(
            self.vis_frame, self.config, self._on_water_changed,
            self.font_size, self.theme, self.font_manager
        )

        # --- Фрейм "Приложение" ---
        self.app_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.app_tab = AppTab(
            self.app_frame, self.config, self.font_size, self.theme,
            on_theme_editor=self._open_theme_editor,
            font_manager=self.font_manager
        )

        self._switch_tab("Бот")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _switch_tab(self, name):
        self.bot_frame.pack_forget()
        self.app_frame.pack_forget()
        if name == "Бот":
            self.bot_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "Приложение":
            self.app_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def _switch_bot_subtab(self, name):
        self.water_frame.pack_forget()
        self.bobber_frame.pack_forget()
        self.vis_frame.pack_forget()
        if name == "Вода":
            self.water_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "Поплавок":
            self.bobber_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "Визуал":
            self.vis_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _load_custom_themes(self):
        custom_file = "custom_themes.json"
        if os.path.exists(custom_file):
            try:
                with open(custom_file, "r", encoding="utf-8") as f:
                    custom_themes = json.load(f)
                for key, data in custom_themes.items():
                    if key not in THEMES:
                        THEMES[key] = {
                            "name": data.get("name", key),
                            "description": data.get("description", "Пользовательская тема"),
                            **data
                        }
            except Exception as e:
                print(f"[SETTINGS] ⚠ Ошибка загрузки пользовательских тем: {e}")

    def _on_water_changed(self, key, value):
        self.on_water_change(key, value)

    # 🆕 Исправлено: убран лишний аргумент self.font_manager
    def _open_theme_editor(self):
        from .theme_editor import ThemeEditorWindow
        editor = ThemeEditorWindow(
            self,
            self.config,
            self._on_custom_theme_saved,
            self.font_size,
            self.theme
        )
        editor.transient(self)

    def _on_custom_theme_saved(self, theme_name, theme_colors):
        THEMES[theme_name] = {
            "name": theme_colors.get("name", theme_name),
            "description": theme_colors.get("description", "Пользовательская тема"),
            **theme_colors
        }
        if self.app_tab:
            themes_frame = self.app_tab._theme_rows[0].frame.master if self.app_tab._theme_rows else None
            if themes_frame:
                self.app_tab._rebuild_theme_list(themes_frame)
        print(f"[SETTINGS] ✓ Пользовательская тема добавлена: {theme_name}")

    def _apply(self):
        self.config["theme"] = self.app_tab.get_pending_theme()
        self.config["font_family"] = self.app_tab.get_pending_font_family()
        if hasattr(self, '_save_config_cb') and self._save_config_cb:
            self._save_config_cb()
        if self.font_manager:
            self.font_manager.clear_cache()
        self.on_apply(self.config)
        print(f"[SETTINGS] ✓ Применено: тема={self.config['theme']}, семейство={self.config.get('font_family')}")

    def set_save_callback(self, cb):
        self._save_config_cb = cb

    def _on_close(self):
        self.is_open = False
        self.destroy()
