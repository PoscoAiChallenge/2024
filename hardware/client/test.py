
import json
import base64
from dotenv import load_dotenv
import requests
import os
import gpiozero

load_dotenv()
URL = os.getenv('URL')
NUM_TRAIN = os.getenv('TRAIN')

motor = gpiozero.LED(18)

while True:
    res = requests.get(URL + '/speed/' + NUM_TRAIN)
    number = res.json().get('status')
    if number == '0':
        motor.off()
    elif number == '1':
        motor.on()
    else:
        print('Invalid speed value:', number)
        motor.off()
