from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import time
import threading

app = Flask(__name__)

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (320, 240)}))  # Reduced size
camera.start()

# Global variable to store the latest frame
latest_frame = None
frame_lock = threading.Lock()

def capture_frames():
    global latest_frame
    while True:
        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])  # Reduced quality
        with frame_lock:
            latest_frame = buffer.tobytes()
        time.sleep(0.1)  # Capture at 10 fps

def generate_frames():
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
        time.sleep(0.3)  # Stream at 10 fps

@app.route('/')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print('Starting camera server...')
    threading.Thread(target=capture_frames, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, threaded=True)