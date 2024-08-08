from picamera2 import Picamera2
import cv2
import asyncio
import aiohttp
import time

async def send_frame(session, url, frame):
    try:
        async with session.post(url, data={'frame': frame}) as response:
            if response.status != 200:
                print(f'Error sending frame: HTTP {response.status}')
    except aiohttp.ClientError as e:
        print(f'Error sending frame: {e}')

async def main():
    camera = Picamera2()
    camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    camera.start()

    url = 'http://192.168.124.101:5000/post_frame'
    
    async with aiohttp.ClientSession() as session:
        frame_count = 0
        start_time = time.time()
        
        while True:
            frame = camera.capture_array()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()
            
            # 비동기로 프레임 전송
            asyncio.create_task(send_frame(session, url, frame_data))
            
            frame_count += 1
            elapsed_time = time.time() - start_time
            
            # 매 초마다 FPS 출력
            if elapsed_time >= 1:
                fps = frame_count / elapsed_time
                print(f"FPS: {fps:.2f}")
                frame_count = 0
                start_time = time.time()

            # 약간의 대기 시간을 줘서 CPU 사용량을 줄입니다
            await asyncio.sleep(0.001)

    camera.stop()

if __name__ == "__main__":
    asyncio.run(main())