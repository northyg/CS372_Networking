# Giselle Northy
# CS 372 Fall 2020
# Project 1
# Part 1 Use a socket to GET a file
# File: connect_socket_proj1_part_1.py
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
server = "gaia.cs.umass.edu"

# connect to server
s.connect((server, 80))

#send GET request to server....
get_request = "GET /wireshark-labs/INTRO-wireshark-file1.html HTTP/1.1\r\nHost:gaia.cs.umass.edu\r\n\r\n"
print("Request: " + get_request)
s.send(get_request.encode())


# get message from server
msg = s.recv(1024)
print("[RECV] - length: " + str(len(msg)))
print(msg.decode())


