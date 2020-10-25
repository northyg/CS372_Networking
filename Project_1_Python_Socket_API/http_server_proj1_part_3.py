# Giselle Northy
# CS 372 Fall 2020
# Project 1
# Part 3 The world’s simplest HTTP server
# File: http_server_proj1_part_3.py
# Version: Python3.7
#
# Sources:
# A. Computer Networking - A Top-Down Approach, Kurose and Ross, 7th Edition
# B. https://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html#sec5.1.2
# C. Sockets Tutorial with Python 3 part 2 - buffering and streaming data
#    https://www.youtube.com/watch?v=8A4dqoGL62E
# D. Sockets Tutorial with Python 3 part 1 - sending and receiving data
#    https://www.youtube.com/watch?v=Lbfe3-v7yE0


import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = '127.0.0.1'
port = 1025

# starting server
s.bind((ip, port))
s.listen(1)

# data to be sent to client
data =  "HTTP/1.1 200 OK\r\n"\
       "Content-Type: text/html; charset=UTF-8\r\n\r\n"\
       "<html>Congratulations!  You've downloaded the first Wireshark lab file!</html>\r\n"

print("Connected by ('" + ip + "', " + str(port) + ")\n")

# loop that accepts requests
while True:
    websocket, address = s.accept()
    sentence = websocket.recv(1024)
    if(len(sentence) <= 0):
        continue
    print("Received: ", end='')
    print(sentence)
    print("\nSending>>>>>>>>")
    print(data)
    websocket.send(data.encode())
    websocket.close()
    print("<<<<<<<<<<<<<<<")
