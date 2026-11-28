"""
Вкладка "Приложение" — контейнер с группированными подвкладками.
Уровень 2: группы (Внешний вид | Интерфейс)
Уровень 3: вкладки внутри группы.
"""
import customtkinter as ctk
from .base_panel import BaseTab
from .themes_panel import ThemeTab
from .fonts_panel import FontTab
from .tips_panel import TipsTab


GROUPS = {
    "🎨 Внешний вид": ["Темы"],
    "⚙ Интерфейс": ["Шрифты", "Подсказки"],
}

TAB_CLASSES = {
    "Темы": ThemeTab,
    "Шрифты": FontTab,
    "Подсказки": TipsTab,
}


class AppTab(BaseTab):
    def __init__(self, parent, config, font_size=13, theme=None,
                 font_manager=None, on_theme_editor=None):
        super().__init__(parent, config, None,
                         font_size=font_size, theme=theme,
                         font_manager=font_manager)
        self.on_theme_editor = on_theme_editor
        self._tab_frames = {}
        self._build()

    def _build(self):
        # Уровень 2: группы
        groups_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        groups_frame.pack(fill="x", padx=0, pady=0)
        self._group_switcher = ctk.CTkSegmentedButton(
            groups_frame,
            values=list(GROUPS.keys()),
            command=self._switch_group,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            selected_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            selected_hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            unselected_color=self.theme.get("bg_slider", "#3a4152"),
            unselected_hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            corner_radius=8, border_width=0,
            font=self._get_font("font_size_button_secondary", "bold"),
        )
        self._group_switcher.pack(side="left", padx=10, pady=5)

        # Уровень 3: вкладки
        tabs_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        tabs_frame.pack(fill="x", padx=0, pady=0)
        self._tab_switcher = ctk.CTkSegmentedButton(
            tabs_frame,
            values=GROUPS[list(GROUPS.keys())[0]],
            command=self._switch_tab,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            selected_color=self.theme.get("bg_button_secondary", "#2c3e50"),
            selected_hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            unselected_color=self.theme.get("bg_slider", "#3a4152"),
            unselected_hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            corner_radius=8, border_width=0,
            font=self._get_font("font_size_button_secondary", "normal"),
        )
        self._tab_switcher.pack(side="left", padx=14, pady=(0, 5))

        # Контент
        self._content_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self._content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self._create_tabs()
        self._group_switcher.set(list(GROUPS.keys())[0])
        self._switch_group(list(GROUPS.keys())[0])

    def _create_tabs(self):
        for name, cls in TAB_CLASSES.items():
            frame = ctk.CTkFrame(self._content_frame, fg_color="transparent")
            if name == "Темы":
                cls(frame, self.config, font_size=self.font_size, theme=self.theme,
                    font_manager=self.font_manager, on_theme_editor=self.on_theme_editor)
            else:
                cls(frame, self.config, font_size=self.font_size, theme=self.theme,
                    font_manager=self.font_manager)
            self._tab_frames[name] = frame

    def _switch_group(self, group_name):
        tabs = GROUPS.get(group_name, [])
        self._tab_switcher.configure(values=tabs)
        if tabs:
            self._tab_switcher.set(tabs[0])
            self._switch_tab(tabs[0])

    def _switch_tab(self, tab_name):
        for frame in self._tab_frames.values():
            frame.pack_forget()
        frame = self._tab_frames.get(tab_name)
        if frame:
            frame.pack(fill="both", expand=True, padx=0, pady=0)

    def get_pending_theme(self):
        return self._tab_frames.get("Темы").get_pending_theme() if "Темы" in self._tab_frames else None

    def get_pending_font_family(self):
        return self._tab_frames.get("Шрифты").get_pending_font_family() if "Шрифты" in self._tab_frames else None

    def navigate_to(self, group_name, tab_name):
        """Переход к конкретной группе и вкладке."""
        if group_name in GROUPS:
            self._group_switcher.set(group_name)
            self._switch_group(group_name)
            if tab_name in GROUPS.get(group_name, []):
                self._tab_switcher.set(tab_name)
                self._switch_tab(tab_name)
