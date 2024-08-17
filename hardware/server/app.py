from flask import Flask, request, jsonify, Response, render_template, redirect
from socket import *
import json
import time
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

def recvall(sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

def socket_sender():
    send_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    send_server.bind((SOCKET_HOST, 9000))
    send_server.listen(1)

    connection, address = send_server.accept()

    while True:
        message = recvall(connection, 64)

        if message.decode() == '1':
            send_server.send(train1_image.encode(), address)
        elif message.decode() == '2':
            send_server.send(train2_image.encode(), address)
        else:
            print("Invalid train ID")

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