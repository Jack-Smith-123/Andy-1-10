"""
Пакет gui.panels — вкладки настроек Andy-1.
"""
from .base_panel import BaseTab
from .bot_panel import BotTab
from .app_panel import AppTab
from .general_panel import GeneralTab
from .event_panel import BiteTab
from .launch_panel import CastTab
from .zones_panel import ZonesTab
from .stealth_panel import AntiCheatTab
from .minigame_panel import MiniGameTab
from .environment_panel import WaterTab
from .target_panel import BobberTab
from .overlay_panel import VisualizerTab
from .fonts_panel import FontTab
from .themes_panel import ThemeTab
from .tips_panel import TipsTab

__all__ = [
    'BaseTab', 'BotTab', 'AppTab',
    'GeneralTab', 'BiteTab', 'CastTab', 'ZonesTab',
    'AntiCheatTab', 'MiniGameTab', 'WaterTab', 'BobberTab',
    'VisualizerTab', 'FontTab', 'ThemeTab', 'TipsTab',
]
