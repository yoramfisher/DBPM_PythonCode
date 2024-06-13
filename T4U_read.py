#!/usr/bin/python

#File: T4U_read.py
# 5/6/22


import serial
import time
import sys
import pandas as pd
import random

verbose = 0
thecomport = ""


def ShowHelp():
   print( "Send a command over (virtual) serial port to TXC-4.")
   print ("Usage:")
   print (sys.argv[0] + " read")
   print (sys.argv[0] + " read -loop -- read forever Ctrl-C to stop.")
   print (sys.argv[0] + " rr 0 -- example to read register 0")
   print (sys.argv[0] + " wr 1 20 -- example to write reg1 = 20")
   


def init(port):
    """
    port is com port, such as "COM3"
    """
    ser=serial.Serial()
    ser.port = port
    ser.baudrate = 115200
    ser.bytesize = serial.EIGHTBITS
    ser.parity = serial.PARITY_NONE
    ser.stopbits = serial.STOPBITS_ONE
    ser.timeout= 1
    ser.xonxoff = False
    ser.rtscts = False
    ser.dsrdtr = False
    ser.writeTimeout = 1
    return ser


def readreg(reg):
   global thecomport
   if thecomport == "":
      iniFile = ("config/T4UParsPD.ini")
      ini = pd.read_csv(iniFile, header="infer")
      thecomport= ini.loc[0,"COM"]

   resp = sendCommand( thecomport, "rr {}".format(reg), 1 )
   #returns: rr>#:OK
   if verbose:
      print(resp)
   
   a = resp.index('>') +1
   b = resp.index(':')
   res = int(resp[a:b])
   return res


def readreg_ex(reg, controller):

   if  controller.ser.__class__.__name__ == "DummyT4U":
      return 0
   
   resp = send( controller.ser,  "rr {}".format(reg), 1 ) 
   #returns: rr>#:OK
   if verbose:
      print(resp)
   
   a = resp.index('>') +1
   b = resp.index(':')
   res = int(resp[a:b])
   return res

def readv():
   resp = sendCommand( thecomport, "read", 1 )
   #returns: read>173, 247, 298, 216:OK
   if verbose:
      print(resp)
   
   a = resp[5:] # remove 'read>'
   b = a.split(':')
   c= b[0].split(',')

   # Convert Float String List to Float Values
   # Using float() + list comprehension
   res = [float(x) for x in c]
  
   return res


#BWM Mod ReadV for Align mode
def readvl():
   resp = sendCommand( thecomport, "read", 1 )
   #returns: read>173, 247, 298, 216:OK
   if verbose:
      print(resp)
   
   a = resp[5:] # remove 'read>'
   b = a.split(':')
   c= b[0].split(',')

   # Convert Float String List to Float Values
   # Using float() + list comprehension
   Ch_list = {}
   Ch_list["ch1"] = c[0]
   Ch_list["ch2"] = c[1]
   Ch_list["ch3"] = c[2]
   Ch_list["ch4"] = c[3]

   return Ch_list
######################
#BWM New feature for passing comport in read command 6/15/23
#######################
def readvlwc(ser):
   
   if ser.__class__.__name__ == "DummyT4U":
      return { "ch1": random.randint(0,500)+1000, "ch2":random.randint(0,500)+2000, "ch3":1500, "ch4":2100 } # simulated data
   
   resp = send( ser, "read", 1 )
   #returns: read>173, 247, 298, 216:OK
   if verbose:
      print(resp)
   
   a = resp[5:] # remove 'read>'
   b = a.split(':')
   c= b[0].split(',')
  
   # Convert Float String List to Float Values
   # Using float() + list comprehension
   # Ch_list = {}
   # Ch_list["ch1"] = c[0]
   # Ch_list["ch2"] = c[1]
   # Ch_list["ch3"] = c[2]
   # Ch_list["ch4"] = c[3]

   if len(c) == 4:
      return  ( int(c[0]), int(c[1]), int(c[2]), int(c[3]) )

def send(ser,command,bQuery):
    """ returns result as string
    """
    ser.write((command+'\r\n').encode())

    if bQuery:
       response = ser.read_until()
    
       if len(response) > 0:
           if verbose:
              print (response.decode())
           ser.flushInput()

       return response.decode()
    return ""   

def setup(ser):
    """
    Setup TODO
    """
        


def tryConnect( port ):    
    """
    Returns ser if connects OK
    """
    try:
        ser = init(port) # Initialise the serial port
        ser.open()         # open the serial port
        return ser
        
    except Exception as e:
        print ('error opening serial port')
        
    return None

def sendCommand(port, cmd, bQuery):
   """
   """
   ser = tryConnect(port);
   if ( ser and ser.isOpen() ):
     
      try:

         resp = send(ser, cmd, bQuery) 
         ser.close()
         return resp


      except Exception as e1:
         print ("Error Communicating...: " + str(e1))
    

   else:
      print ("Could not open serial portError.\r\n");


   
#
#
#
def main(argv):
   #print("Hello from Main")
   repeat = 0
   bQuery=1

   
   if len(argv) < 1:
      #ShowHelp()
      #sys.exit()
      cmds = 'read'
   else:
      cmds = ' '.join(argv[0:])

                   
   if (len( argv ) == 2)  and \
       (argv[0].upper() == "READ") and \
       (argv[1].upper() == "-LOOP") :
          repeat = 1

      
      
   while True:  
      sendCommand( thecomport, cmds, bQuery )
      if  not repeat:
         break

#
#
#
if __name__ == "__main__":

   if len(sys.argv) <= 1:
      ShowHelp()
      sys.exit()

   #thecomport = "com18"

   verbose =0
   argv = sys.argv

   #
   #
   #  #debug
   ## argv = ['this', 'read', '-loop']
   #
   #
   #
   main(argv[1:])
   
