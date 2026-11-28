import cv2
import time
import numpy as np
import os
import glob
import sys
import subprocess
from pynput.mouse import Controller as MouseController, Button
from pynput import keyboard

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


class LinuxWindowFinder:
    def __init__(self):
        self.cached_rect = None
        self.last_check_time = 0
        self.CACHE_TTL = 1.0
        
        # Проверяем, что xdotool установлен
        try:
            subprocess.run(['xdotool', '--version'], 
                         capture_output=True, timeout=2)
            print("✅ xdotool найден")
            self.has_xdotool = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("⚠️ xdotool не установлен! Установи: sudo apt install xdotool")
            self.has_xdotool = False

    def get_mouse_position(self):
        """Получает координаты мыши через xdotool"""
        if not self.has_xdotool:
            return None, None
        
        try:
            result = subprocess.run(
                ['xdotool', 'getmouselocation'],
                capture_output=True, text=True, timeout=1
            )
            if result.returncode == 0:
                # Парсим: "x:1167 y:216 screen:0 window:0x3e00001"
                parts = result.stdout.strip().split()
                x = int(parts[0].split(':')[1])
                y = int(parts[1].split(':')[1])
                return x, y
        except Exception as e:
            print(f"⚠️ Ошибка xdotool (mouse): {e}")
        return None, None

    def find_window_rect(self, title_substr):
        """Ищет окно через xdotool"""
        if not self.has_xdotool:
            return None
        
        # Проверяем кэш
        now = time.time()
        if self.cached_rect and (now - self.last_check_time) < self.CACHE_TTL:
            return self.cached_rect
        
        try:
            # Ищем окно по названию
            result = subprocess.run(
                ['xdotool', 'search', '--name', title_substr],
                capture_output=True, text=True, timeout=1
            )
            if result.returncode != 0 or not result.stdout.strip():
                self.cached_rect = None
                return None
            
            window_id = result.stdout.strip().split('\n')[0]
            
            # Получаем геометрию окна
            result = subprocess.run(
                ['xdotool', 'getwindowgeometry', '--shell', window_id],
                capture_output=True, text=True, timeout=1
            )
            if result.returncode == 0:
                props = {}
                for line in result.stdout.strip().split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        props[key] = int(value)
                
                x = props.get('X', 0)
                y = props.get('Y', 0)
                width = props.get('WIDTH', 0)
                height = props.get('HEIGHT', 0)
                
                rect = (x, y, x + width, y + height)
                self.cached_rect = rect
                self.last_check_time = now
                return rect
        except Exception as e:
            print(f"⚠️ Ошибка xdotool (window): {e}")
        
        return None


class FishingService:
    def __init__(self):
        self.mouse = MouseController()  # Только для кликов
        self.win_finder = LinuxWindowFinder()
        
        self.bobberExamples = []
        self.bobberExamplesInWater = []
        
        example_files = sorted(glob.glob("bobberExamples/*Example*.png"))
        water_files = sorted(glob.glob("bobberExamples/*InWatter*.png"))
        
        for f in example_files:
            img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                self.bobberExamples.append(img)
                print(f"✅ Загружен шаблон: {f}")
        
        for f in water_files:
            img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                self.bobberExamplesInWater.append(img)
                print(f"✅ Загружен шаблон в воде: {f}")
        
        if not self.bobberExamples or not self.bobberExamplesInWater:
            print("⚠️ Не найдено шаблонов в bobberExamples/!")
        
        self.h, self.w = self.bobberExamples[0].shape[:2] if self.bobberExamples else (50, 50)
        self.h_in, self.w_in = self.bobberExamplesInWater[0].shape[:2] if self.bobberExamplesInWater else (50, 50)
        
        self.last_bobber_y = None
        self.missing_frames = 0
        self.BITE_Y_THRESHOLD = 7
        self.MISSING_FRAMES_LIMIT = 4
        self.BOBBERT_MATCH_THRESHOLD = 0.63
        self.mouse_down = False
        self.previous_misings = []
        self.state_enter_time = time.time()
        self.last_seen_time = time.time()
        self.NO_OBJECT_TIMEOUT = 2.0
        self.state = "STARTING"
        self.fishing_active = False
        self.initiat_keyboard = False
        self.show_oss_feed = False
        self.show_state_change = False
        
        self.window_title = "Albion"
        self._last_debug_time = 0

    def toggle_fishing(self):
        self.fishing_active = not self.fishing_active
        print("Авто-рыбалка ВКЛ 🟢" if self.fishing_active else "Авто-рыбалка ВЫКЛ 🔴")
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
        self.mouse.press(Button.left)
        self.mouse_down = True
        print("🟢 Mouse DOWN")

    def mouse_release(self):
        self.mouse.release(Button.left)
        self.mouse_down = False
        print("🔴 Mouse UP")

    def crop_center(self, frame, crop_w=130, crop_h=50):
        h, w, _ = frame.shape
        center_x = w // 2
        center_y = h // 2
        x1 = max(center_x - crop_w // 2, 0)
        y1 = max(center_y - crop_h // 2, 0)
        x2 = min(center_x + crop_w // 2, w)
        y2 = min(center_y + crop_h // 2, h)
        return frame[y1:y2, x1:x2]

    def get_game_window_rect(self, window_title):
        return self.win_finder.find_window_rect(window_title)

    def map_mouse_to_frame_window(self, frame, window_title):
        # Используем xdotool для мыши (корректно в VMware!)
        mx, my = self.win_finder.get_mouse_position()
        if mx is None:
            return None, None
        
        rect = self.get_game_window_rect(window_title)
        if not rect:
            return None, None
        
        left, top, right, bottom = rect
        win_w = right - left
        win_h = bottom - top
        
        rel_x = mx - left
        rel_y = my - top
        
        # Отладка раз в 2 секунды
        now = time.time()
        if now - self._last_debug_time > 2:
            print(f"🖱️ Mouse: ({mx}, {my}) | Window: ({left}, {top}, {right}, {bottom}) | Relative: ({rel_x}, {rel_y}) | WinSize: ({win_w}, {win_h})")
            self._last_debug_time = now
        
        if rel_x < 0 or rel_y < 0 or rel_x > win_w or rel_y > win_h:
            return None, None
        
        frame_h, frame_w, _ = frame.shape
        fx = int(rel_x * frame_w / win_w)
        fy = int(rel_y * frame_h / win_h)
        return fx, fy

    def crop_mouse_area(self, frame, window_title, crop_w=100, crop_h=100):
        fx, fy = self.map_mouse_to_frame_window(frame, window_title)
        if fx is None:
            return None
        
        x1 = max(fx - crop_w // 2, 0)
        y1 = max(fy - crop_h // 2, 0)
        x2 = min(fx + crop_w // 2, frame.shape[1])
        y2 = min(fy + crop_h // 2, frame.shape[0])
        return frame[y1:y2, x1:x2]

    def find_bobber_in_roi(self, roi):
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        best_loc = None
        best_val = 0.0
        
        for template in self.bobberExamplesInWater:
            res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > best_val:
                best_val = max_val
                best_loc = max_loc
        
        if best_val < self.BOBBERT_MATCH_THRESHOLD:
            return None, best_val
        return best_loc, best_val

    def start_state(self):
        if time.time() - self.state_enter_time < 3:
            return
        print("🎣 Casting...")
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
        self.mouse.press(Button.right)
        self.mouse.release(Button.right)
        self.set_state("STARTING")

    def hook_state(self, frame):
        if time.time() - self.state_enter_time < 1:
            return frame
        
        roi = self.crop_mouse_area(frame, self.window_title, crop_w=300, crop_h=300)
        
        if roi is None:
            return frame
        
        pos, score = self.find_bobber_in_roi(roi)
        
        if pos is None:
            self.missing_frames += 1
            if self.missing_frames >= self.MISSING_FRAMES_LIMIT and len(self.previous_misings) >= 2:
                print(f"🎯 BITE (bobber disappeared, score={score:.3f})")
                self.mouse_press()
                time.sleep(0.05)
                self.mouse_release()
                self.set_state("MINI GAME")
                self.last_bobber_y = None
                self.missing_frames = 0
                self.previous_misings = []
            elif self.missing_frames >= self.MISSING_FRAMES_LIMIT and len(self.previous_misings) == 0:
                print("⚠️ Поплавок не найден в этом статусе!")
                self.set_state("RESTART")
                self.last_bobber_y = None
                self.missing_frames = 0
                self.previous_misings = []
            return roi
        
        self.missing_frames = 0
        if len(self.previous_misings) <= 2:
            self.previous_misings.append(1)
        
        x, y = pos
        bobber_y = y + self.h_in // 2
        cv2.rectangle(roi, (x, y), (x + self.w_in, y + self.h_in), (0, 255, 255), 2)
        
        if self.last_bobber_y is not None:
            dy = bobber_y - self.last_bobber_y
            if dy > self.BITE_Y_THRESHOLD:
                print(f"🎯 BITE (Y jump: {dy})")
                self.mouse_press()
                time.sleep(0.05)
                self.mouse_release()
                self.set_state("MINI GAME")
                self.last_bobber_y = None
                self.missing_frames = 0
                self.previous_misings = []
                return roi
        
        self.last_bobber_y = bobber_y
        return roi

    def find_bober(self, frame):
        cropped = self.crop_center(frame, 130, 50)
        if cropped is None or cropped.size == 0:
            return frame
        
        frame = cv2.resize(cropped, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        best_loc = None
        best_val = 0.0
        
        for template in self.bobberExamples:
            res = cv2.matchTemplate(gray_frame, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > best_val:
                best_val = max_val
                best_loc = max_loc
        
        now = time.time()
        if best_val < self.BOBBERT_MATCH_THRESHOLD:
            if now - self.last_seen_time > self.NO_OBJECT_TIMEOUT:
                self.set_state("RESTART")
            return frame
        
        self.last_seen_time = time.time()
        x, y = best_loc
        cv2.rectangle(frame, (x, y), (x + self.w, y + self.h), (0, 255, 255), 2)
        
        if x <= 55 or x <= 130:
            if not self.mouse_down:
                self.mouse_press()
        elif x >= 158:
            if self.mouse_down:
                self.mouse_release()
        
        return frame

    def controller(self, frame):
        if not self.initiat_keyboard:
            def on_press(key):
                try:
                    if key == keyboard.Key.f1:
                        self.toggle_fishing()
                except AttributeError:
                    if hasattr(key, 'vk') and key.vk == 67:
                        self.toggle_fishing()
            
            try:
                self.listener = keyboard.Listener(on_press=on_press)
                self.listener.daemon = True
                self.listener.start()
                self.initiat_keyboard = True
                print("✅ Keyboard listener запущен")
            except Exception as e:
                print(f"⚠️ Не удалось запустить keyboard listener: {e}")
        
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
        else:
            return frame
