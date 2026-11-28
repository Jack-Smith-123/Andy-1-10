"""
Вкладка "Бот" — контейнер с группированными подвкладками.
Уровень 2: группы (Поведение | Детекция | Визуал)
Уровень 3: вкладки внутри группы.
"""
import customtkinter as ctk
from .base_panel import BaseTab
from .general_panel import GeneralTab
from .launch_panel import CastTab
from .event_panel import BiteTab
from .minigame_panel import MiniGameTab
from .stealth_panel import AntiCheatTab
from .environment_panel import WaterTab
from .target_panel import BobberTab
from .zones_panel import ZonesTab
from .overlay_panel import VisualizerTab


# Группы и вкладки внутри них
GROUPS = {
    "🎮 Поведение": ["Общее", "Заброс", "Поклёвка", "Мини-игра", "Анти-чит"],
    "👁 Детекция": ["Вода", "Поплавок", "Зоны"],
    "🎨 Визуал": ["Оверлеи"],
}

TAB_CLASSES = {
    "Общее": GeneralTab,
    "Заброс": CastTab,
    "Поклёвка": BiteTab,
    "Мини-игра": MiniGameTab,
    "Анти-чит": AntiCheatTab,
    "Вода": WaterTab,
    "Поплавок": BobberTab,
    "Зоны": ZonesTab,
    "Оверлеи": VisualizerTab,
}


class BotTab(BaseTab):
    def __init__(self, parent, config, callbacks=None, font_size=13,
                 theme=None, font_manager=None):
        super().__init__(parent, config, None,
                         font_size=font_size, theme=theme,
                         font_manager=font_manager)
        self.callbacks = callbacks or {}
        self._tab_frames = {}
        self._current_group = None
        self._build()

    def _build(self):
        # Уровень 2: переключатель групп
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

        # Уровень 3: переключатель вкладок
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
            key = {"Общее": "general", "Заброс": "cast", "Поклёвка": "bite",
                   "Мини-игра": "minigame", "Анти-чит": "anticheat",
                   "Вода": "water", "Поплавок": "bobber", "Зоны": "zones",
                   "Оверлеи": "visual"}.get(name, name)
            cb = lambda *a, _k=key, **kw: self.callbacks.get(_k, lambda *x, **y: None)(*a, **kw)
            self._tab_frames[name] = frame
            cls(frame, self.config, cb, self.font_size, self.theme, self.font_manager)

    def _switch_group(self, group_name):
        self._current_group = group_name
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

    def navigate_to(self, group_name, tab_name):
        """Переход к конкретной группе и вкладке."""
        if group_name in GROUPS:
            self._group_switcher.set(group_name)
            self._switch_group(group_name)
            if tab_name in GROUPS.get(group_name, []):
                self._tab_switcher.set(tab_name)
                self._switch_tab(tab_name)
