from flask import Flask, request, jsonify, render_template, redirect
from socket import *     
import time

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

@app.route('/')
def index():
    return "server is running"

@app.route('/speed/<id>', methods=['GET', 'POST'])
def train(id):
    global train1_stat, train2_stat
    if request.method == 'POST':
        try:
            speed = str(request.json.get('speed'))
        except:
            speed = str(request.form.get('speed'))
            
        if speed is None:
            print('Speed is None')
            speed = str(request.json.get('speed'))
            
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
    app.run(host='0.0.0.0', port=5000)