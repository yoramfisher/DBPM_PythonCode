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
#
# Edit values below
#
startv = 0 
endv   = 1
stepv  = 0.05

path_to_file = 'laser.txt'

cwd = os.getcwd()
T4Upars = np.loadtxt(r"T4UPars.ini",dtype = float, delimiter = None, comments = '%')
guesscenterX = T4Upars[0]
guesscenterY = T4Upars[1]
width = T4Upars[2]
N_samples = T4Upars[3]
#### mototr SNs need later

motorX = '80861709'
motorY = '80861770'
motorZ = '80861765'
verbose = 0
def move_motors(x,y):
   xmotor = moveAxis.setup(motorX)
   ymotor = moveAxis.setup(motorY)
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

def plot_Bscan (dSN):
   dat = np.loadtxt((cwd + r"\laser.txt"), dtype = float, delimiter = None, comments = '%',skiprows = 5,)

   x = (np.array(dat)[:,0] -20)
   tCounts = (np.array(dat)[:,1] + np.array(dat)[:,2] + np.array(dat)[:,3] + np.array(dat)[:,4])
   y = tCounts/np.max(tCounts) * -1
   figB = plt.figure()
   bPlot = figB.add_subplot(1,1,1)
   bPlot.plot(x, y, color ="blue")
   # To show the plot
   bPlot.set_title("Device Bias Scan SN " + dSN)
   bPlot.set_xlabel("Bias (V)")
   bPlot.set_ylabel("Current (Normalized)")
   #plt.show() 
   BpltName = "#Laser" + dSN + ".jpg"
   figB.savefig(str(BpltName))
   plt.close()
   
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

   plot_Bscan("laserTest")


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
   
