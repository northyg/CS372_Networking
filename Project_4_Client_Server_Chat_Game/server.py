# Giselle Northy
# CS 372 Fall 2020
# Project 4
# 
# File: server.py
# Version: Python3.7
#
# Sources:
# [1]https://docs.python.org/3.4/howto/sockets.html
# [2]https://www.geeksforgeeks.org/random-numbers-in-python
# [3]https://www.tutorialspoint.com/python/python_multithreading.htm
# [4]https://pythonbasics.org/if-statements/

# Server needs to bind and then listen

import socket
import random

class MySocket:

    def __init__(self, sock=None):
        self.MSGLEN = 4
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    # Method binds the address and port to the server 
    def bind(self, address, port):
        server_address = (address, port)
        #print ('starting up on ' + str(server_address[0]) + ' ' + str(server_address[1]))
        self.sock.bind(server_address)

    # Method connects to socket
    def connect(self, host, port):
        self.sock.connect((host, port))

    # Method sends message and adds a header indicating length of msg
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
    
    # Method listens on the socket 
    def listen(self):
        self.sock.listen(1)


    # EXTRA CREDIT
    # Method sets the game message, i.e. if it's 0, say Rock!
    def getRPSstring(self, numberIn):
        stringOut = ''
        if (numberIn == 0):
            stringOut = ("Rock!")
        elif (numberIn == 1):
            stringOut = ("Paper!")
        elif (numberIn == 2):
            stringOut = ("Scissors!")
        return stringOut


    # Method generates random number between 0 - 2
    def randomgen(self):
        self.randomnumber = random.choice([0, 1, 2])
        self.numbertoprint = self.getRPSstring(self.randomnumber)
        
        print("Served rolled "  + str(self.randomnumber))    

    # Method decides win conditions
    #   rock beats scissor 0 > 2
    #   scissor beats paper 2 > 1
    #   paper beats rock 1 > 0
    #   rock ties rock 0 = 0
    #   scissor ties scissor 2 = 2
    #   paper ties paper 1 = 1
    #   server random 0-2
    #   0 = rock
    #   1 = paper
    #   2 = scissor
    #   if not those then try again
    #   quit /q close socket        
    def rockpaperscissor(self, message):
    
    # draw condition
        retval = ''
        if (message == '/q'):
            self.sock.close()
            retval = 'quit'
        elif (str(self.randomnumber) == message):
            retval = "It's a draw!"
            self.randomgen()
              
    # server wins
        elif (self.randomnumber == 0 and message == '2' or self.randomnumber == 2 and message == '1' or self.randomnumber == 1 and message == '0'):
            retval = ("Server wins with " + self.numbertoprint)
            self.randomgen()

    # client wins
        elif (self.randomnumber == 2 and message == '0' or self.randomnumber == 1 and message == '2' or self.randomnumber == 0 and message == '1'):
            retval = ("Client wins with " + self.getRPSstring(int(message)))
            self.randomgen()

        else:
            retval = ("Wrong input, try again!")
        return retval
    
# Constructor runs the init function

# Sets the host, port variables
localhost = 'localhost'
port = 10000
chatConnection = MySocket()
chatConnection.bind(localhost, port)
print("Server listening on: "+ localhost + " on port: " + str(port))

chatConnection.listen()

#Prints the welcome message and menu
welcomemsg = ("Welcome to Rock Paper Scissors server mashup!" +
              "\nRock beats Scissor 0 > 2\nScissor beats Paper 2 > 1" +
              "\nPaper beats Rock 1 > 0\nSame equals draw" +
              "\nPress:\n0 for Rock\n1 for Paper\n2 for Scissors\n/q to Quit")              
print ( 'waiting for connection')
connection, client_address = chatConnection.sock.accept()
clientConnection = MySocket(connection)

# take first message to start connection, disregard for game
message = clientConnection.myreceive().decode() 
clientConnection.randomgen()

# send out welcome message menu
clientConnection.mysend(welcomemsg)

# Conditinues 'game' until client sends /q
while True:
        message = clientConnection.myreceive().decode()
        print("Got message: " + message)
        result = clientConnection.rockpaperscissor(message)
        if (result == 'quit'): #close connection if /q
            break
        clientConnection.mysend(result) 
        


