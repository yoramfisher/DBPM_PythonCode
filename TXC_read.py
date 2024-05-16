#!/usr/bin/python

#File: TXC_read.py
# 9/27/2022


import socket
import time
import select

class TXC_read:
    def __init__(self, dest_addr = '127.0.0.1', dest_port = 14000):
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.my_socket.connect((dest_addr, dest_port));

    def flushSocket(self):
        while True:
            readable, writeable, errored = select.select([self.my_socket], [], [], 0.01);
            if len(readable) == 0: # Socket empty
                return;
            self.my_socket.recv(4096); # Slurp data and loop again
        
    def readResponse(self):
        read_bytes = b'';
        while True:
            readable, writeable, errored = select.select([self.my_socket],[],[], 1.0);
            if len(readable) == 0:
                print(read_bytes);
                return -1;      # No data to read

            curr_byte = self.my_socket.recv(1);
            if (curr_byte == b'\0'):
                continue;       # Slurp nulls
            
            read_bytes += curr_byte;
            if (curr_byte == '\n'.encode()) or (curr_byte == 'K'.encode()) :
                read_string = read_bytes.decode();
                print(read_bytes);
                return read_string;

    def queryFlux(self):
        query_str = '!L getFlux\r\n';
        self.flushSocket();
        self.my_socket.send(query_str.encode());
        resp_str = self.readResponse();
        #print(resp_str);
        return resp_str;

    def queryCol(self, col_idx):
        query_str = '!L getCol {}\r\n'.format(col_idx);
        self.flushSocket();
        self.my_socket.send(query_str.encode());
        resp_str = self.readResponse();
        return resp_str;

    def writeReg(self, reg_num, val):
        write_str = 'wr {} {}\r\n'.format(reg_num, val);
        self.my_socket.send(write_str.encode());
        self.flushSocket();
        return 0;

    def bsReg(self, reg_num, val):
        bs_str = 'bs {} {}\r\n'.format(reg_num, val);
        self.my_socket.send(bs_str.encode());
        self.flushSocket();
        return 0;
    
    def readreg(self, reg_num):
        query_str = 'rr {}\r\n'.format(reg_num);
        self.flushSocket();
        self.my_socket.send(query_str.encode());
        resp_str = self.readResponse();

        if resp_str == -1:      # An error condition
            return -1;          # Negative indicates error condition, since correct result is unsigned
        
        resp_num = int(resp_str.split(':')[0].split('>')[1]);
        return resp_num
