from flask import Flask, Response
import cv2

app = Flask(__name__)

camera = cv2.VideoCapture(-1)
camera.set(3, 400)
camera.set(4, 400)

def generate_frames():
    while True:
        _, frame = camera.read()
        _, frame = cv2.imencode('.jpg', frame)
        frame = frame.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print('Starting camera server...')
    app.run(host='0.0.0.0', port=5000)
