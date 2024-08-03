import io
import time
import picamera
import requests
from threading import Thread

class PiCameraStreamer:
    def __init__(self, server_url):
        self.server_url = server_url
        self.stream = io.BytesIO()
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1920, 1080)
        self.camera.framerate = 30
        self.is_running = False

    def capture_frames(self):
        for _ in self.camera.capture_continuous(self.stream, format='jpeg', use_video_port=True):
            if not self.is_running:
                break
            self.stream.seek(0)
            yield self.stream.read()
            self.stream.seek(0)
            self.stream.truncate()

    def send_frames(self):
        for frame in self.capture_frames():
            try:
                response = requests.post(
                    self.server_url, 
                    data=frame, 
                    headers={'Content-Type': 'image/jpeg'}
                )
                print(f"Frame sent. Status code: {response.status_code}")
            except requests.RequestException as e:
                print(f"Error sending frame: {e}")
            time.sleep(1/60)  # 약 30 FPS로 제한

    def start(self):
        self.is_running = True
        Thread(target=self.send_frames).start()

    def stop(self):
        self.is_running = False
        self.camera.close()