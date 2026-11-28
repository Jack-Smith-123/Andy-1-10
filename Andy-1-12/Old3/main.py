from cameraStream import CameraStream
import asyncio

async def main():
    cam = CameraStream(camera_index=8)

    await asyncio.gather(
        cam.run_camera_feed(),
    )

asyncio.run(main())