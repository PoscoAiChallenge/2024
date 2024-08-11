from flask import Flask, request, jsonify, Response, render_template, redirect
import socket
import json
import time
import threading
import base64

# train status
train1_stat = 0
train2_stat = 0

#images
train1_image = ''
train2_image = ''

#log data
log_data = []

# Create a Flask app
app = Flask(__name__)

# Socket configuration
SOCKET_HOST = ''  # Listen on all available interfaces
SOCKET_PORT = 9000
BUFFER_SIZE = 65536  # Adjust this based on your expected data size

def socket_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((SOCKET_HOST, SOCKET_PORT))
    print(f"Socket listening on port {SOCKET_PORT}")

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"Received data from {addr}")
            print(data)
            # Decode the received data
            json_data = json.loads(data.decode('utf-8'))
            
            # Extract train ID and base64 encoded image
            train_id = json_data.get('train_id')
            base64_image = json_data.get('image')
            
            if base64_image:
                image_data = base64.b64decode(base64_image)
                
                if train_id == 1:
                    global train1_image
                    train1_image = image_data
                elif train_id == 2:
                    global train2_image
                    train2_image = image_data
                else:
                    print(f"Received data for unknown train ID: {train_id}")
            else:
                print("Received JSON data without image")
                
        except json.JSONDecodeError:
            print("Received invalid JSON data")
        except Exception as e:
            print(f"Socket error: {e}")

def socket_sender():
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    socket.bind((SOCKET_HOST, SOCKET_PORT))
    
    while True:
        try:

            global train1_image
            global train2_image
            recv_data, addr = socket.recvfrom(BUFFER_SIZE)

            if b'1' in recv_data:
                socket.sendto(train1_image, (SOCKET_HOST, SOCKET_PORT))
            elif b'2' in recv_data:
                socket.sendto(train2_image, (SOCKET_HOST, SOCKET_PORT))
            else:
                print("Received invalid data")
        except Exception as e:
            print(f"Socket error: {e}")

# Start socket listener in a separate thread
socket_thread = threading.Thread(target=socket_listener, daemon=True)
socket_thread.start()
socket_sender_thread = threading.Thread(target=socket_sender, daemon=True)
socket_sender_thread.start()

@app.route('/')
def index():
    return render_template('index.html', train1=train1_stat, train2=train2_stat)

@app.route('/speed/<id>', methods=['GET', 'POST'])
def train(id):
    global train1_stat, train2_stat
    if request.method == 'POST':
        speed = request.form.get('speed')
        if speed is None:
            speed = request.json.get('speed')
            
        
        if id == '1':
            train1_stat = speed
        elif id == '2':
            train2_stat = speed
        else:
            return jsonify({'error': 'Invalid train ID'}), 400
        return redirect('/')

    elif request.method == 'GET':
        if id == '1':
            return jsonify({'status': train1_stat})
        elif id == '2':
            return jsonify({'status': train2_stat})
        else:
            return jsonify({'error': 'Invalid train ID'}), 400
    else:
        return jsonify({'error': 'Invalid request method'}), 405
    
@app.route('/image/<id>', methods=['GET'])
def image(id):

    global train1_image
    global train2_image

    if request.method == 'GET':
        if id == '1':
            return train1_image
        elif id == '2':
            return train2_image
        else:
            return jsonify({'error': 'Invalid train ID'}), 400
    else:
        return jsonify({'error': 'Invalid request method'}), 405

    
    
@app.route('/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        data = request.json
        data = time.strftime('%Y-%m-%d %H:%M:%S') + ' - ' + str(data)
        log_data.append(data)
        return jsonify({'status': 'success'})
    elif request.method == 'GET':
        return render_template('log.html', logs=log_data)
    else:
        return jsonify({'error': 'Invalid request method'}), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)