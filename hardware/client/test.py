import json
import base64
from dotenv import load_dotenv
import os
from picamera2 import Picamera2
import cv2
import socket
import time
from datetime import datetime

load_dotenv()
SERVER_IP = os.getenv('SERVER_IP')
URL = os.getenv('URL')
NUM_TRAIN = os.getenv('TRAIN')

server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
server.connect((SERVER_IP, 9000))

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XBGR8888', "size": (400, 400)}))
camera.start()

def generate_frames():
    prev_frame = None
    motion_threshold = 5000  # Adjustable threshold

    while True:
        frame = camera.capture_array()
        
        # Convert XRGB8888 to BGR
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Motion detection (if needed)
        if prev_frame is not None:
            diff = cv2.absdiff(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY),
                               cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY))
            non_zero = cv2.countNonZero(diff)
            if non_zero <= motion_threshold:
                prev_frame = frame_bgr
                continue  # If no motion is detected, move to the next frame

        prev_frame = frame_bgr

        # JPEG compression
        ret, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        
        return frame_bytes

while True:
    image = generate_frames()
    base64_image = base64.b64encode(image).decode('utf-8')
    stime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

    data = json.dumps({
        "num_train": NUM_TRAIN,
        "image": base64_image,
    })  

    data_length = str(len(data))
    image_length = str(len(base64_image))

    print(f"Image length: {image_length}")
    print(f"Data length: {data_length}")
    print(f"Time: {stime}")

    server.sendall(data_length.encode().ljust(64))
    server.send(data.encode())
    server.send(stime.encode().ljust(64))

    time.sleep(0.05)

    

    #server.send(data.encode())
    #print("sending image")
    
    time.sleep(0.1)  # Add a small delay to control the frame rate