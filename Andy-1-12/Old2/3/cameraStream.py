import cv2
import asyncio
from fishingService import FishingService

class CameraStream:
    def __init__(self, camera_index=0):
        # В Linux используем CAP_V4L2 вместо CAP_DSHOW (который только для Windows)
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
        
        # Если CAP_V4L2 не сработает, пробуем стандартный режим
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(camera_index)
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.fishingService = FishingService()
        self.running = True

    async def run_camera_feed(self):
        if not self.cap.isOpened():
            print("❌ Не удалось открыть камеру. Проверьте индекс камеры и права доступа.")
            print("💡 Подсказка: в Linux индекс виртуальной камеры OBS часто равен 0 или 1.")
            return

        print("✅ Камера успешно подключена!")

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("⚠️ Нет кадров, проверь источник видео (например, OBS VirtualCam)")
                await asyncio.sleep(0.05)
                continue

            cropped = self.fishingService.controller(frame)

            # Раскомментируй для отладки:
            cv2.imshow("OBS Feed", frame)
            cv2.imshow("State Change", cropped)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

            await asyncio.sleep(1 / 40)  # стабильные ~40 FPS

        self.cap.release()
        cv2.destroyAllWindows()
