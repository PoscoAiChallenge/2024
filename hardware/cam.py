import io
import time
import requests
from threading import Thread
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

class PiCameraStreamer:
    def __init__(self, server_url):
        self.server_url = server_url
        self.stream = io.BytesIO()
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_still_configuration(main={"size": (600, 600)}))
        self.encoder = JpegEncoder()
        self.output = FileOutput(self.stream)
        self.is_running = False

    def capture_frames(self):
        self.camera.start()
        request_config = self.camera.create_jpeg_configuration()  # JPEG 설정 생성
        while self.is_running:
            self.stream.seek(0)
            self.stream.truncate()
            self.camera.capture_file(self.output, wait=True, request=request_config)  # 설정 적용
            yield self.stream.getvalue()

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
            time.sleep(1/30)  # 약 30 FPS로 제한

    def start(self):
        self.is_running = True
        Thread(target=self.send_frames).start()

    def stop(self):
        self.is_running = False
        self.camera.stop()
        self.camera.close()

if __name__ == "__main__":
    streamer = PiCameraStreamer("http://your-server-url/endpoint")
    try:
        streamer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping streamer...")
        streamer.stop()