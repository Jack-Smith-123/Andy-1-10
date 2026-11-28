from cameraStream import CameraStream
import asyncio

async def main():
    # В Linux индекс камеры часто 0 (вместо 8, как было в Windows-версии)
    # Если не работает, попробуй 1 или 2
    cam = CameraStream(camera_index=0)
    await asyncio.gather(cam.run_camera_feed())

if __name__ == "__main__":
    asyncio.run(main())
