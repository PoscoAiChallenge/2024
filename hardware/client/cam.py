from picamera2 import Picamera2
import requests
import cv2
from time import sleep

def main():
    camera = Picamera2()
    camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    camera.start()

    try:
        while True:
            frame = camera.capture_array()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            try:
                res = requests.post('http://192.168.124.101:5000/post_frame', 
                                    files={'frame': frame},
                                    timeout=5)  # 5초 타임아웃 설정
                if res.status_code != 200:
                    print(f'Error sending frame: HTTP {res.status_code}')
                    # 여기서 break하지 않고 계속 진행
            except requests.RequestException as e:
                print(f'Error sending frame: {e}')
                # 네트워크 오류 발생 시 잠시 대기 후 재시도
                sleep(1)
            
            sleep(0.1)  # 프레임 전송 간격, 필요에 따라 조정
    
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        camera.stop()
        print("Camera stopped")

if __name__ == "__main__":
    main()