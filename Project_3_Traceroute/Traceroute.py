# Giselle Northy
# CS372
# Project 3
# 11/30/2020
#
# Sources:
# [1] https://erg.abdn.ac.uk/users/gorry/course/inet-pages/icmp-code.html
# [2] https://stackoverflow.com/questions/18058389/how-to-switch-between-python-2-7-to-python-3-from-command-line
# [3] https://stackoverflow.com/questions/1708835/python-socket-receive-incoming-packets-always-have-a-different-size
# [4] https://medium.com/@NickKaramoff/tcp-packets-from-scratch-in-python-3a63f0cd59fe
# [5] https://docs.python.org/3/library/socket.html?highlight=socket#module-socket
# [6] https://stackoverflow.com/questions/34614893/how-is-an-icmp-packet-constructed-in-python
# [7] https://stackoverflow.com/questions/19897209/troubleshooting-typeerror-ord-expected-string-of-length-1-but-int-found
# [8] https://docs.python.org/3/library/struct.html#format-characters
# [9] https://datatracker.ietf.org/doc/rfc792/?include_text=1
# [10] https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol#Control_messages
# [11] https://www.programcreek.com/python/example/86/struct.unpack

from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 40
TIMEOUT  = 2.0
TRIES    = 2

def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2

    count = 0
    while (count < countTo):
        thisVal = string[count+1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if (countTo < len(string)):
        csum = csum + string[len(string) - 1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def build_packet(data_size):
        # First, make the header of the packet, then append the checksum to the header,
        # then finally append the data
        # ICMP Header
        
        # Build the header
        theChecksum = 0
        pid = os.getpid() & 0xFFFF
        header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, theChecksum, pid, 1)

        # Make the data packet using time()
        data = struct.pack("d", time.time())

        # Generate the checksum
        theChecksum = checksum(header + data)

        # Insert checksum into header
        header = header[:2] + struct.pack('!H', theChecksum) + header[4:]

        # Don’t send the packet yet, just return the final packet in this function.
        # So the function ending should look like this
        # Note: padding = bytes(data_size)
        padding = bytes(data_size)
        packet = header + data + padding
        return packet

def get_route(hostname,data_size):
    timeLeft = TIMEOUT
    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):

                        destAddr = gethostbyname(hostname)

                        # SOCK_RAW is a powerful socket type. For more details:   http://sock-raw.org/papers/sock_raw
                        #Fill in start

                        # Make a raw socket named mySocket

                        mySocket = socket(AF_INET, SOCK_RAW, getprotobyname('icmp'))
                        mySocket.bind(("", 14002));

                        #Fill in end

                        # setsockopt method is used to set the time-to-live field.
                        mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
                        mySocket.settimeout(TIMEOUT)
                        try:
                                d = build_packet(data_size)
                                mySocket.sendto(d, (hostname, 0))
                                t= time.time()
                                startedSelect = time.time()
                                whatReady = select.select([mySocket], [], [], timeLeft)
                                howLongInSelect = (time.time() - startedSelect)
                                if whatReady[0] == []: # Timeout
                                        print("  *        *        *    Request timed out.")
                                recvPacket, addr = mySocket.recvfrom(1024)
                                timeReceived = time.time()
                                timeLeft = timeLeft - howLongInSelect
                                if timeLeft <= 0:
                                        print("  *        *        *    Request timed out.")

                        except timeout:
                                continue

                        else:
                                #Fill in start
                                #Fetch the icmp type from the IP packet
                                (types, code, checksum, packet_id, sequence, data) = struct.unpack("bbHHhd", recvPacket[20:36])

                                print("types: " + str(types) + " code: " + str(code) + " checksum: " + str(checksum) + " ID: " + str(packet_id) + " seq: " + str(sequence))

                                # Extra Credit #2, added comments to print out error codes
                                #Fill in end

                                if types == 11:
                                        bytes = struct.calcsize("d")
                                        timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                                        print("  %d    rtt=%.0f ms    %s" %(ttl, (timeReceived -t)*1000, addr[0]))
                                        if code == 0:
                                            print("0 error code = time to live exceeded in transit")
                                        if code == 1:
                                            print("1 error code = fragment reassembly time exceeded")

                                elif types == 3:
                                        bytes = struct.calcsize("d")
                                        timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                                        print("  %d    rtt=%.0f ms    %s" %(ttl, (timeReceived-t)*1000, addr[0]))
                                        if code == 0:
                                            print("0 error code = net unreachable")
                                        elif code == 1:
                                            print("1 error code = host unreachable")
                                        elif code == 2:
                                            print ("2 error code = protocol unreachable")
                                        elif code == 3:
                                            print ("3 error code = port unreachable")
                                        elif code == 4:
                                            print ("4 error code = fragmentation needed and DF set")
                                        elif code == 5:
                                            print ("5 error code = source route failed")    


                                elif types == 0:
                                        bytes = struct.calcsize("d")
                                        timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                                        print("  %d    rtt=%.0f ms    %s" %(ttl, (timeReceived - t)*1000, addr[0]))
                                        print("0 error code = echo reply")
                                        return

                                else:
                                        print("error, types is " + str(types))
                                break
                        finally:
                                mySocket.close()


print('Argument List: {0}'.format(str(sys.argv)))

data_size = 0
if len(sys.argv) >= 2:
    data_size = int(sys.argv[1])

# below are the routes for testing: 4 hosts on 3 different continents

#get_route("oregonstate.edu",data_size)
#get_route("gaia.cs.umass.edu",data_size)
#get_route("bbc.co.uk",data_size)
get_route("sony.co.jp",data_size)
