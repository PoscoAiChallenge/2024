from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import gpiozero
import requests
import threading
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

SERVER_IP = os.getenv('SERVER_IP')
URL = os.getenv('URL')
NUM_TRAIN = os.getenv('TRAIN')

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()

def generate_frames():
    while True:
        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
def motor_control():
    motor = gpiozero.LED(18)
    motor_status = 0
    while True:
        res = requests.get(URL + '/speed/' + NUM_TRAIN)
        number = str(res.json()['status'])

        if number == '0':
            motor.off()
            
            if motor_status == 1:
                motor_status = 0
                requests.post(URL + '/log', json={'status': 'Motor' + NUM_TRAIN + ' is off'})
            else:
                continue
                
        elif number == '1':
            motor.on()

            if motor_status == 0:
                motor_status = 1
                requests.post(URL + '/log', json={'status': 'Motor' + NUM_TRAIN + ' is on'})
            else:
                continue
        else:
            print('Invalid speed value:', number)
            motor.off()
            motor_status = 0
            requests.post(URL + '/log', json={'status': 'Invalid speed value: ' + str(number)})



@app.route('/')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print('Starting camera server...')
    threading.Thread(target=motor_control).start()
    app.run(host='0.0.0.0', port=5000)