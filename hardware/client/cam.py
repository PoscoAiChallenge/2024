from picamera2 import Picamera2
import requests
import cv2

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()

while True:
        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        requests.post('http://192.168.124.101:5000/post_frame', files={'frame': frame}, timeout=0.1)
