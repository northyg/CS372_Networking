# Giselle Northy
# CS 372 Fall 2020
# Project 4
# 
# File: client.py
# Version: Python3.7
#
# Sources:
# [1]https://docs.python.org/3.4/howto/sockets.html
# [2]https://www.geeksforgeeks.org/random-numbers-in-python
# [3]https://www.tutorialspoint.com/python/python_multithreading.htm
# [4]https://pythonbasics.org/if-statements/


import socket
import sys

# Create TCP/IP socket

class MyClient:

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.MSGLEN = 4 # set msglength to 4, the length of the header

    # Method set up connection with host        
    def connect(self, host, port) :
        self.sock.connect((host, port))

    # Method sends message and shows error if connect broke
    def mysend(self, msg):
        totalsent = 0
        length = str((len(msg) + 4)).zfill(4) # pads with leading 0's
        msg = length + msg
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:].encode())
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    # Method receives message, checks the length to receive correct amount
    def myreceive(self):
        chunks = []
        newchunks = []
        bytes_recd = 0
        while bytes_recd < self.MSGLEN:
            chunk = self.sock.recv(min(self.MSGLEN - bytes_recd, 2048))
            if chunk == b'': # if received 0 bytes then connection broken
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        length = int(b''.join(chunks))
        while bytes_recd < length:
            newchunk = self.sock.recv(min(length - bytes_recd, 2048))
            if newchunk == b'':
                raise RuntimeError("socket connection broken")
            newchunks.append(newchunk)
            bytes_recd = bytes_recd + len(newchunk)
        return b''.join(newchunks)



# Begin Constructor 

# Starts the connection on the following host and port
clientConnection = MyClient()
clientConnection.connect('localhost', 10000)
print("Press any key to get started and connect to server")
while True:
    message = input("Send a message: ")
    clientConnection.mysend(message)
    if (message == '/q'): # close the connection
        clientConnection.sock.close()
        break
    msg = clientConnection.myreceive().decode()
    print("Got message: " + msg)    
