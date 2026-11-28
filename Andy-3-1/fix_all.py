import os

files = {
    'config.py': """# config.py - настройки
WINDOW_TITLE = "Albion Online Client"
TARGET_FPS = 30
MATCH_THRESHOLD = 0.70

ASSET_DIR = "assets"
IDLE_PREFIX = "obj_a_"
DIVE_PREFIX = "obj_b_"
TEMPLATE_COUNT = 10

ROI_WIDTH = 400
ROI_HEIGHT = 400
""",

    'detector.py': """# detector.py - поиск поплавка с несколькими вариантами шаблонов
import os
import cv2
from config import MATCH_THRESHOLD, ROI_WIDTH, ROI_HEIGHT, ASSET_DIR, IDLE_PREFIX, DIVE_PREFIX, TEMPLATE_COUNT

class BobberDetector:
    def __init__(self):
        self.idle_templates = []
        self.dive_templates = []
        
        for i in range(1, TEMPLATE_COUNT + 1):
            idle_path = os.path.join(ASSET_DIR, f"{IDLE_PREFIX}{i}.png")
            dive_path = os.path.join(ASSET_DIR, f"{DIVE_PREFIX}{i}.png")
            
            idle_tpl = cv2.imread(idle_path, cv2.IMREAD_GRAYSCALE)
            dive_tpl = cv2.imread(dive_path, cv2.IMREAD_GRAYSCALE)
            
            if idle_tpl is not None:
                self.idle_templates.append(idle_tpl)
            if dive_tpl is not None:
                self.dive_templates.append(dive_tpl)
        
        print(f"✅ Загружено {len(self.idle_templates)} шаблонов покоя, {len(self.dive_templates)} шаблонов нырка")

    def _match_all(self, roi_gray, templates):
        best_loc = None
        best_val = 0.0
        for tpl in templates:
            res = cv2.matchTemplate(roi_gray, tpl, cv2.TM_CCOEFF_NORMED)
            _, mv, _, ml = cv2.minMaxLoc(res)
            if mv > best_val:
                best_val = mv
                best_loc = ml
        return best_loc, best_val

    def find_state(self, frame, mouse_pos):
        if mouse_pos is None or frame is None:
            return None, None, 0.0
        
        mx, my = mouse_pos
        fh, fw = frame.shape[:2]
        
        tpl = self.idle_templates[0] if self.idle_templates else (self.dive_templates[0] if self.dive_templates else None)
        if tpl is None:
            return None, None, 0.0
        
        h, w = tpl.shape[:2]
        x1 = max(0, mx - ROI_WIDTH // 2); y1 = max(0, my - ROI_HEIGHT // 2)
        x2 = min(fw, mx + ROI_WIDTH // 2); y2 = min(fh, my + ROI_HEIGHT // 2)
        roi_gray = cv2.cvtColor(frame[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
        
        loc_idle, val_idle = self._match_all(roi_gray, self.idle_templates)
        loc_dive, val_dive = self._match_all(roi_gray, self.dive_templates)
        
        if val_idle >= MATCH_THRESHOLD and val_idle >= val_dive:
            x = x1 + loc_idle[0] + w // 2
            y = y1 + loc_idle[1] + h // 2
            return 'idle', (x, y), val_idle
        elif val_dive >= MATCH_THRESHOLD:
            x = x1 + loc_dive[0] + w // 2
            y = y1 + loc_dive[1] + h // 2
            return 'dive', (x, y), val_dive
        
        return None, None, max(val_idle, val_dive)
""",

    'capture.py': """# capture.py - Быстрый захват экрана и мыши
import mss
import cv2
import numpy as np
import pyautogui

class ScreenCapture:
    def __init__(self, window_manager):
        self.wm = window_manager

    def get_frame(self):
        if not self.wm.is_found:
            return None
        with mss.mss() as sct:
            screenshot = sct.grab(self.wm.rect)
            frame = np.array(screenshot)
            return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def get_mouse_rel(self):
        if not self.wm.is_found:
            return None
        try:
            mx, my = pyautogui.position()
            rel_x = mx - self.wm.rect["left"]
            rel_y = my - self.wm.rect["top"]
            if 0 <= rel_x < self.wm.rect["width"] and 0 <= rel_y < self.wm.rect["height"]:
                return (rel_x, rel_y)
            return None
        except Exception:
            return None
"""
}

for name, content in files.items():
    with open(name, 'w') as f:
        f.write(content)
    print(f"✅ {name} создан/обновлён")
