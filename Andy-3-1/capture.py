import subprocess
import mss
import numpy as np
import cv2

def find_albion_window():
    """Ищет окно через wmctrl и получает координаты через xwininfo."""
    try:
        result = subprocess.run(
            ["wmctrl", "-l"],
            capture_output=True, text=True, check=True
        )
        
        window_id = None
        for line in result.stdout.strip().split('\n'):
            if "Albion Online Client" in line:
                window_id = line.split()[0]
                break
        
        if not window_id:
            return "Окно 'Albion Online Client' не найдено"
        
        geo = subprocess.run(
            ["xwininfo", "-id", window_id],
            capture_output=True, text=True, check=True
        )
        
        coords = {}
        for line in geo.stdout.split('\n'):
            if "Absolute upper-left X:" in line:
                coords['X'] = int(line.split(':')[1].strip())
            elif "Absolute upper-left Y:" in line:
                coords['Y'] = int(line.split(':')[1].strip())
            elif "Width:" in line:
                coords['WIDTH'] = int(line.split(':')[1].strip())
            elif "Height:" in line:
                coords['HEIGHT'] = int(line.split(':')[1].strip())
        
        return {
            "id": window_id,
            "left": coords.get('X', 0),
            "top": coords.get('Y', 0),
            "width": coords.get('WIDTH', 1024),
            "height": coords.get('HEIGHT', 768)
        }
        
    except subprocess.CalledProcessError as e:
        return f"Ошибка выполнения команды: {e}"
    except Exception as e:
        return f"Неожиданная ошибка: {e}"

def grab_frame(monitor_rect):
    """Делает снимок указанной области."""
    with mss.mss() as sct:
        screenshot = sct.grab(monitor_rect)
        frame = np.array(screenshot)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

def get_cursor_position(window_data):
    """Получает позицию курсора мыши относительно окна игры."""
    try:
        result = subprocess.run(
            ["xdotool", "getmouselocation"],
            capture_output=True, text=True, check=True
        )
        
        # Парсим вывод: x:123 y:456 screen:0 window:0x...
        parts = result.stdout.strip().split()
        x = int(parts[0].split(':')[1])
        y = int(parts[1].split(':')[1])
        
        # Переводим в координаты окна
        rel_x = x - window_data['left']
        rel_y = y - window_data['top']
        
        # Проверяем, что курсор внутри окна
        if 0 <= rel_x < window_data['width'] and 0 <= rel_y < window_data['height']:
            return (rel_x, rel_y)
        
        return None
        
    except Exception as e:
        return None
