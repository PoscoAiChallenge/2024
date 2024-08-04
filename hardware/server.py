from flask import Flask, request, jsonify, Response, render_template, redirect
import cv2
import numpy as np
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

train1_stat = 'STOP'
train2_stat = 'STOP'

global_frame1 = None
global_frame2 = None

# Create a Flask app
app = Flask(__name__)

# Define a route for the root URL
@app.route('/')
def index():
    return render_template('index.html')

# Define a route for the /predict URL
@app.route('/train/<id>', methods=['GET', 'POST'])
def train(id):
    if request.method == 'POST':
        if id == '1':
            global train1_stat
            train1_stat = speed = request.form.get('speed')
            return redirect('/')
        elif id == '2':
            global train2_stat
            train2_stat = speed = request.form.get('speed')
            return redirect('/')
        else:
            return json.dumps({'error': 'Invalid train ID'})

    elif request.method == 'GET':
        if id == '1':
            return jsonify({'status': train1_stat})
        elif id == '2':
            return jsonify({'status': train2_stat})
        else:
            return json.dumps({'error': 'Invalid train ID'}), 400
    else:
        return json.dumps({'error': 'Invalid request method'}), 405
    
def generate_frames(frame_source):
    while True:
        if frame_source is not None:
            ret, buffer = cv2.imencode('.jpg', frame_source)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/train/video/<id>', methods=['GET','POST'])
def train_video(id):
    if request.method == 'POST':
        if id == '1':
            global global_frame1
            img_data = request.data
            nparr = np.frombuffer(img_data, np.uint8)
            global_frame1 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return json.dumps({'status': 'OK'})
        
        elif id == '2':
            global global_frame2
            img_data = request.data
            nparr = np.frombuffer(img_data, np.uint8)
            global_frame2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            print(request.data)
            return json.dumps({'status': 'OK'})
        
        else:
            return json.dumps({'error': 'Invalid train ID'}), 400
        
    elif request.method == 'GET':
        if id == '1':
            return Response(generate_frames(global_frame1), mimetype='multipart/x-mixed-replace; boundary=frame')
        elif id == '2':
            return Response(generate_frames(global_frame2), mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return json.dumps({'error': 'Invalid train ID'}), 400

    else:
        return json.dumps({'error': 'Invalid request method'}), 405
    
# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
