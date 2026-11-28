# test_core.py - Тест ядра бота в консоли
import time
import cv2
from config import WINDOW_TITLE, TARGET_FPS, TEMPLATE_PATH
from window_manager import WindowManager
from capture import ScreenCapture
from detector import BobberDetector

def main():
    print("🚀 Запуск теста ядра Andy-3...")
    
    wm = WindowManager(WINDOW_TITLE)
    if not wm.update_geometry():
        print("❌ Не удалось найти окно игры. Завершение.")
        return

    capture = ScreenCapture(wm)
    detector = BobberDetector(TEMPLATE_PATH)

    frame_time = 1.0 / TARGET_FPS
    print(f"✅ Бот готов! Целевой FPS: {TARGET_FPS}. Наведи мышь на поплавок. Ctrl+C для остановки.")

    try:
        while True:
            start_time = time.time()

            frame = capture.get_frame()
            mouse_pos = capture.get_mouse_rel()

            if frame is not None and mouse_pos is not None:
                bobber_pos, confidence = detector.find_in_roi(frame, mouse_pos)
                
                if bobber_pos:
                    print(f"🎯 Поплавок найден! Уверенность: {confidence:.2f} | Коорд: {bobber_pos}")
                else:
                    # Раскомментируй, если хочешь видеть, как бот "ищет"
                    # print(f"👀 Мышь: {mouse_pos}, Макс. совпадение: {confidence:.2f}")
                    pass

            elapsed = time.time() - start_time
            sleep_time = frame_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n🛑 Тест остановлен.")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
