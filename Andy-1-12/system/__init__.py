"""
Пакет system — системные операции (экран, ввод, окна, сочетания клавиш).
"""
from .display import DisplayReader
from .interact import Interactor
from .app_find import AppLocator
from .shortcuts import ShortcutManager

__all__ = [
    "DisplayReader",
    "Interactor",
    "AppLocator",
    "ShortcutManager",
]