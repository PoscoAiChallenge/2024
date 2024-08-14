import socket
import json
import base64
from dotenv import load_dotenv
import requests
import os

load_dotenv()
URL = os.getenv('URL')
NUM_TRAIN = os.getenv('TRAIN')

while True:
    res = requests.get(URL + '/speed/' + NUM_TRAIN)
    print(res.status_code)