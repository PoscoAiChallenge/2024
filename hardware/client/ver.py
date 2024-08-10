import os
import requests
import cv2
from gpiozero import PWMLED, LED
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up GPIO
URL = str(os.getenv('URL'))
NUM_TRAIN = str(os.getenv('TRAIN'))

# set up GPIO
motor = LED(17)

while True:
    try:
        res = requests.get(URL + '/speed/' + NUM_TRAIN)

        if res.status_code == 200:
            data = res.json()
            speed = int(data['status'])
            
        if speed != 0:
            speed = max(0, min(speed, 100))  # Clamp speed between 0 and 100
            motor.on()
            requests.post(URL + '/log', json={'speed': speed, 'train': NUM_TRAIN})
        else:
            motor.off()
            requests.post(URL + '/log', json={'speed': 0, 'train': NUM_TRAIN})
        
    except requests.RequestException as e:
        print(f'Request error: {e}')