#
# File: comObject.pu
# Description: Abstract communication to T4U over Serial OR Ethernet
#
# History
# v 1.0 YF 03Mar2023 - Created
#

import os
import sys
import time
import socket
import serial
from datetime import datetime
import traceback
import random
import math


# CONFIGURATION
#



class comObject:
    """
    Supports either TCP or COM port I/O to 2Omega controller
    """
 
    
    # init method or constructor
    def __init__(self, comType, ip_addr, port, verbose=0):
        self.comms = None
        self.comType = comType
        self.ip_addr = ip_addr
        self.port = port
        self.verbose = verbose
        self.interCommandDelay = 0.1

    def open_serial(self):
        """
        port is com port, such as "COM3"
        returns a SerialPort
        """
        ser=serial.Serial()
        ser.port = self.port
        ser.baudrate = 19200
        ser.bytesize = serial.EIGHTBITS
        ser.parity = serial.PARITY_NONE
        ser.stopbits = serial.STOPBITS_ONE
        ser.timeout= 1
        ser.xonxoff = False
        ser.rtscts = False
        ser.dsrdtr = False
        ser.writeTimeout = 1
        return ser


    def open_socket(self):
        """
        port is TCP port such as 23
        returns a socket
        """
        comm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        comm_socket.connect( (self.ip_addr, self.port))
        comm_socket.settimeout( 1.0 ) # seconds
        return comm_socket

    #
    #
    #
    def tryConnect( self ):    
        """
        type 1 = TCPIP, 2 = COMM Port, else undefined
        Returns socket or serial port if connects OK
        """

        if (self.comType == 1):
            try:
                if self.verbose:
                    print("Opening socket:" + str(self.ip_addr) + ":" + str(self.port) )
                self.comms = self.open_socket() 
                return self.comms
                
            except Exception as e:
                print ('error opening TCP Port')
                
            return None

        if (self.comType == 2):
            try:
                if self.verbose:
                    print("Opening Serial:" + str(self.port) )
                self.comms = self.open_serial() # Initialise the serial port
                self.comms.open()         # open the serial port
                return self.comms
                
            except Exception as e:
                print ('error opening serial port')
                
            return None

        return None


    def sendQuery(self, cmd):
        """
        send a query - return a string response
        """
        recv = None
        if self.comms == None:
            return None     # Error. not open

        if self.verbose:
            print(cmd + " : ", end="")

        if self.comType == 1:   
            self.comms.send( (cmd+'\r\n').encode() ) 
            time.sleep(self.interCommandDelay);
            recv = self.comms.recv(1000).decode()
            time.sleep(self.interCommandDelay);

        if self.comType == 2:
            self.comms.write( (cmd+'\r\n').encode())
            time.sleep(self.interCommandDelay);

            response = self.comms.read_until()
            if len(response) > 0:
                recv = response.decode()

        if self.verbose:
            print(recv)        
        return recv        


    def parse(self, strResponse):
        # T? Returns T?>1.23:OK\r
        p1 = strResponse.split('>')   # T?       1.23:OK\r
        if p1 and len(p1) >= 2:
            p2 = p1[1].split(':')     #  1.23   OK\r
            if p2 and len(p2) ==2 :
                try:
                    v = float( p2[0] ) 
                    return v
                except ValueError: 
                    pass
                    
        return None  

    def setRange(self,rng):
        if (rng >=0 and rng <=2 ):
            return self.sendQuery("wr 3 {}".format( rng ))

    def read4(self):
        """ Return four raw values a,b,c,d in counts
        """
        res = self.sendQuery("read")
        # Expect "read>#,#,#,#:OK"
        p1 = res.split('>')   # read>#,#,#,#:OK\r
        if p1 and len(p1) >= 2:
            p2 = p1[1].split(':')     #,#,#,#   OK\r
            if p2 and len(p2) == 2:
                vals = p2[0].split(',')
                return vals    
                 
    def read4Many(self, N, channel):
        """ Average N reads, and return a scalar
        """
        sum = 0.0
        for i in range(N) :
            vals = self.read4()
            sum += float(vals[channel])   
        return sum / N;          