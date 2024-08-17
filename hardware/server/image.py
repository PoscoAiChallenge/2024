from flask import Flask, request, jsonify, Response, render_template, redirect
import socket
import json
import time
import base64

SOCKET_HOST = ''

train1_image = ''
train2_image = ''

def recvall(sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf


TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPServerSocket.bind((SOCKET_HOST, 9000))
TCPServerSocket.listen(1)

connection, address = TCPServerSocket.accept()

while True:
    try:
        length = recvall(connection, 64)
        length = length.decode()
        data = recvall(connection, int(length))

        # Decode the received data
        json_data = json.loads(data.decode())
            
        # Extract train ID and base64 encoded image
        train_id = json_data.get('train_id')
        base64_image = json_data.get('image')
            
        print(f"Received data for train ID: {train_id}")
        print(f"Received image length: {len(base64_image)}")

        if base64_image:
                
            if train_id == '1':
                train1_image = base64_image

            elif train_id == '2':
                train2_image = base64_image
                    
            else:
                print(f"Received data for unknown train ID: {train_id}")
        else:
            print("Received JSON data without image")
    except:
        print("Error receiving data")
        connection.close()