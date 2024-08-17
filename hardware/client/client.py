
import json
import base64
from dotenv import load_dotenv
import requests
import os
import gpiozero
from picamera2 import Picamera2
import cv2
import threading
from socket import *
import time
from datetime import datetime

load_dotenv()
SERVER_IP = os.getenv('SERVER_IP')
URL = os.getenv('URL')
NUM_TRAIN = os.getenv('TRAIN')


motor = gpiozero.LED(18)

server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
server.connect((SERVER_IP, 9000))

motor_status = 0

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (400, 400)}))
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
    
def send_image():
    while True:
        image = generate_frames()
        base64_image = base64.b64encode(image).decode('utf-8')

        data = json.dumps({
            "train_id": NUM_TRAIN,
            "image": base64_image,
        })  

        data_length = str(len(data))

        server.sendall(data_length.encode().ljust(64))
        server.send(data.encode())

        time.sleep(0.05)

image_thread = threading.Thread(target=send_image, daemon=True)
image_thread.start()

while True:
    res = requests.get(URL + '/speed/' + NUM_TRAIN)
    number = res.json().get('status')

    if number == 0:
        motor.off()
        
        if motor_status == 1:
            motor_status = 0
        else:
            requests.post(URL + '/log', json={'status': 'Motor' + NUM_TRAIN + ' is off'})
    elif number == 1:
        motor.on()

        if motor_status == 0:
            motor_status = 1
        else:
            requests.post(URL + '/log', json={'status': 'Motor' + NUM_TRAIN + ' is on'})
    else:
        print('Invalid speed value:', number)
        motor.off()
        motor_status = 0
        requests.post(URL + '/log', json={'status': 'Invalid speed value: ' + str(number)})
    time.sleep(0.01)