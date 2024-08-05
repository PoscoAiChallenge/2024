import io
import time
import requests
from threading import Thread
from picamera2 import Picamera2

class PiCameraStreamer:
    def __init__(self, server_url):
        self.server_url = server_url
        self.camera = Picamera2()
        self.still_config = self.camera.create_still_configuration(main={"size": (600, 600)})
        self.camera.configure(self.still_config)
        self.is_running = False

    def capture_and_send_frames(self):
        self.camera.start()
        while self.is_running:
            frame = self.camera.capture_array()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            try:
                response = requests.post(
                    self.server_url, 
                    data=stream.getvalue(), 
                    headers={'Content-Type': 'image/jpeg'}
                )
                print(f"Frame sent. Status code: {response.status_code}")
            except requests.RequestException as e:
                print(f"Error sending frame: {e}")
            time.sleep(1/30)  # 약 30 FPS로 제한

    def start(self):
        self.is_running = True
        Thread(target=self.capture_and_send_frames).start()

    def stop(self):
        self.is_running = False
        self.camera.stop()
        self.camera.close()