import cv2
import asyncio
import sys
from fishingService import FishingService


class CameraStream:
    def __init__(self, camera_index=0, fishing_service=None):
        self.fishingService = fishing_service if fishing_service is not None else FishingService()

        self.cap = None
        if sys.platform.startswith("linux"):
            backends = [cv2.CAP_V4L2, cv2.CAP_ANY]
        else:
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]

        for backend in backends:
            self.cap = cv2.VideoCapture(camera_index, backend)
            if self.cap.isOpened():
                print(f"✅ Камера открыта через бэкенд: {backend}")
                break

        if self.cap is None or not self.cap.isOpened():
            print(f"❌ Не удалось открыть камеру с индексом {camera_index}")
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.running = True

    async def run_camera_feed(self):
        if self.cap is None or not self.cap.isOpened():
            print("❌ Камера не доступна, выходим")
            return

        print("✅ Камера успешно подключена!")

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("⚠️ Нет кадров, проверь источник видео")
                await asyncio.sleep(0.05)
                continue

            cropped = self.fishingService.controller(frame)

            if self.fishingService.show_oss_feed:
                cv2.imshow("OBS Feed", frame)

            if self.fishingService.show_state_change:
                cv2.imshow("State Change", cropped)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

            await asyncio.sleep(1 / 40)

        self.cap.release()
        cv2.destroyAllWindows()
