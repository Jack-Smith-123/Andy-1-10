"""
Пакет конфигурации Andy-1-3.
Экспортирует ConfigMixin, DEFAULT_CONFIG и CONFIG_FILE,
чтобы импорты вида `from config import ConfigMixin` работали
как из корня, так и из подпапок.
"""
from .config import ConfigMixin, DEFAULT_CONFIG, CONFIG_FILE

__all__ = ["ConfigMixin", "DEFAULT_CONFIG", "CONFIG_FILE"]
