import cv2
from flask import Flask, Response
from threading import Thread

app = Flask(__name__)

class PiCameraStreamer:
    def __init__(self):
        self.camera = None
        self.is_running = False

    def init_camera(self):
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            raise RuntimeError("Failed to open camera")

    def start(self):
        self.init_camera()
        self.is_running = True
        Thread(target=self.run_flask).start()

    def stop(self):
        self.is_running = False
        if self.camera:
            self.camera.release()

    def generate_frames(self):
        while self.is_running:
            success, frame = self.camera.read()
            if not success:
                print("Failed to read frame")
                break
            else:
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