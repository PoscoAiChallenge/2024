import json
import base64
from dotenv import load_dotenv
import os
from picamera2 import Picamera2
import cv2
import socket
import time

load_dotenv()
SERVER_IP = os.getenv('SERVER_IP')
URL = os.getenv('URL')
NUM_TRAIN = os.getenv('TRAIN')

server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
server.connect((SERVER_IP, 9000))

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (400, 400)}))
camera.start()

def generate_frames():
    prev_frame = None
    motion_threshold = 5000  # 조정 가능한 임계값

    while True:
        if frame_buffer.empty():
            time.sleep(0.001)
            continue

        frame = frame_buffer.get()
        
        # YUV420에서 BGR로 변환
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_I420)

        # 모션 감지 (필요한 경우)
        if prev_frame is not None:
            diff = cv2.absdiff(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY),
                               cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY))
            non_zero = cv2.countNonZero(diff)
            if non_zero <= motion_threshold:
                prev_frame = frame_bgr
                continue  # 모션이 감지되지 않으면 다음 프레임으로

        prev_frame = frame_bgr

        # JPEG 압축
        ret, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        
        return frame_bytes

while True:
    image = generate_frames()
    base64_image = base64.b64encode(image).decode('utf-8')
    image_length = str(len(base64_image))
    stime = datetime.utnow().strftime('%Y-%m-%d %H:%M:%S.%f')

    server.sendall(image_length.encode())
    server.send(base64_image.encode())
    server.send(stime.encode())

    data = f'''
    {{
        "train_id": "{str(NUM_TRAIN)}",
        "image": "{base64_image}"
    }}

    '''

    server.send(data.encode())
    print("sending image")