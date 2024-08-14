import socket
import json
import base64
from dotenv import load_dotenv
import os

load_dotenv()
URL = os.getenv('URL')
NUM_TRAIN = os.getenv('TRAIN')

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind((URL, 9000))
