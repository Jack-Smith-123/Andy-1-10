import cv2
import time
import numpy as np
import pyautogui
import subprocess
from pynput import keyboard

class FishingService():
    def __init__(self):
        self.bobberExample = cv2.imread("bobberExamples/bobberExample2.png", cv2.IMREAD_GRAYSCALE)
        self.bobberExampleInWatter = cv2.imread("bobberExamples/bobberExampleInWatter2.png", cv2.IMREAD_GRAYSCALE)
        
        if self.bobberExample is None or self.bobberExampleInWatter is None:
            raise FileNotFoundError("❌ Не удалось загрузить изображения поплавка! Проверь папку bobberExamples/")
            
        self.h, self.w = self.bobberExample.shape[:2]
        self.h_in, self.w_in = self.bobberExampleInWatter.shape[:2]

        self.last_bobber_y = None
        self.missing_frames = 0
        self.BITE_Y_THRESHOLD = 7
        self.MISSING_FRAMES_LIMIT = 4

        self.mouse_down = False
        self.previous_misings = []
        self.state_enter_time = time.time()
        self.last_seen_time = time.time()
        self.NO_OBJECT_TIMEOUT = 2.0
        self.state = "STARTING"

        self.fishing_active = False
        
        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<f1>': self.toggle_fishing
        })
        self.hotkey_listener.start()
        
        # ВАЖНО: Впиши сюда ТОЧНОЕ название окна игры, которое выдаёт xdotool
        self.window_title = "Albion Online" 

    def toggle_fishing(self):
        self.fishing_active = not self.fishing_active
        print("\n" + "="*40)
        print("🟢 Авто-рыбалка ВКЛ" if self.fishing_active else "🔴 Авто-рыбалка ВЫКЛ")
        print("="*40 + "\n")
        if self.fishing_active:
            self.set_state("STARTING")

    def set_state(self, new_state):
        self.state = new_state
        self.state_enter_time = time.time()
        if new_state == "MINI GAME":
            self.last_seen_time = time.time()
            self.mouse_down = False
        print(f"➡️ STATE → {new_state}")

    def mouse_press(self):
        pyautogui.mouseDown(button='left')
        self.mouse_down = True
        print("🟢 Mouse DOWN")

    def mouse_release(self):
        pyautogui.mouseUp(button='left')
        self.mouse_down = False
        print("🔴 Mouse UP")

    def get_game_window_rect(self, window_title):
        try:
            result = subprocess.run(['xdotool', 'search', '--name', window_title], capture_output=True, text=True)
            window_ids = result.stdout.strip().split('\n')
            
            # Фильтруем пустые строки
            window_ids = [wid for wid in window_ids if wid]
            
            if not window_ids:
                print(f"⚠️ Окно с именем '{window_title}' НЕ НАЙДЕНО!")
                return None
            
            window_id = window_ids[0]
            geom_result = subprocess.run(['xdotool', 'getwindowgeometry', '--shell', window_id], capture_output=True, text=True)
            geom = {}
            for line in geom_result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=')
                    geom[key] = int(value)
            
            left = geom.get('X', 0)
            top = geom.get('Y', 0)
            width = geom.get('WIDTH', 0)
            height = geom.get('HEIGHT', 0)
            
            return left, top, left + width, top + height
        except Exception as e:
            print(f"❌ Ошибка xdotool: {e}")
            return None

    def crop_mouse_area(self, frame, window_title, crop_w=300, crop_h=300):
        rect = self.get_game_window_rect(window_title)
        if not rect:
            return None  # Если окно не найдено, возвращаем None

        left, top, right, bottom = rect
        win_w = right - left
        win_h = bottom - top

        mx, my = pyautogui.position()
        rel_x = mx - left
        rel_y = my - top

        # Если мышь вне окна игры
        if rel_x < 0 or rel_y < 0 or rel_x > win_w or rel_y > win_h:
            print("⚠️ Мышь находится ВНЕ окна игры! Верни мышь в окно Albion.")
            return None

        frame_h, frame_w, _ = frame.shape
        
        # Масштабируем координаты мыши под размер кадра из OBS
        fx = int(rel_x * frame_w / win_w)
        fy = int(rel_y * frame_h / win_h)

        x1 = max(fx - crop_w // 2, 0)
        y1 = max(fy - crop_h // 2, 0)
        x2 = min(fx + crop_w // 2, frame_w)
        y2 = min(fy + crop_h // 2, frame_h)

        return frame[y1:y2, x1:x2]

    def find_bobber_in_roi(self, roi):
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray, self.bobberExampleInWatter, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        # СНИЗИЛИ порог с 0.63 до 0.55 для VMware + OBS (сжатие меняет пиксели)
        if max_val < 0.55:
            return None, max_val
        return max_loc, max_val

    def start_state(self):
        if time.time() - self.state_enter_time < 3:
            return
        print("🎣 Заброс удочки...")
        self.mouse_press()
        time.sleep(1)
        self.mouse_release()
        time.sleep(2)
        self.set_state("HOOK")

    def reset_state(self):
        if self.mouse_down:
            self.mouse_release()
        if time.time() - self.state_enter_time < 0.5:
            return
        print("🔄 Перезапуск...")
        pyautogui.click(button='right')
        time.sleep(1)
        self.set_state("STARTING")

    def hook_state(self, frame):
        if time.time() - self.state_enter_time < 1:
            return frame

        roi = self.crop_mouse_area(frame, self.window_title, crop_w=300, crop_h=300)
        
        if roi is None:
            # Рисуем предупреждение на главном кадре
            cv2.putText(frame, "WINDOW NOT FOUND / MOUSE OUTSIDE", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return frame

        pos, score = self.find_bobber_in_roi(roi)

        if pos is None:
            self.missing_frames += 1
            # Для отладки: показываем максимальный найденный процент совпадения
            if self.missing_frames % 10 == 0:
                print(f"🔍 Поиск... (лучшее совпадение: {score:.2f})")

            if self.missing_frames >= self.MISSING_FRAMES_LIMIT and len(self.previous_misings) >= 2:
                print("🎯 КЛЁВ! (поплавок исчез)")
                self.mouse_press()
                time.sleep(0.05)
                self.mouse_release()
                self.set_state("MINI GAME")
                self.last_bobber_y = None
                self.missing_frames = 0
                self.previous_misings = []
            elif self.missing_frames >= self.MISSING_FRAMES_LIMIT and len(self.previous_misings) == 0:
                print("⚠️ Поплавок не найден, перезапуск")
                self.set_state("RESTART")
                self.last_bobber_y = None
                self.missing_frames = 0
                self.previous_misings = []
            return frame

        # Если нашли!
        self.missing_frames = 0
        if len(self.previous_misings) <= 2:
            self.previous_misings.append(1)

        x, y = pos
        bobber_y = y + self.h_in // 2

        # Рисуем зелёную рамку вокруг найденного поплавка в ROI
        cv2.rectangle(roi, (x, y), (x + self.w_in, y + self.h_in), (0, 255, 0), 2)
        cv2.putText(roi, f"Score: {score:.2f}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        if self.last_bobber_y is not None:
            dy = bobber_y - self.last_bobber_y
            if dy > self.BITE_Y_THRESHOLD:
                print(f"🎯 КЛЁВ! (Скачок Y: {dy})")
                self.mouse_press()
                time.sleep(0.05)
                self.mouse_release()
                self.set_state("MINI GAME")
                self.last_bobber_y = None
                self.missing_frames = 0
                self.previous_misings = []
                return frame

        self.last_bobber_y = bobber_y
        return frame

    def find_bober(self, frame):
        # Логика мини-игры (оставляем как есть, но добавляем визуализацию)
        cropped = self.crop_center(frame, 130, 50)
        if cropped is None or cropped.size == 0:
            return frame

        frame_resized = cv2.resize(cropped, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        gray_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray_frame, self.bobberExample, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        now = time.time()
        if max_val < 0.65: # Чуть снизили порог для мини-игры
            if now - self.last_seen_time > self.NO_OBJECT_TIMEOUT:
                self.set_state("RESTART")
            return frame

        self.last_seen_time = time.time()
        x, y = max_loc

        cv2.rectangle(frame_resized, (x, y), (x + self.w, y + self.h), (0, 255, 0), 2)
        
        # Логика удержания для мини-игры
        if x <= 55 or x <= 130:
            if not self.mouse_down:
                self.mouse_press()
        elif x >= 158:
            if self.mouse_down:
                self.mouse_release()

        return frame

    def controller(self, frame):
        if self.fishing_active:
            if self.state == "STARTING":
                self.start_state()
                return frame
            elif self.state == "HOOK":
                return self.hook_state(frame)
            elif self.state == "MINI GAME":
                return self.find_bober(frame)
            elif self.state == "RESTART":
                self.reset_state()
                return frame
        return frame
