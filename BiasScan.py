#!/usr/bin/python
#File: BiasScan.py
# 5/6/22


from ast import Global
from venv import create
import serial
import time
import sys
import T4U_read
import RigolDP712
import numpy as np
import matplotlib as plt
import os
import moveAxis
import pandas as pd
#
# Edit values below
#
startv = 0 ## -5
endv   = 40.1
stepv  = 0.1

path_to_file = 'bscan.txt'

iniFile = ("config/T4UParsPD.ini")
ini = pd.read_csv(iniFile, header="infer")
guesscenterX = ini.loc[0,"x"]
guesscenterY = ini.loc[0,"y"]
centerZ = 0   #  ini.loc[0,"z"]    Go to a strongly defocussed z pos for Bias scan.
width = ini.loc[0,"width"]
N_samples = ini.loc[0,"precision"]


#### mototr SNs need later

motorX = '80861709'
motorY = '80861770'
motorZ = '80861765'
verbose = 0
def move_motors(x,y):
   xmotor = moveAxis.setup(motorX)
   ymotor = moveAxis.setup(motorY)
   theAxisToMoveSN = motorZ
   zmotor = moveAxis.setup(theAxisToMoveSN)
   moveAxis.move(zmotor,centerZ)
   if verbose:
        print("X,Y:",  "{:.3f}".format(x), "{:.3f}".format(y) ) 
   moveAxis.move(xmotor,x)
   moveAxis.move(ymotor,y)


def ShowHelp():
   print( "Sweep Bias Voltage read values from TXC-4")
   print( "  Save output to a file.")
   print ("Usage:")
   print (sys.argv[0])
   print("  Edit this file to change startv, endv, stepv " )
   

#def  set_Bias(v):
#   #KoradKA3005P.main("V {:2f}".format(v))
#   KoradKA3005P.main("V {:2f}".format(v))
#   #debug only
#   print("An exception occurred" + "V {:2f}".format(v) )
   
   
def createHeader(f):
    """ Save Date Time Gain, and also save a background data set
    """
    import datetime
    now = datetime.datetime.now()   
    f.write ("%" + now.strftime("%Y-%m-%d %H:%M:%S \n"))
    resp = T4U_read.readreg(1)
    f.write("% Deci  {} \n".format(resp))

    resp = T4U_read.readreg(3)
    f.write("% Gain  {} \n".format(resp))
    
    resp = T4U_read.readreg(32)
    f.write("% FWVer  {}.{}.{}.{} \n".format((resp >> 24) & 0x08, \
        (resp >> 16) & 0x08, (resp>>8) & 0x08 , resp & 0x8))
    
    # the next line must be formatted with 5 integers, but contains special information
    f.write("{:.2f} {:.2f} {:.2f} {:.2f} {:.2f} \n".format(startv, endv, stepv, 0,0));

    # TODO - read 100 or 1000 points, with shutter closed? maybe not here  - somewhere.


def saveToDisk(f, v,vals):
   if f:
      s = "{:.3f} {:.3f} {:.3f} {:.3f} {:.3f} \n".\
          format(v, vals[0],vals[1], vals[2], vals[3] )
      f.write( s )
      print( s , end="") # debug info

    
def scan( fname, serialPort):
   """
   fname is file
   serialPort is serial port
   """
   bScanning = True  
   v = startv
   
   while bScanning:
      # set Bias Voltage
      RigolDP712.Rigol_SetVoltage( serialPort, v) 

      vals = T4U_read.readv()

      saveToDisk(fname, v,vals)
            
      v += stepv
   
      if (v > endv):
          # we are done
          done = 1
          break


   
#
#
#BWM add code to set motor to center
def main(argv):
   print("Hello from Main")
   move_motors(guesscenterX,guesscenterY) 
   ser = RigolDP712.Rigol_tryConnect()
   if ser:
      f = open(path_to_file, 'w')
      createHeader( f )
      
      scan( f, ser )
      f.close()
      ser.close()

#
#
#
if __name__ == "__main__":

  
   argv = sys.argv

   #
   #
   #  #debug
   ## argv = ['this', 'read', '-loop']
   #
   #
   #
   main(argv[1:])
   
