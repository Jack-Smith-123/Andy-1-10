import cv2
import time
import pyautogui
import os
import numpy as np
from pynput import keyboard

pyautogui.PAUSE = 0.01
DEBUG_MODE = True

class FishingService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img1 = os.path.join(base_dir, "bobberExamples", "bobberExample2.png")
        img2 = os.path.join(base_dir, "bobberExamples", "bobberExampleInWatter2.png")
        
        self.bobberExample = cv2.imread(img1, cv2.IMREAD_GRAYSCALE)
        self.bobberExampleInWatter = cv2.imread(img2, cv2.IMREAD_GRAYSCALE)
        
        if self.bobberExample is None or self.bobberExampleInWatter is None:
            print("❌ ОШИБКА: Не найдены картинки поплавка в папке bobberExamples!")
            
        self.h, self.w = self.bobberExample.shape[:2]
        self.h_in, self.w_in = self.bobberExampleInWatter.shape[:2]
        
        self.last_bobber_y = None
        self.missing_frames = 0
        self.MISSING_FRAMES_LIMIT = 4
        self.BITE_Y_THRESHOLD = 5
        
        self.bobber_was_seen = False
        
        self.state = "IDLE"
        self.fishing_active = False
        self.state_enter_time = time.time()
        self.last_seen_time = time.time()
        self.mouse_down = False
        
        # Переменные для мини-игры
        self.time_in_zone = 0.0
        self.MIN_TIME_IN_ZONE = 5.0  # Нужно удерживать поплавок 5 секунд
        
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def _on_press(self, key):
        if key == keyboard.Key.f1:
            self.fishing_active = not self.fishing_active
            status = "ВКЛ 🟢" if self.fishing_active else "ВЫКЛ 🔴"
            print(f"\n--- Авто-рыбалка {status} ---")
            if self.fishing_active:
                self._set_state("STARTING")
            else:
                self._set_state("IDLE")
                if self.mouse_down:
                    self._mouse_release()

    def _set_state(self, new_state):
        self.state = new_state
        self.state_enter_time = time.time()
        print(f"➡️ STATE: {new_state}")
        if new_state == "HOOK":
            self.bobber_was_seen = False
            self.missing_frames = 0
        if new_state == "MINI_GAME":
            self.time_in_zone = 0.0
            self.last_seen_time = time.time()

    def _mouse_press(self):
        pyautogui.mouseDown(button='left')
        self.mouse_down = True
        print("  🟢 Mouse DOWN")

    def _mouse_release(self):
        pyautogui.mouseUp(button='left')
        self.mouse_down = False
        print("  🔴 Mouse UP")

    def _find_bobber_template(self, roi, template):
        """Поиск по шаблону (для HOOK состояния)."""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        h, w = template.shape[:2]
        return max_loc, max_val, (w, h)

    def _state_starting(self):
        if time.time() - self.state_enter_time < 2.0:
            return
        print("🎣 Забрасываем...")
        self._mouse_press()
        time.sleep(0.5)
        self._mouse_release()
        time.sleep(2.0)
        self._set_state("HOOK")

    def _state_hook(self, frame):
        if time.time() - self.state_enter_time < 1.0:
            return frame

        if not self.bobber_was_seen and (time.time() - self.state_enter_time > 30):
            print("⚠️ Поплавок так и не появился за 30 сек. Рестарт.")
            self._set_state("RESTART")
            return frame

        pos, score, (w, h) = self._find_bobber_template(frame, self.bobberExampleInWatter)

        if DEBUG_MODE:
            debug_frame = frame.copy()
            cv2.rectangle(debug_frame, pos, (pos[0] + w, pos[1] + h), (0, 255, 0), 2)
            cv2.putText(debug_frame, f"Score: {score:.2f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("HOOK - Bot Vision", debug_frame)

        if score < 0.50:
            self.missing_frames += 1
            if self.bobber_was_seen and self.missing_frames >= self.MISSING_FRAMES_LIMIT:
                print(f"🎯 КЛЮЁТ! (Поплавок исчез, score={score:.2f})")
                self._mouse_press()
                time.sleep(0.1)
                self._mouse_release()
                self._set_state("MINI_GAME")
            return frame

        self.missing_frames = 0
        self.bobber_was_seen = True
        
        x, y = pos
        current_bobber_y = y + (h // 2)

        if self.last_bobber_y is not None:
            dy = current_bobber_y - self.last_bobber_y
            if dy > self.BITE_Y_THRESHOLD:
                print(f"🎯 КЛЮЁТ! (Рывок вниз на {dy}px, score={score:.2f})")
                self._mouse_press()
                time.sleep(0.1)
                self._mouse_release()
                self._set_state("MINI_GAME")
                self.last_bobber_y = None
                return frame

        self.last_bobber_y = current_bobber_y
        return frame

    def _state_mini_game(self, frame):
        """Мини-игра: удерживаем оранжевый поплавок в центре кадра."""
        frame_h, frame_w, _ = frame.shape
        center_x = frame_w // 2
        
        # Ищем оранжевый/красный поплавок по цвету
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_orange = np.array([5, 100, 100])
        upper_orange = np.array([25, 255, 255])
        orange_mask = cv2.inRange(hsv, lower_orange, upper_orange)
        
        contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bobber_x = None
        bobber_y = None
        if contours:
            valid_contours = [c for c in contours if 50 < cv2.contourArea(c) < 5000]
            if valid_contours:
                largest = max(valid_contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest)
                bobber_x = x + w // 2
                bobber_y = y + h // 2
        
        # Отладка
        if DEBUG_MODE:
            debug_frame = frame.copy()
            cv2.line(debug_frame, (center_x, 0), (center_x, frame_h), (255, 0, 0), 2)
            cv2.line(debug_frame, (center_x - 30, 0), (center_x - 30, frame_h), (0, 255, 255), 1)
            cv2.line(debug_frame, (center_x + 30, 0), (center_x + 30, frame_h), (0, 255, 255), 1)
            if bobber_x is not None:
                cv2.circle(debug_frame, (bobber_x, bobber_y), 8, (0, 255, 0), 2)
            cv2.putText(debug_frame, f"Time: {self.time_in_zone:.1f}s / {self.MIN_TIME_IN_ZONE:.0f}s", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.imshow("MINI_GAME - Bot Vision", debug_frame)
        
        if bobber_x is None:
            if time.time() - self.last_seen_time > 1.5:
                print("⚠️ Потерян поплавок в мини-игре. Перезапуск.")
                self._set_state("RESTART")
            return frame
        
        self.last_seen_time = time.time()
        
        offset = bobber_x - center_x
        dead_zone = 30
        
        if offset < -dead_zone:
            if not self.mouse_down:
                self._mouse_press()
        elif offset > dead_zone:
            if self.mouse_down:
                self._mouse_release()
        
        # Счетчик времени в зоне
        if abs(offset) <= dead_zone:
            self.time_in_zone += 1/40
            if self.time_in_zone >= self.MIN_TIME_IN_ZONE:
                print(f"🎉 Рыба поймана! (удерживали {self.time_in_zone:.1f} сек)")
                self._set_state("STARTING")
                return frame
        else:
            self.time_in_zone = max(0, self.time_in_zone - 0.1)
        
        # Таймаут мини-игры
        if time.time() - self.state_enter_time > 25:
            print("⏱️ Таймаут мини-игры. Перезапуск.")
            self._set_state("RESTART")
        
        return frame

    def _state_restart(self):
        if time.time() - self.state_enter_time < 0.5:
            return
        print("🔄 Отмена и перезапуск...")
        if self.mouse_down:
            self._mouse_release()
        pyautogui.click(button='right')
        time.sleep(1)
        self._set_state("STARTING")

    def controller(self, frame):
        if not self.fishing_active:
            if DEBUG_MODE:
                cv2.destroyAllWindows()
            return frame

        if self.state == "STARTING":
            self._state_starting()
        elif self.state == "HOOK":
            self._state_hook(frame)
        elif self.state == "MINI_GAME":
            self._state_mini_game(frame)
        elif self.state == "RESTART":
            self._state_restart()
            
        return frame
