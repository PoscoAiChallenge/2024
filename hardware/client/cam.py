import cv2
from picamera2 import Picamera2
import time
import threading
import queue
from flask import Flask, Response

# 카메라 초기화
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480), "format": "YUV420"},
    controls={"FrameDurationLimits": (20000, 20000)}  # 약 50 FPS
)
picam2.configure(config)
picam2.start()

app = Flask(__name__)

# 프레임 버퍼
frame_buffer = queue.Queue(maxsize=10)

def capture_frames():
    while True:
        frame = picam2.capture_array()
        if not frame_buffer.full():
            frame_buffer.put(frame)
        else:
            frame_buffer.get()  # 가장 오래된 프레임 제거
            frame_buffer.put(frame)

# 프레임 캡처 스레드 시작
capture_thread = threading.Thread(target=capture_frames, daemon=True)
capture_thread.start()

def generate_frames():
    prev_frame = None
    motion_threshold = 5000  # 조정 가능한 임계값

    while True:
        if frame_buffer.empty():
            time.sleep(0.001)
            continue

        frame = frame_buffer.get()
        
        # YUV420에서 BGR로 변환
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_I420)

        # 모션 감지 (필요한 경우)
        if prev_frame is not None:
            diff = cv2.absdiff(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY),
                               cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY))
            non_zero = cv2.countNonZero(diff)
            if non_zero <= motion_threshold:
                prev_frame = frame_bgr
                continue  # 모션이 감지되지 않으면 다음 프레임으로

        prev_frame = frame_bgr

        # JPEG 압축
        ret, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        print()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print('Starting camera server...')
    app.run(host='0.0.0.0', port=5000)