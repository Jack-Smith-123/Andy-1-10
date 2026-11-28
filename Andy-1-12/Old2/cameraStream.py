import cv2
import asyncio
from fishingService import FishingService

class CameraStream:
    def __init__(self, camera_index=0, fishing_service=None):
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(camera_index)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # ВАЖНО: используем переданный из GUI экземпляр, иначе настройки GUI не применятся
        self.fishingService = fishing_service if fishing_service is not None else FishingService()
        self.running = True

    async def run_camera_feed(self):
        if not self.cap.isOpened():
            print("❌ Не удалось открыть камеру. Проверь OBS Virtual Camera.")
            return

        print("✅ Камера подключена!")

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                await asyncio.sleep(0.05)
                continue

            self.fishingService.controller(frame)

            # окно полного OBS-фида (галка "Show OBS Feed")
            if getattr(self.fishingService, 'show_obs_feed', False):
                cv2.imshow("OBS Feed", frame)

            # waitKey обязателен, чтобы окна OpenCV перерисовывались и закрывались
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

            await asyncio.sleep(1/40)

        self.cap.release()
        cv2.destroyAllWindows()
