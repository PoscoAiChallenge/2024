import os
import requests
import time
import RPi.GPIO as GPIO
from dotenv import load_dotenv
import subprocess
import signal

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

process = subprocess.Popen(['python3', 'cam.py'])

try:
    while True:
        try:
            res = requests.get(URL + 'train/1')
            if res.status_code == 200:
                data = res.json()
                if data['status'] != 'STOP':
                    speed = int(data['status'])

                    speed = max(0, min(speed, 100))  # Clamp speed between 0 and 100

                    GPIO.output(MOTOR_PIN, GPIO.HIGH)
                    pwm.ChangeDutyCycle(speed)
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
        
        except requests.RequestException as e:
            print(f'Request error: {e}')
            GPIO.output(MOTOR_PIN, GPIO.LOW)
            pwm.ChangeDutyCycle(0)
        
        time.sleep(0.05)

except KeyboardInterrupt:
    process.send_signal(signal.SIGINT)
    process.wait()
    print("Stopping...")
finally:
    GPIO.cleanup()
    print("Cleanup done")