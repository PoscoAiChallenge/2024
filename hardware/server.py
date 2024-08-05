from flask import Flask, request, jsonify, Response, render_template, redirect
import cv2
import numpy as np
from dotenv import load_dotenv
import json
import threading

# Load environment variables
load_dotenv()

train1_stat = 'STOP'
train2_stat = 'STOP'

global_frame1 = None
global_frame2 = None

# Create a Flask app
app = Flask(__name__)
lock = threading.Lock()

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
    global global_frame1, global_frame2
    while True:
        with lock:
            if frame_source == 1:
                frame = global_frame1
            else:
                frame = global_frame2
        
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        else:
            # If no frame is available, send a blank frame
            blank_frame = np.zeros((600, 600, 3), np.uint8)
            ret, buffer = cv2.imencode('.jpg', blank_frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/train/video/<id>', methods=['GET', 'POST'])
def train_video(id):
    global global_frame1, global_frame2
    
    if request.method == 'POST':
        if id not in ['1', '2']:
            return json.dumps({'error': 'Invalid train ID'}), 400
        
        img_data = request.data
        if not img_data:
            return json.dumps({'error': 'No image data received'}), 400
        
        print(f"Received data length for train {id}: {len(img_data)}")
        
        try:
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return json.dumps({'error': 'Failed to decode image'}), 400
            
            with lock:
                if id == '1':
                    global_frame1 = frame
                else:
                    global_frame2 = frame
            
            return json.dumps({'status': 'OK'})
        
        except Exception as e:
            print(f"Error processing image for train {id}: {str(e)}")
            return json.dumps({'error': str(e)}), 500
        
    elif request.method == 'GET':
        if id not in ['1', '2']:
            return json.dumps({'error': 'Invalid train ID'}), 400
        
        frame_source = 1 if id == '1' else 2
        
        return Response(generate_frames(frame_source),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    else:
        return json.dumps({'error': 'Invalid request method'}), 405
    
# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
