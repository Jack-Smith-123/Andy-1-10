"""
Загрузка и матчинг шаблонов поплавка.
Мульти-шаблонная система: до 10 шаблонов из папки.
"""
import cv2
import os
import glob

class TemplateMatcher:
    def __init__(self, config, log_callback=None):
        self.config = config
        self.log = log_callback or print
        
        self.water_templates = []
        self.minigame_templates = []
        self.h_water, self.w_water = 0, 0
        self.h_minigame, self.w_minigame = 0, 0
        
        self._load_all_templates()
    
    def _load_all_templates(self):
        """Загружает шаблоны из папок (до bobber_max_templates штук)."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        max_templates = self.config.get("bobber_max_templates", 10)
        
        # --- Шаблоны воды ---
        water_dir = self.config.get("bobber_water_dir", "templates/bobber_in_water")
        water_dir_full = os.path.join(base_dir, water_dir)
        
        if os.path.isdir(water_dir_full):
            files = sorted(glob.glob(os.path.join(water_dir_full, "*.png")))
            for f in files[:max_templates]:
                img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    self.water_templates.append(img)
                    if self.h_water == 0:
                        self.h_water, self.w_water = img.shape[:2]
            self.log(f"✓ Загружено {len(self.water_templates)} шаблонов воды из {water_dir}")
        
        # Fallback на одиночный файл
        if not self.water_templates:
            water_path = self.config.get("bobber_water_path", "templates/bobber_in_water.png")
            water_path_full = os.path.join(base_dir, water_path)
            if not os.path.exists(water_path_full):
                water_path_full = os.path.join(base_dir, "bobberExamples", "bobberExampleInWatter2.png")
            img = cv2.imread(water_path_full, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                self.water_templates.append(img)
                self.h_water, self.w_water = img.shape[:2]
                self.log("✓ Загружен одиночный шаблон воды (fallback)")
        
        # --- Шаблоны мини-игры ---
        minigame_dir = self.config.get("bobber_minigame_dir", "templates/bobber_minigame")
        minigame_dir_full = os.path.join(base_dir, minigame_dir)
        
        if os.path.isdir(minigame_dir_full):
            files = sorted(glob.glob(os.path.join(minigame_dir_full, "*.png")))
            for f in files[:max_templates]:
                img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    self.minigame_templates.append(img)
                    if self.h_minigame == 0:
                        self.h_minigame, self.w_minigame = img.shape[:2]
            self.log(f"✓ Загружено {len(self.minigame_templates)} шаблонов мини-игры")
        
        # Fallback на одиночный файл
        if not self.minigame_templates:
            minigame_path = self.config.get("bobber_minigame_path", "templates/bobber_minigame.png")
            minigame_path_full = os.path.join(base_dir, minigame_path)
            if not os.path.exists(minigame_path_full):
                minigame_path_full = os.path.join(base_dir, "bobberExamples", "bobberExample2.png")
            img = cv2.imread(minigame_path_full, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                self.minigame_templates.append(img)
                self.h_minigame, self.w_minigame = img.shape[:2]
                self.log("✓ Загружен одиночный шаблон мини-игры (fallback)")
        
        if not self.water_templates or not self.minigame_templates:
            self.log("⚠️ ВНИМАНИЕ: Не найдены картинки поплавка!")
    
    def match_best(self, gray_frame, templates):
        """Прогоняет matchTemplate по всем шаблонам, возвращает (max_val, max_loc, best_idx)."""
        best_val = -1.0
        best_loc = (0, 0)
        best_idx = -1
        for idx, tmpl in enumerate(templates):
            if tmpl is None:
                continue
            res = cv2.matchTemplate(gray_frame, tmpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > best_val:
                best_val = max_val
                best_loc = max_loc
                best_idx = idx
        return best_val, best_loc, best_idx
