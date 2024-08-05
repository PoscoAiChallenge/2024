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
        self.camera = None
        self.is_running = False
        self.init_camera()

    def init_camera(self, max_retries=3):
        for attempt in range(max_retries):
            try:
                self.camera = Picamera2()
                self.camera.configure(self.camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
                print(f"Camera initialized successfully on attempt {attempt + 1}")
                return
            except Exception as e:
                print(f"Failed to initialize camera on attempt {attempt + 1}: {e}")
                if self.camera:
                    self.camera.close()
                time.sleep(2)  # Wait before retrying
        
        raise RuntimeError("Failed to initialize camera after multiple attempts")

    def start(self):
        if not self.camera:
            raise RuntimeError("Camera not initialized")
        self.camera.start()
        self.is_running = True
        Thread(target=self.run_flask).start()

    def stop(self):
        self.is_running = False
        if self.camera:
            self.camera.stop()
            self.camera.close()

    def generate_frames(self):
        while self.is_running:
            if not self.camera:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + b'\r\n')
                continue
            try:
                frame = self.camera.capture_array()
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                print(f"Error capturing frame: {e}")
                time.sleep(0.1)

    def run_flask(self):
        app.run(host='0.0.0.0', port=5000, threaded=True)

@app.route('/')
def video_feed():
    return Response(streamer.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

streamer = PiCameraStreamer()

if __name__ == '__main__':
    streamer.start()