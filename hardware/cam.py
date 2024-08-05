import io
import time
import requests
from threading import Thread
from picamera2 import Picamera2
import cv2
from flask import Flask, Response

app = Flask(__name__)

class PiCameraStreamer:
    def __init__(self):
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
        self.is_running = False

    def start(self):
        self.camera.start()
        self.is_running = True
        Thread(target=self.run_flask).start()

    def stop(self):
        self.is_running = False
        self.camera.stop()

    def generate_frames(self):
        while self.is_running:
            frame = self.camera.capture_array()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def run_flask(self):
        app.run(host='0.0.0.0', port=5000, threaded=True)

@app.route('/')
def video_feed():
    return Response(streamer.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

streamer = PiCameraStreamer()

if __name__ == '__main__':
    streamer.start()