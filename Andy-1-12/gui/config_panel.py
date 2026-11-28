"""
Окно Options — настройки с трёхуровневой навигацией и поиском.
С мгновенным индикатором загрузки.
"""
import customtkinter as ctk
from .panels import BotTab, AppTab
from .search_index import SEARCH_INDEX


SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class OptionsView(ctk.CTkToplevel):
    def __init__(self, parent, config, on_apply_callback, on_water_change_callback,
                 font_size=13, theme=None, font_manager=None):
        super().__init__(parent)
        self.title("Options")
        win_width = 560
        win_height = 750
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
        self.configure(fg_color=self.theme.get("bg_main", "#1a1f2e"))

        # === 1. ВЕРХНЯЯ ПАНЕЛЬ (рисуется мгновенно) ===
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            self.top_frame, text="⚙ Options",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_primary", "#e0e0e0")
        ).pack(side="left", padx=10)

        # Спиннер СПРАВА от заголовка
        self.spinner_label = ctk.CTkLabel(
            self.top_frame,
            text="⠋",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("bg_button_primary", "#1f6aa5")
        )
        self.spinner_label.pack(side="left", padx=(5, 10))
        self._spinner_index = 0
        self._spinner_stopped = False
        self._animate_spinner()

        # Поле поиска
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.top_frame,
            textvariable=self.search_var,
            placeholder_text="🔍 Поиск...",
            width=220, height=32,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            placeholder_text_color=self.theme.get("text_secondary", "#666666"),
            border_color=self.theme.get("bg_slider", "#3a4152"),
            corner_radius=8,
        )
        self.search_entry.pack(side="right", padx=10)
        self.search_entry.bind("<KeyRelease>", self._on_search_change)

        # Popup поиска
        self.search_popup = ctk.CTkToplevel(self)
        self.search_popup.title("")
        self.search_popup.overrideredirect(True)
        self.search_popup.attributes("-topmost", True)
        self.search_popup.withdraw()
        self.search_popup.configure(fg_color=self.theme.get("bg_panel", "#2a3142"))

        # === 2. КНОПКИ ВНИЗУ ===
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(pady=10, padx=10, fill="x", side="bottom")
        btn_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        ctk.CTkButton(
            btn_frame, text="✅ Применить",
            font=self._get_font("font_size_button_primary", "bold"),
            height=40,
            fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._apply
        ).pack(side="left", padx=4, expand=True, fill="x")
        ctk.CTkButton(
            btn_frame, text="✕ Закрыть",
            font=self._get_font("font_size_button_secondary"),
            height=40,
            fg_color=self.theme.get("bg_button_close", "#6c757d"),
            hover_color=self.theme.get("bg_button_close_hover", "#5a6268"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._on_close
        ).pack(side="right", padx=4, expand=True, fill="x")

        # === 3. ОБЛАСТЬ КОНТЕНТА ===
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Спиннер по центру контента
        self.loading_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.loading_text = ctk.CTkLabel(
            self.loading_frame,
            text="Загрузка настроек...",
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_secondary", "#a0a8b8")
        )
        self.loading_text.pack(pady=10)

        self.loading_bar = ctk.CTkProgressBar(
            self.loading_frame,
            width=250,
            mode="indeterminate",
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            progress_color=self.theme.get("bg_button_primary", "#1f6aa5")
        )
        self.loading_bar.pack(pady=5)
        self.loading_bar.start()

        # === 4. Отложенная инициализация вкладок ===
        self.after(50, self._load_tabs)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _animate_spinner(self):
        """Крутит спиннер в заголовке."""
        if self._spinner_stopped:
            return
        if hasattr(self, 'spinner_label') and self.spinner_label.winfo_exists():
            spinner = SPINNER_FRAMES[self._spinner_index % len(SPINNER_FRAMES)]
            self.spinner_label.configure(text=spinner)
            self._spinner_index += 1
            self.after(120, self._animate_spinner)

    def _load_tabs(self):
        """Загружает тяжёлые вкладки."""
        self.app_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.bot_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        tabs_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
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
            corner_radius=8, border_width=0,
            font=self._get_font("font_size_button_secondary", "bold")
        )
        self.tab_switcher.pack(side="left", padx=10, pady=5)

        self.app_tab = AppTab(
            self.app_frame, self.config, self.font_size, self.theme,
            font_manager=self.font_manager
        )
        self.bot_tab = BotTab(
            self.bot_frame, self.config,
            callbacks={
                "general": lambda *a, **kw: None,
                "cast": lambda *a, **kw: None,
                "bite": lambda *a, **kw: None,
                "minigame": lambda *a, **kw: None,
                "anticheat": lambda *a, **kw: None,
                "water": self._on_water_changed,
                "bobber": lambda *a, **kw: None,
                "zones": lambda *a, **kw: None,
                "visual": lambda *a, **kw: None,
            },
            font_size=self.font_size, theme=self.theme, font_manager=self.font_manager
        )

        self._switch_tab("Бот")
        self._hide_loading()

    def _hide_loading(self):
        """Убирает индикатор загрузки."""
        self._spinner_stopped = True
        if hasattr(self, 'loading_frame') and self.loading_frame.winfo_exists():
            self.loading_frame.place_forget()
            self.loading_frame.destroy()
        if hasattr(self, 'loading_bar'):
            try:
                self.loading_bar.stop()
            except:
                pass

    def _on_search_change(self, event=None):
        query = self.search_var.get().strip().lower()
        if not query:
            self.search_popup.withdraw()
            return

        results = [
            item for item in SEARCH_INDEX
            if query in item["label"].lower() or query in item["key"].lower()
        ][:10]

        if not results:
            self.search_popup.withdraw()
            return

        self._show_search_popup(results)
        self.after(10, self.search_entry.focus_set)

    def _show_search_popup(self, results):
        for widget in self.search_popup.winfo_children():
            widget.destroy()

        entry_x = self.search_entry.winfo_rootx()
        entry_y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height() + 4
        self.search_popup.geometry(f"280x{36 * len(results) + 10}+{entry_x}+{entry_y}")

        for item in results:
            btn = ctk.CTkButton(
                self.search_popup,
                text=f"{item['label']}  →  {item['group']} / {item['tab']}",
                font=self._get_font("font_size_label"),
                height=36,
                fg_color="transparent",
                hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
                text_color=self.theme.get("text_primary", "#e0e0e0"),
                anchor="w",
                command=lambda it=item: self._on_search_select(it),
            )
            btn.pack(fill="x", padx=4, pady=2)

        self.search_popup.deiconify()
        self.search_popup.lift()

    def _on_search_select(self, item):
        self.search_var.set("")
        self.search_popup.withdraw()

        group = item["group"]
        tab = item["tab"]

        bot_groups = ["🎮 Поведение", "👁 Детекция", "🎨 Визуал"]
        app_groups = ["🎨 Внешний вид", "⚙ Интерфейс"]

        if group in bot_groups:
            self.tab_switcher.set("Бот")
            self._switch_tab("Бот")
            if hasattr(self.bot_tab, "navigate_to"):
                self.bot_tab.navigate_to(group, tab)
        elif group in app_groups:
            self.tab_switcher.set("Приложение")
            self._switch_tab("Приложение")
            if hasattr(self.app_tab, "navigate_to"):
                self.app_tab.navigate_to(group, tab)

    def _switch_tab(self, name):
        self.bot_frame.pack_forget()
        self.app_frame.pack_forget()
        if name == "Бот":
            self.bot_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "Приложение":
            self.app_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def _on_water_changed(self, key=None, value=None):
        if self.on_water_change and key:
            self.on_water_change(key, value)

    def _apply(self):
        self.config["theme"] = self.app_tab.get_pending_theme()
        self.config["font_family"] = self.app_tab.get_pending_font_family()
        if self.font_manager:
            self.font_manager.clear_cache()
        self._save_config()
        self.on_apply(self.config)
        print(f"[SETTINGS] ✓ Применено и сохранено: тема={self.config.get('theme')}")

    def _save_config(self):
        import json
        import os
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.dat")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"[CONFIG] ✓ Сохранено: {config_path}")
        except Exception as e:
            print(f"[CONFIG] ✗ Ошибка сохранения: {e}")

    def set_save_callback(self, cb):
        self._save_config_cb = cb

    def _on_close(self):
        self.is_open = False
        try:
            self.search_popup.destroy()
        except:
            pass
        try:
            self.destroy()
        except:
            pass
