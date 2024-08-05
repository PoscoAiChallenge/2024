import os
import requests
import time
import RPi.GPIO as GPIO
from dotenv import load_dotenv
from cam import PiCameraStreamer

# Load environment variables
load_dotenv()

# Set up GPIO
URL = os.getenv('URL')
BUZZER_PIN = 18
MOTOR_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(MOTOR_PIN, GPIO.OUT)

# Set up PWM
pwm = GPIO.PWM(MOTOR_PIN, 1000)  # 1000 Hz frequency
pwm.start(0)  # Start with 0% duty cycle

# Create a camera streamer
streamer = PiCameraStreamer()
print('Camera streamer created')
# Start the camera streamer
streamer.start()
print('Camera streamer started')

while(1):
    res = requests.get(URL + 'train/1')
    if res.status_code == 200:
        data = res.json()
        if data['status'] != 'STOP':
            speed = int(data['status'])

            if speed < 0:
                speed = 0
            elif speed > 100:
                speed = 100

            GPIO.output(MOTOR_PIN, GPIO.HIGH)
            pwm.ChangeDutyCycle(50)
        elif data['status'] == 'STOP':
            GPIO.output(MOTOR_PIN, GPIO.LOW)
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            pwm.ChangeDutyCycle(0)
        else:
            print('Invalid status')

    else:
        print('Error getting train status')
        GPIO.output(MOTOR_PIN, GPIO.LOW)
        pwm.ChangeDutyCycle(0)
        streamer.stop()
    
    time.sleep(0.05)

