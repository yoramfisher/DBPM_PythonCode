#Created 9/26/2022 BWM
#Program to get single images from TXC dataViewer for general use
#Intended intial release for diamond scanning with TXC electronics

import sys
import time
import socket
import select

class TXCSocket:
    def __init__(self, dest_addr, dest_port = 14000):
        self.TXC_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.TXC_socket.connect((dest_addr, dest_port));
        

   
    def send_cmd(self, socket_str, timeout = 1):
        print("Sending command: {}".format(socket_str));
        bytes_sent = self.TXC_socket.send(socket_str.encode());
        sent_time = time.monotonic();
        read_list, write_list, err_list = select.select([self.TXC_socket], [], [], timeout);
        if (len(read_list) == 0):
            print("No read data.");
            return -1;
        TXC_response = self.TXC_socket.recv(4096);#How many bits should we get in a response any?
        recv_time = time.monotonic();
        print("Response: {}".format(TXC_response.decode()));
        print("Round-trip time: {}".format(recv_time-sent_time));
        return TXC_response.decode();
    
fileLoc = "C:\\Users\\benm\\Desktop\\TXC_Town\\Suite12_25AUG2022\\TXCViewer_v1.p19_release\\release\\junk.raw"
dvs = TXCSocket('127.0.0.1');
wreg = dvs.send_cmd("!L numFrames1\r\n") 
print (wreg)
wreg = dvs.send_cmd("!L savef " + fileLoc + "\r\n") 
print (wreg)