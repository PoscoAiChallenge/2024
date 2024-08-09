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
IP = os.getenv('IP')
PORT = os.getenv('PORT')

# Set up socket
sock = socket(AF_INET, SOCK_DGRAM)
sock = bind((IP, PORT))

# set up GPIO
motor = PWMLED(18)
buzzer = LED(4)

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()

async def horn():
    buzzer.on()
    await asyncio.sleep(0.5)
    buzzer.off()
    await asyncio.sleep(0.5)

    return True

while True:
    try:
        res = requests.get(URL + 'speed/' + NUM_TRAIN)

        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        sock.sendto(base64.b64encode(buffer.tobytes()), (IP, PORT))

        if res.status_code == 200:
            data = res.json()
            speed = int(data['status'])
            
        if speed != 0:
            speed = max(0, min(speed, 100))  # Clamp speed between 0 and 100
            motor.value = speed / 100
            requests.post(URL + '/log', json={'speed': speed, 'train': NUM_TRAIN})
            await horn()

        else:
            print('Invalid status')
        
    except requests.RequestException as e:
        sock.close()
        print(f'Request error: {e}')