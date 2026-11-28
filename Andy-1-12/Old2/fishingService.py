import cv2
import time
import pyautogui
import os
import numpy as np
from pynput import keyboard

pyautogui.PAUSE = 0.01

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

        # === НАСТРАИВАЕМЫЕ ПАРАМЕТРЫ (управляются из GUI) ===
        self.BOBBERT_MATCH_THRESHOLD = 0.62   # порог совпадения шаблона (hook + minigame)
        self.BITE_Y_THRESHOLD = 7             # рывок по Y = клёв

        # === ГАЛКИ ОТЛАДКИ (управляются из GUI) ===
        self.show_obs_feed = False
        self.show_state_change = False

        self.last_bobber_y = None
        self.last_bobber_x = None
        self.missing_frames = 0
        self.MISSING_FRAMES_LIMIT = 4
        self.MAX_X_JUMP = 80
        self.MIN_SEEN_FRAMES = 4

        self.bobber_was_seen = False
        self.seen_streak = 0

        self.state = "IDLE"
        self.fishing_active = False
        self.state_enter_time = time.time()
        self.last_seen_time = time.time()
        self.mouse_down = False

        self.time_in_zone = 0.0
        self.MIN_TIME_IN_ZONE = 3.0
        self.last_action_time = 0

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
            self.seen_streak = 0
            self.missing_frames = 0
            self.last_bobber_y = None
            self.last_bobber_x = None
        if new_state == "MINI_GAME":
            self.time_in_zone = 0.0
            self.last_seen_time = time.time()
            self.last_action_time = 0

    def _mouse_press(self):
        pyautogui.mouseDown(button='left')
        self.mouse_down = True
        print("  🟢 Mouse DOWN")

    def _mouse_release(self):
        pyautogui.mouseUp(button='left')
        self.mouse_down = False
        print("  🔴 Mouse UP")

    def crop_center(self, frame, crop_w=130, crop_h=50):
        h, w, _ = frame.shape
        cx, cy = w // 2, h // 2
        x1 = max(cx - crop_w // 2, 0)
        y1 = max(cy - crop_h // 2, 0)
        x2 = min(cx + crop_w // 2, w)
        y2 = min(cy + crop_h // 2, h)
        return frame[y1:y2, x1:x2]

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

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray, self.bobberExampleInWatter, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        bx, by = max_loc

        if self.show_state_change:
            debug_frame = frame.copy()
            if max_val >= self.BOBBERT_MATCH_THRESHOLD:
                cv2.rectangle(debug_frame, (bx, by), (bx + self.w_in, by + self.h_in), (0, 255, 0), 2)
            cv2.putText(debug_frame, f"Score: {max_val:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("HOOK - Bot Vision", debug_frame)

        if max_val < self.BOBBERT_MATCH_THRESHOLD:
            self.missing_frames += 1
            if self.bobber_was_seen and self.seen_streak >= self.MIN_SEEN_FRAMES and self.missing_frames >= self.MISSING_FRAMES_LIMIT:
                print(f"🎯 КЛЮЁТ! (Поплавок исчез, score={max_val:.2f})")
                self._mouse_press()
                time.sleep(0.1)
                self._mouse_release()
                self._set_state("MINI_GAME")
            return frame

        self.missing_frames = 0
        self.seen_streak += 1
        if self.seen_streak >= self.MIN_SEEN_FRAMES:
            self.bobber_was_seen = True

        current_bobber_y = by + (self.h_in // 2)
        current_bobber_x = bx + (self.w_in // 2)

        if self.bobber_was_seen and self.last_bobber_y is not None:
            dy = current_bobber_y - self.last_bobber_y
            dx = abs(current_bobber_x - self.last_bobber_x)
            if dx > self.MAX_X_JUMP:
                self.last_bobber_y = current_bobber_y
                self.last_bobber_x = current_bobber_x
                return frame
            if dy > self.BITE_Y_THRESHOLD:
                print(f"🎯 КЛЮЁТ! (Рывок вниз на {dy}px, score={max_val:.2f})")
                self._mouse_press()
                time.sleep(0.1)
                self._mouse_release()
                self._set_state("MINI_GAME")
                self.last_bobber_y = None
                return frame

        self.last_bobber_y = current_bobber_y
        self.last_bobber_x = current_bobber_x
        return frame

    def _state_mini_game(self, frame):
        cropped = self.crop_center(frame, 130, 50)
        if cropped is None or cropped.size == 0:
            return frame

        zoomed = cv2.resize(cropped, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        gray = cv2.cvtColor(zoomed, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray, self.bobberExample, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        now = time.time()

        if max_val < self.BOBBERT_MATCH_THRESHOLD:
            if (now - self.last_seen_time > 2.0) or (now - self.state_enter_time > 15):
                print("⏱️ Мини-игра завершена. Перезапуск.")
                if self.mouse_down:
                    self._mouse_release()
                self._set_state("STARTING")
            return frame

        self.last_seen_time = now
        x, y = max_loc

        if self.show_state_change:
            debug_frame = zoomed.copy()
            cv2.rectangle(debug_frame, (x, y), (x + self.w, y + self.h), (0, 255, 0), 2)
            cv2.line(debug_frame, (130, 0), (130, 100), (255, 0, 0), 1)
            cv2.line(debug_frame, (158, 0), (158, 100), (0, 0, 255), 1)
            cv2.putText(debug_frame, f"X: {x} | Score: {max_val:.2f}", (5, 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.imshow("MINI_GAME - Bot Vision", debug_frame)

        # оригинальная простая логика: левая половина -> тянем, правая -> отпускаем
        if x <= 130:
            if not self.mouse_down:
                self._mouse_press()
        elif x >= 158:
            if self.mouse_down:
                self._mouse_release()

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
