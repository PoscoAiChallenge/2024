
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

load_dotenv()
URL = os.getenv('URL')
NUM_TRAIN = os.getenv('TRAIN')

SERVER_IP = os.getenv('SERVER_IP')

motor = gpiozero.LED(18)

s = socket(family=AF_INET, type=SOCK_DGRAM)

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (400, 400)}))
camera.start()

def generate_frames():
    while True:
        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        return frame
    
def send_image():
    while True:
        image = generate_frames()
        base64_image = base64.b64encode(image).decode('utf-8')
        s.sendto(json.dumps({'train_id': NUM_TRAIN, 'image': base64_image}).encode(), (SERVER_IP, 9000))

image_thread = threading.Thread(target=send_image, daemon=True)
image_thread.start()

while True:
    res = requests.get(URL + '/speed/' + NUM_TRAIN)
    number = res.json().get('status')
    if number == '0':
        motor.off()
        requests.post(URL + '/log', json={'status': 'Motor' + NUM_TRAIN + ' is off'})
    elif number == '1':
        motor.on()
        requests.post(URL + '/log', json={'status': 'Motor' + NUM_TRAIN + ' is on'})
    else:
        print('Invalid speed value:', number)
        motor.off()
        requests.post(URL + '/log', json={'status': 'Invalid speed value: ' + number})