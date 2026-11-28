"""
Модульные вкладки настроек.
Все вкладки вынесены в отдельные файлы в папке ui/tabs/
"""
# Импортируем все вкладки из подпапки
from .panels import (
    GeneralTab,
    BiteTab,
    CastTab,
    ZonesTab,
    AntiCheatTab,
    MiniGameTab,
    WaterTab,
    BobberTab,
    VisualizerTab,
    AppTab,
    FontTab,
    ThemeTab,
    TipsTab,
)

__all__ = [
    'GeneralTab',
    'BiteTab',
    'CastTab',
    'ZonesTab',
    'AntiCheatTab',
    'MiniGameTab',
    'WaterTab',
    'BobberTab',
    'VisualizerTab',
    'AppTab',
    'FontTab',
    'ThemeTab',
    'TipsTab',
]