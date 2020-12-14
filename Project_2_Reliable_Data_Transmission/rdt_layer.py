# Giselle Northy
# Project 2 - RDT
# File name: rdt_layer.py

# Sources used:

# Reference [1] OSU: https://canvas.oregonstate.edu/courses/1784243/pages/exploration-rdt-with-tcp-stop-and-wait-retransmission?module_item_id=19971965
# Reference [2] StackOverflow: https://stackoverflow.com/questions/1207406/how-to-remove-items-from-a-list-while-iterating
# Reference [3] https://stackoverflow.com/questions/9371114/check-if-list-of-objects-contain-an-object-with-a-certain-attribute-value
# Reference [4] https://www.tutorialspoint.com/what-is-cumulative-acknowledgement
# Reference [5] Piazza - CS372 Section 400 - Project 2 Threads

from unreliable import *
import copy

class RDTLayer(object):
    # The length of the string data that will be sent per packet...
    DATA_LENGTH = 4 # characters
    # Receive window size for flow-control
    FLOW_CONTROL_WIN_SIZE = 15 # characters

    # Add class members as needed...
    #
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0 # <--- Use this for segment 'timeouts'
        self.seqnum = 0
        self.acknum = 0
        self.countSegmentTimeouts = 0
        self.dataReceived = ''
        self.tempSegments = []
        self.tempReceivedSegments = []

    # Called by main to set the unreliable sending lower-layer channel
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # Called by main to set the unreliable receiving lower-layer channel
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # Called by main to set the string data to send
    def setDataToSend(self,data):
        self.dataToSend = data

    # Called by main to get the currently received and buffered string data, in order
    def getDataReceived(self):
        #print('Complete this... okay?')
        return self.dataReceived

    def updateReceivedSegments(self):
        for tempSeg in self.tempReceivedSegments:
            if (self.acknum == tempSeg.seqnum): #found the next segment
                self.dataReceived = self.dataReceived + tempSeg.payload #add to dataReceive string
                self.acknum = self.acknum + self.DATA_LENGTH # update next expected ACK
                self.tempReceivedSegments.remove(tempSeg) # delete from received segments waiting to be put back together
                self.updateReceivedSegments() #call function again incase more are out of order in this list
                break

    # "timeslice". Called by main once per iteration
    def manage(self):
        self.currentIteration += 1
        self.manageSend()
        self.manageReceive()

    # Manage Segment sending  tasks...
    def manageSend(self):
            #debug stuff
            print("Current tempSegments: ", end="")
            for tempSeg in self.tempSegments:
                print(str(tempSeg.seqnum) + tempSeg.payload + " ", end="")
            print("\nCurrent tempReceivedSegments: ", end="")
            for tempSeg in self.tempReceivedSegments:
                print(str(tempSeg.seqnum) + tempSeg.payload + " ", end="")

            # first look through existing segments sent and see if any timed out
            # see if any Segments need to be re-sent
            for tempSeg in self.tempSegments:
                if (self.currentIteration - tempSeg.getStartIteration() > 5):
                    #timed out, no ACK received, resend
                    self.countSegmentTimeouts = self.countSegmentTimeouts + 1
                    print("Resending seg " + str(tempSeg.seqnum))
                    tempSeg.setStartIteration(self.currentIteration)
                    self.sendChannel.send(copy.copy(tempSeg))
            
            # You should pipeline segments to fit the flow-control window
            # The flow-control window is the constant RDTLayer.FLOW_CONTROL_WIN_SIZE
            # The maximum data that you can send in a segment is RDTLayer.DATA_LENGTH
            # These constants are given in # characters

            # the sequence number next to send, plus length, does not go beyond the window start at last received ack
            while ((self.seqnum + self.DATA_LENGTH) < (self.acknum + self.FLOW_CONTROL_WIN_SIZE)):

                #Send data if there is still more data to send
                if (len(self.dataToSend) > self.seqnum):
                    seg = Segment()
                    # set data to be send to start at sequence, and go until sequence + data length
                    seg.setData(self.seqnum,self.dataToSend[self.seqnum:(self.seqnum+self.DATA_LENGTH)])
                    # Set start iteration at this loop, so we know when timeout might occur and resend
                    seg.setStartIteration(self.currentIteration)
                    # Update Sequence number                
                    self.seqnum = self.seqnum + self.DATA_LENGTH;
                    # send a copy, in the event data gets corrupted on send
                    self.sendChannel.send(copy.copy(seg))
                    # store segement incase it needs to be resent later
                    self.tempSegments.append(seg)
                else:
                    #we have sent all the data we wanted to send
                    break


    # Manage Segment receive  tasks...
    def manageReceive(self):
        # This call returns a list of incoming segments (see Segment class)...
        listIncoming = self.receiveChannel.receive()
        
        #print('got...')
        #print(listIncoming)
        #print('length is ' + str(len(listIncoming)))

        # debug
        print("Printing all values incoming...")
        for inc in listIncoming:
            print(inc.to_string())
        print("done printing all incoming...")

        sendAck = False

        # server side getting message from client, putting it back together
        for incoming in listIncoming:
            #print(incoming.to_string())
            if (incoming.seqnum == self.acknum):
                #make sure packet is not corrupted
                if (incoming.checkChecksum()):
                    self.dataReceived = self.dataReceived + incoming.payload
                    # Update next segement expected (ACK responsel)
                    self.acknum = self.acknum + self.DATA_LENGTH
                    # We should check if there are additional segments we received out of order
                    self.updateReceivedSegments()
                    sendAck = True
                
            elif (incoming.seqnum == -1):
                #this is an ACK message, don't send an ACK back
                sendAck = False
                
                #go through all pending time-out segments and clear if ACKed
                # if the seq number is less than acknum, remove it from the list
                # reference [3]
                self.tempSegments[:] = [tempSeg for tempSeg in self.tempSegments if not (tempSeg.seqnum < incoming.acknum)]
                # update flow control window to determine how many have been received ok
                #numCharsClear = incoming.acknum - self.acknum
                #if (numCharsClear == 0): #if we get an ACK for the same sequence we are at, 
                #    numCharsClear = 1    #   we are being let know it got something out of order
                #numCharsClear = numCharsClear * self.DATA_LENGTH
                #self.charsInWindow = self.charsInWindow - self.DATA_LENGTH
                self.acknum = incoming.acknum
                
                #for tempSeg in self.tempSegments:
                #    if (tempSeg.seqnum < incoming.acknum):
                #        print("Removing seg " + str(tempSeg.seqnum) + " from resend list")
                        #need to remove this outside of the loop
                        #self.tempSegments.remove(tempSeg)
                        
                    
            elif (incoming.seqnum > self.acknum):
                # this one is out of order, so we need to save it elsewhere to reassemble later

                # check and see if this sequence is already in the list
                if (incoming.checkChecksum()):
                    # reference [3]
                    if(not any(tempSeg.seqnum == incoming.seqnum for tempSeg in self.tempReceivedSegments)):
                        print("Adding " + incoming.to_string() + " to list.")
                        self.tempReceivedSegments.append(incoming)
                    sendAck = True
            else:
                sendAck = True

        # The goal is to employ cumulative ack, just like TCP does...
        if (sendAck):
            ack = Segment()
            ack.setAck(self.acknum)
            # Use the unreliable sendChannel to send the ack packet
            self.sendChannel.send(ack)
                
        #print(listIncoming[0].to_string())
        # How can you tell data segments apart from ack segemnts?


        
