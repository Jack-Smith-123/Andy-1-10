"""
Пакет ui — интерфейс (окна, виджеты, темы).
"""
from .main_view import MainView
from .video_view import VideoView
from .log_view import OutputView
from .settings_view import OptionsView
from .themes import THEMES, get_theme

__all__ = [
    "MainView",
    "VideoView",
    "OutputView",
    "OptionsView",
    "THEMES",
    "get_theme",
]