from flask import Flask, request, jsonify, Response, render_template, redirect
from dotenv import load_dotenv
import json
import queue

# Load environment variables
load_dotenv()

train1_stat = 0
train2_stat = 0

# Create a Flask app
app = Flask(__name__)

# Define a route for the root URL
@app.route('/')
def index():
    return render_template('index.html', train1=train1_stat, train2=train2_stat)

# Define a route for the /predict URL
@app.route('/train/<id>', methods=['GET', 'POST'])
def train(id):
    if request.method == 'POST':
        speed = request.form.get('speed')

        if speed is None:
            speed = request.json.get('speed')

        if id == '1':
            global train1_stat
            train1_stat = speed
            print(train1_stat)
            return 'OK'

        elif id == '2':
            global train2_stat
            train2_stat = speed
            print(train2_stat)
            return 'OK'

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
    
frame_queue = queue.Queue(maxsize=30)  # 최근 30개의 프레임만 유지

@app.route('/post_frame', methods=['POST'])
def post_frame():
    if 'frame' in request.files:
        frame = request.files['frame'].read()
        if frame_queue.full():
            frame_queue.get()  # 가장 오래된 프레임 제거
        frame_queue.put(frame)
        return "Frame received", 200
    return "No frame in request", 400

def gen_frames():
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/stream')
def stream():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    
# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
