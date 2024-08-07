from flask import Flask, request, jsonify, Response, render_template, redirect
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

train1_stat = 'STOP'
train2_stat = 'STOP'

# Create a Flask app
app = Flask(__name__)

# Define a route for the root URL
@app.route('/')
def index():
    return render_template('index.html', train1_stat=train1_stat, train2_stat=train2_stat)

# Define a route for the /predict URL
@app.route('/train/<id>', methods=['GET', 'POST'])
def train(id):
    if request.method == 'POST':
        if id == '1':
            global train1_stat
            train1_stat = speed = request.form.get('speed')

        elif id == '2':
            global train2_stat
            train2_stat = speed = request.form.get('speed')
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
    
# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
