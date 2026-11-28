# window_manager.py - Управление окном игры
import subprocess

class WindowManager:
    def __init__(self, title):
        self.title = title
        self.rect = {"top": 0, "left": 0, "width": 1024, "height": 768}
        self.is_found = False

    def update_geometry(self):
        """Ищет окно и обновляет его координаты."""
        try:
            result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True, check=True)
            window_id = None
            for line in result.stdout.strip().split('\n'):
                if self.title in line:
                    window_id = line.split()[0]
                    break
            
            if not window_id:
                print(f"⚠️ Окно '{self.title}' не найдено!")
                self.is_found = False
                return False

            geo = subprocess.run(["xwininfo", "-id", window_id], capture_output=True, text=True, check=True)
            coords = {}
            for line in geo.stdout.split('\n'):
                if "Absolute upper-left X:" in line: coords['X'] = int(line.split(':')[1].strip())
                elif "Absolute upper-left Y:" in line: coords['Y'] = int(line.split(':')[1].strip())
                elif "Width:" in line: coords['WIDTH'] = int(line.split(':')[1].strip())
                elif "Height:" in line: coords['HEIGHT'] = int(line.split(':')[1].strip())

            self.rect = {
                "top": coords.get('Y', 0),
                "left": coords.get('X', 0),
                "width": coords.get('WIDTH', 1024),
                "height": coords.get('HEIGHT', 768)
            }
            self.is_found = True
            print(f"✅ Окно найдено: {self.rect['width']}x{self.rect['height']}")
            return True
        except Exception as e:
            print(f"❌ Ошибка поиска окна: {e}")
            self.is_found = False
            return False
