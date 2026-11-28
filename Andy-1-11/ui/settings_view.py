"""
Окно Options — настройки с вкладками.
"""
import customtkinter as ctk
from .tabs import GeneralTab, WaterTab, BobberTab, VisualizerTab, AppTab, BiteTab
from .themes import THEMES
from .tabs import GeneralTab, WaterTab, BobberTab, VisualizerTab, AppTab


class OptionsView(ctk.CTkToplevel):
    def __init__(self, parent, config, on_apply_callback, on_water_change_callback,
                 font_size=13, theme=None, font_manager=None):
        super().__init__(parent)
        self.title("Options")
        
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

        self.configure(fg_color=self.theme.get("bg_main", "#1a1f2e"))

        # Заголовок
        ctk.CTkLabel(
            self, text="⚙ Options",
            font=self._get_font("font_size_header", "bold"),
            text_color=self.theme.get("text_primary", "#e0e0e0")
        ).pack(pady=10)

        # Кнопки внизу
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(pady=10, padx=10, fill="x", side="bottom")

        btn_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        apply_btn = ctk.CTkButton(
            btn_frame, text="✅ Применить",
            font=self._get_font("font_size_button_primary", "bold"),
            height=40,
            fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._apply
        )
        apply_btn.pack(side="left", padx=4, expand=True, fill="x")

        close_btn = ctk.CTkButton(
            btn_frame, text="✕ Закрыть",
            font=self._get_font("font_size_button_secondary"),
            height=40,
            fg_color=self.theme.get("bg_button_close", "#6c757d"),
            hover_color=self.theme.get("bg_button_close_hover", "#5a6268"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._on_close
        )
        close_btn.pack(side="right", padx=4, expand=True, fill="x")

        # Внешние вкладки: Бот | Приложение
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

        # Контент внешних вкладок
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=0, pady=0)

                # === Сначала "Приложение" (чтобы app_frame существовал до вызова _switch_tab) ===
        self.app_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.app_tab = AppTab(
            self.app_frame, self.config, self.font_size, self.theme,
            font_manager=self.font_manager
        )

        # === Потом "Бот" с подвкладками ===
        self.bot_frame = ctk.CTkFrame(content_frame, fg_color="transparent")

        bot_tabs_frame = ctk.CTkFrame(self.bot_frame, fg_color="transparent")
        bot_tabs_frame.pack(fill="x", padx=0, pady=0)

        self.bot_tab_switcher = ctk.CTkSegmentedButton(
            bot_tabs_frame,
            values=["Общее", "Вода", "Поплавок", "RGB"],
            command=self._switch_bot_tab,
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

        self.general_frame = ctk.CTkFrame(bot_content_frame, fg_color="transparent")
        self.water_frame = ctk.CTkFrame(bot_content_frame, fg_color="transparent")
        self.bobber_frame = ctk.CTkFrame(bot_content_frame, fg_color="transparent")
        self.visualizer_frame = ctk.CTkFrame(bot_content_frame, fg_color="transparent")

        self.general_tab = GeneralTab(
            self.general_frame, self.config, self._on_general_changed,
            self.font_size, self.theme, self.font_manager
        )
        self.water_tab = WaterTab(
            self.water_frame, self.config, self._on_water_changed,
            self.font_size, self.theme, self.font_manager
        )
        self.bobber_tab = BobberTab(
            self.bobber_frame, self.config, self._on_bobber_changed,
            self.font_size, self.theme, self.font_manager
        )
        self.visualizer_tab = VisualizerTab(
            self.visualizer_frame, self.config, self._on_visualizer_changed,
            self.font_size, self.theme, self.font_manager
        )

        self._switch_bot_tab("Общее")
        self._switch_tab("Бот")

        # === Фрейм "Приложение" ===
        self.app_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.app_tab = AppTab(
            self.app_frame, self.config, self.font_size, self.theme,
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

    def _switch_bot_tab(self, name):
        self.general_frame.pack_forget()
        self.water_frame.pack_forget()
        self.bobber_frame.pack_forget()
        self.visualizer_frame.pack_forget()
        
        if name == "Общее":
            self.general_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "Вода":
            self.water_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "Поплавок":
            self.bobber_frame.pack(fill="both", expand=True, padx=0, pady=0)
        elif name == "RGB":
            self.visualizer_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _on_general_changed(self):
        if hasattr(self, '_save_config_cb') and self._save_config_cb:
            self._save_config_cb()

    def _on_water_changed(self, key=None, value=None):
        if hasattr(self, '_save_config_cb') and self._save_config_cb:
            self._save_config_cb()
        if self.on_water_change and key:
            self.on_water_change(key, value)

    def _on_bobber_changed(self):
        if hasattr(self, '_save_config_cb') and self._save_config_cb:
            self._save_config_cb()

    def _on_visualizer_changed(self):
        if hasattr(self, '_save_config_cb') and self._save_config_cb:
            self._save_config_cb()

    def _apply(self):
        self.config["theme"] = self.app_tab.get_pending_theme()
        self.config["font_family"] = self.app_tab.get_pending_font_family()
        if hasattr(self, '_save_config_cb') and self._save_config_cb:
            self._save_config_cb()
        if self.font_manager:
            self.font_manager.clear_cache()
        self.on_apply(self.config)
        print(f"[SETTINGS] ✓ Применено: тема={self.config['theme']}")

    def set_save_callback(self, cb):
        self._save_config_cb = cb

    def _on_close(self):
        self.is_open = False
        try:
            self.destroy()
        except Exception:
            pass