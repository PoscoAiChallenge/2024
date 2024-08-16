from flask import Flask, request, jsonify, Response, render_template, redirect
from socket import *
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
SOCKET_HOST = ""  # Listen on all available interfaces
SOCKET_PORT = 9000
BUFFER_SIZE = 2048 

def socket_listener():
    UDPServerSocket = socket(family=AF_INET, type=SOCK_DGRAM)
    UDPServerSocket.bind((SOCKET_HOST, SOCKET_PORT))

    while True:
        try:
            recv_data = UDPServerSocket.recvfrom(BUFFER_SIZE)
            data = recv_data[0]

            # Decode the received data
            json_data = json.loads(data.decode())
            
            # Extract train ID and base64 encoded image
            train_id = json_data.get('train_id')
            base64_image = json_data.get('image')
            
            if base64_image:
                image_data = base64.b64decode(base64_image)
                
                if train_id == '1':
                    global train1_image
                    train1_image = image_data
                    
                    print(train1_image)

                elif train_id == '2':
                    global train2_image
                    train2_image = image_data

                    print(train2_image)
                    
                else:
                    print(f"Received data for unknown train ID: {train_id}")
            else:
                print("Received JSON data without image")
                
        except json.JSONDecodeError:
            print("Received invalid JSON data")
        except Exception as e:
            print(f"Socket error: {e}")


# Start socket listener in a separate thread
socket_thread = threading.Thread(target=socket_listener, daemon=True)
socket_thread.start()

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