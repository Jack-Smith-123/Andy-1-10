"""
Пакет core — логика рыбалки Andy-1-3.
"""
from .fishing_service import FishingService
from .water_detector import WaterDetector
from .cursor_tracker import CursorTracker

__all__ = ["FishingService", "WaterDetector", "CursorTracker"]

