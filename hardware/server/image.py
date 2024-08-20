import socket
import json
import requests
import threading
import base64
import flask

SOCKET_HOST = ''

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

def socket_receiver1():

    TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPServerSocket.bind((SOCKET_HOST, 8999))
    TCPServerSocket.listen(1)

    connection, address = TCPServerSocket.accept()

    global train1_image, train2_image

    while True:
        try:
            length = recvall(connection, 64)
            length = length.decode()
            data = recvall(connection, int(length))

            # Decode the received data
            json_data = json.loads(data.decode())
                
            # Extract train ID and base64 encoded image
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
                requests.post()
                print("Received JSON data without image")
        except:
            print("Error receiving data")
            connection.close()

def socket_receiver2():

    TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPServerSocket.bind((SOCKET_HOST, 9000))
    TCPServerSocket.listen(1)

    connection, address = TCPServerSocket.accept()

    global train1_image, train2_image

    while True:
        try:
            length = recvall(connection, 64)
            length = length.decode()
            data = recvall(connection, int(length))

            # Decode the received data
            json_data = json.loads(data.decode())
                
            # Extract train ID and base64 encoded image
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
                requests.post()
                print("Received JSON data without image")
        except:
            print("Error receiving data")
            connection.close()


def socket_sender():
    global train1_image, train2_image

    send_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    send_server.bind((SOCKET_HOST, 8997))
    send_server.listen(1)

    connection, address = send_server.accept()

    while True:
        message = recvall(connection, 64)

        if not message:
            continue

        if str(message.decode().rstrip()) == '1':
            train1_image_length = str(len(train1_image)).encode().ljust(64)
            connection.sendall(train1_image_length)
            connection.send(train1_image.encode())

        elif str(message.decode().rstrip()) == '2':
            train2_image_length = str(len(train2_image)).encode().ljust(64)
            connection.sendall(train2_image_length)
            connection.send(train2_image.encode())
        else:
            print("Invalid train ID")

        if connection.fileno() == -1:
            connection, address = send_server.accept()

def socket_sender2():
    global train1_image, train2_image

    send2_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    send2_server.bind((SOCKET_HOST, 8998))
    send2_server.listen(1)

    connection, address = send2_server.accept()

    while True:
        message = recvall(connection, 64)

        if not message:
            continue

        if str(message.decode().rstrip()) == '1':
            train1_image_length = str(len(train1_image)).encode().ljust(64)
            connection.sendall(train1_image_length)
            connection.send(train1_image.encode())

        elif str(message.decode().rstrip()) == '2':
            train2_image_length = str(len(train2_image)).encode().ljust(64)
            connection.sendall(train2_image_length)
            connection.send(train2_image.encode())
        else:
            print("Invalid train ID")

        if connection.fileno() == -1:
            connection, address = send2_server.accept()

def make_image(base64_image):
    image = base64.b64decode(base64_image)
    yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

@app.route('/')
def index():
    return "Server is running"

@app.route('/train1', methods=['GET'])
def get_train1_image():
    global train1_image

    if train1_image:
        return flask.Response(make_image(train1_image), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "No image available"
    
@app.route('/train2', methods=['GET'])
def get_train2_image():
    global train2_image

    if train2_image:
        return flask.Response(make_image(train2_image), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "No image available"

if __name__ == '__main__':
    print("Starting socket server...")
    threading.Thread(target=socket_receiver1, daemon=True).start()
    threading.Thread(target=socket_receiver2, daemon=True).start()
    threading.Thread(target=socket_sender, daemon=True).start()
    threading.Thread(target=socket_sender2, daemon=True).start()
    app.run(host='0.0.0.0', port=5001, debug=True)
