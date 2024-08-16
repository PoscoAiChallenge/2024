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

server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (400, 400)}))
camera.start()

def generate_frames():
    while True:
        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        return frame
    
while True:
    image = generate_frames()
    base64_image = base64.b64encode(image).decode('utf-8')

    data = f'''
    {{
        "train_id": "{str(NUM_TRAIN)}",
        "image": "{base64_image}"
    }}

    '''

    server.sendto(str.encode(data), (SERVER_IP, 9000))
    print("sending image")
    time.sleep(0.01)