from flask import Flask, request, jsonify, Response, render_template, redirect
import socket
import json
import time
import requests
import threading

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

def socket_receiver():
    global train1_image, train2_image

    while True:
        try:
            length = recvall(connection, 64)
            length = length.decode()
            data = recvall(connection, int(length))

            print("message received")

            # Decode the received data
            json_data = json.loads(data.decode())
                
            # Extract train ID and base64 encoded image
            train_id = json_data.get('train_id')
            base64_image = json_data.get('image')

            if base64_image:
                    
                if train_id == '1':
                    train1_image = base64_image

                elif train_id == '2':
                    train2_image = base64_image
                        
                else:
                    print(f"Received data for unknown train ID: {train_id}")
            else:
                requests.post()
                print("Received JSON data without image")
        except:
            print("Error receiving data")
            connection.close()

def socket_sender():
    global train1_image, train2_image

    send_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    send_server.bind((SOCKET_HOST, 8999))
    send_server.listen(1)

    connection, address = send_server.accept()

    while True:
        message = recvall(connection, 64)
        print(message.decode())

        if message.decode() == '1':
            train1_image_length = str(len(train1_image))
            send_server.send(train1_image_length.encode(), address)
            send_server.send(train1_image.encode(), address)

        elif message.decode() == '2':
            train2_image_length = str(len(train2_image))
            send_server.send(train2_image_length.encode(), address)
            send_server.send(train2_image.encode(), address)
        else:
            print("Invalid train ID")

def main():
    receiver_thread = threading.Thread(target=socket_receiver, daemon=True)
    sender_thread = threading.Thread(target=socket_sender, daemon=True)

    receiver_thread.start()
    sender_thread.start()

    receiver_thread.join()
    sender_thread.join()

if __name__ == '__main__':
    main()