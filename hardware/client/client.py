import os
import requests
import cv2
from gpiozero import PWMLED, LED
from dotenv import load_dotenv
from picamera2 import PiCamera2
import asyncio
from socket import socket, AF_INET, SOCK_DGRAM, bind, timeout, error
import base64

# Load environment variables
load_dotenv()

# Set up GPIO
URL = os.getenv('URL')
NUM_TRAIN = os.getenv('TRAIN')

# Set up socket
sock = socket(AF_INET, SOCK_DGRAM)
sock = bind((IP, PORT))

# set up GPIO
motor = LED(18)
buzzer = LED(4)

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()

while True:
    try:
        res = requests.get(URL + 'speed/' + NUM_TRAIN)

        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)

        if res.status_code == 200:
            data = res.json()
            speed = int(data['status'])
            
        if speed != 0:
            speed = max(0, min(speed, 100))  # Clamp speed between 0 and 100
            motor.on()
            requests.post(URL + '/log', json={'speed': speed, 'train': NUM_TRAIN})

        else:
            motor.off()
        
    except requests.RequestException as e:
        print(f'Request error: {e}')