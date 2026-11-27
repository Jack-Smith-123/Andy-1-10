"""
Пакет вкладок настроек.
"""
from .general_tab import GeneralTab
from .water_tab import WaterTab
from .bobber_tab import BobberTab
from .visualizer_tab import VisualizerTab
from .font_tab import FontTab
from .theme_tab import ThemeTab
from .tips_tab import TipsTab
from .app_tab import AppTab

__all__ = [
    "GeneralTab", "WaterTab", "BobberTab", "VisualizerTab",
    "FontTab", "ThemeTab", "TipsTab", "AppTab"
]