from cameraStream import CameraStream
import asyncio

async def main():
    # В Linux OBS Virtual Camera обычно имеет индекс 0 (или 1, если есть веб-камера)
    cam = CameraStream(camera_index=0)
    await asyncio.gather(
        cam.run_camera_feed(),
    )

if __name__ == "__main__":
    asyncio.run(main())
