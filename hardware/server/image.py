import socket
import json
import threading
import base64
import time
import flask

SOCKET_HOST = '0.0.0.0'  # 모든 인터페이스에서 연결 허용

train1_image = ''
train2_image = ''

app = flask.Flask(__name__)

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def create_socket_and_bind(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((SOCKET_HOST, port))
    except OSError as e:
        print(f"Error binding to port {port}: {e}")
        return None
    return sock

def socket_receiver(port):
    TCPServerSocket = create_socket_and_bind(port)
    if not TCPServerSocket:
        return

    TCPServerSocket.listen(1)
    print(f"Listening on port {port}")

    while True:
        try:
            connection, address = TCPServerSocket.accept()
            print(f"Connected by {address} on port {port}")
            handle_connection(connection)
        except Exception as e:
            print(f"Error in socket_receiver on port {port}: {e}")

def handle_connection(connection):
    global train1_image, train2_image

    while True:
        try:
            length = recvall(connection, 64)
            if not length:
                break
            length = length.decode()
            data = recvall(connection, int(length))

            json_data = json.loads(data.decode())
            
            train_id = json_data.get('train_id')
            base64_image = json_data.get('image')

            if base64_image:
                if train_id == '1':
                    train1_image = base64_image
                elif train_id == '2':
                    train2_image = base64_image
                else:
                    print(f"Received data for unknown train ID: {train_id}")
            else: 
                print("Received JSON data without image")
        except Exception as e:
            print(f"Error handling connection: {e}")
            break
    
    connection.close()

def socket_sender(port):
    global train1_image, train2_image

    send_server = create_socket_and_bind(port)
    if not send_server:
        return

    send_server.listen(1)
    print(f"Sender listening on port {port}")

    while True:
        connection, address = send_server.accept()
        print(f"Sender connected by {address} on port {port}")
        
        try:
            while True:
                message = recvall(connection, 64)
                if not message:
                    break

                train_id = str(message.decode().rstrip())
                if train_id in ['1', '2']:
                    image = train1_image if train_id == '1' else train2_image
                    image_length = str(len(image)).encode().ljust(64)
                    connection.sendall(image_length)
                    connection.send(image.encode())
                else:
                    print(f"Invalid train ID: {train_id}")
        except Exception as e:
            print(f"Error in socket_sender on port {port}: {e}")
        finally:
            connection.close()

def make_train1_image():
    global train1_image

    while True:
        time.sleep(0.1)
        image = base64.b64decode(train1_image)
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
    
def make_train2_image():
    global train2_image

    while True:
        time.sleep(0.1)
        image = base64.b64decode(train2_image)
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

@app.route('/')
def index():
    return flask.render_template('view.html')

@app.route('/chat', methods=['GET'])
def chat():
    return flask.render_template('chat.html')

@app.route('/train1', methods=['GET'])
def get_train1_image_data():
    global train1_image
    return flask.Response(make_train1_image(), mimetype='multipart/x-mixed-replace; boundary=frame') if train1_image else "No image available"

@app.route('/train2', methods=['GET'])
def get_train2_image_data():
    global train2_image
    return flask.Response(make_train2_image(), mimetype='multipart/x-mixed-replace; boundary=frame') if train2_image else "No image available"

if __name__ == '__main__':
    print("Starting socket server...")
    threading.Thread(target=socket_receiver, args=(8999,), daemon=True).start()
    threading.Thread(target=socket_receiver, args=(9000,), daemon=True).start()
    threading.Thread(target=socket_sender, args=(8997,), daemon=True).start()
    threading.Thread(target=socket_sender, args=(8998,), daemon=True).start()
    app.run(host='0.0.0.0', port=5001, debug=False)