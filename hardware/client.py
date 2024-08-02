import os
import requests
import json
import RPi.GPIO as GPIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up GPIO
URL = os.getenv('URL')
BUZZER_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Set up PWM
pwm = GPIO.PWM(BUZZER_PIN, 1000)  # 1000 Hz frequency
pwm.start(0)  # Start with 0% duty cycle

