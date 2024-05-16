#!/usr/bin/python
#File: rasterScan.py
# 5/6/22

# V1.1.0  5/6/22- start coding -vline and -hline cmd line params
# V1.2.0  5/16/22 - Add options to read in and convert data file
#Requires External file moveAxis.py
#Requires T4U_read.py

# Use: .\RasterScanTXC.py -raster 0
# Where: <execute program> <action> <gain?>

import serial
import time
import sys
from RigolDP712 import Rigol_ReadVoltage, Rigol_SetVoltage, Rigol_tryConnect
import TXC_read
import moveAxis
import os
import numpy as np

txc_obj = TXC_read.TXC_read();
#
# Edit values below
#
cwd = os.getcwd()
T4Upars = np.loadtxt("T4UPars.ini",dtype = float, delimiter = None, comments = '%')

guesscenterX = T4Upars[0]
guesscenterY = T4Upars[1]
width = T4Upars[2]
N_samples = T4Upars[3]
Vsupply = T4Upars[4]

#make python recal values
def initVal ():
    global stepx,stepy
    global xmotor, ymotor, zmotor
    global startx, starty
    global endx, endy
    global startz, endz, stepz
    global vscan, hscan, zscan
    vscan = 0
    hscan = 0
    zscan = 0

    VS = Vsupply
    #
    # kludge for finer xscan
    # width = 1
    #
    #

    startx = guesscenterX - (width/2.0)
    endx   = guesscenterX + (width/2.0)
    starty = guesscenterY - (width/2.0)
    endy   = guesscenterY + (width/2.0)
    stepx  = (endx - startx) / N_samples
    stepy  = (endy - starty) / N_samples

    # the following are used with option -zscan only
    startz = 0
    endz = 10
    stepz = 1
    

path_to_file = ''


# As seen by CCD
# X is Left/Right,  0 on the Left
# Y is Up/Down,  0 is on bottom
# Z is toward X-ray source, 0 is furthest.
#
#  Important that these serial numbers match the axes.
# 
motorX = '80861709'
motorY = '80861770'
motorZ = '80861765'


# constants
kScanTypeSerpentine = 1 # seemed like a good idea but its not
kScanTypeRaster = 2     # use this!

scantype = kScanTypeRaster # 2 = Serpentine, 2 = Raster 


# Some globals
xmotor = None
ymotor = None
zmotor = None
verbose =0



def ShowHelp():
   print( "Raster Scan X-Y and some times z motors and read values from T4U")
   print( "  Save output to a file.")
   print ("Usage:")
   print ("    -raster + voltage -- runs raster scan with voltage ")
   print ( "   -vscan + voltage -- runs 1 vertical scan through gcx,gcy")
   print ( "   -hscan + voltage -- runs 1 horizontal scan through gcx,gcy")
   print ( "   -zscan + voltage -- runs hscans at different z positions for finding best focus.")
   print ()
   print ( "   -help  -- Show Help")
   
   print("  Edit T4UPars.ini to change step size, precision, x-y start " )
   

#
#  STUB - call actual motor move here
#
def move_motors(x,y):
    global xmotor, ymotor
    if verbose:
        print("X,Y:",  "{:.3f}".format(x), "{:.3f}".format(y) ) 
    moveAxis.move(xmotor,x)
    moveAxis.move(ymotor,y)


def move_zmotor(z):
    global zmotor
    if verbose:
        print("Z:",  "{:.3f}".format(z) )
    moveAxis.move(zmotor,z)


def saveToDisk(f, x,y,vals):
   if f:
      s = "{:.3f} {:.3f} {:.3f} {:.3f} \n".\
          format(x,y, vals[0],vals[1],  )
      f.write( s )
      f.flush() 
      print( s , end="") # debug info


def createHeader(f):
    """ Save Date Time Gain, and also save a background data set
    """
    import datetime
    now = datetime.datetime.now()   
    global txc_obj;
    f.write ("%" + now.strftime("%Y-%m-%d %H:%M:%S \n"))
    resp = txc_obj.readreg(1)
    f.write("% Deci  {} \n".format(resp))

    resp = txc_obj.readreg(3)
    f.write("% Gain  {} \n".format(resp))
    
    resp = txc_obj.readreg(32)
    f.write("% FWVer  {}.{}.{}.{} \n".format((resp >> 24) & 0x08, \
        (resp >> 16) & 0x08, (resp>>8) & 0x08 , resp & 0x8))
    
    # the next line must be formatted with 6 integers, but contains special information
    f.write("{} {} {} {} {} {} \n".format(startx, starty, endx, endy, stepx, stepy));

    # TODO - read 100 or 1000 points, with shutter closed? maybe not here  - somewhere.

def scan( fname):
    global stepx,stepy
    global xmotor, ymotor, zmotor
    global startx, starty
    global endx, endy
    global startz, enz, stepz
    global txc_obj
    # open up and 'talk to motors
    xmotor = moveAxis.setup(motorX)
    ymotor = moveAxis.setup(motorY)

    bScanning = True
    if hscan:
        starty = guesscenterY
        stepy = 0
        endy = starty-1
    elif vscan:
        startx = guesscenterX
        stepx = 0
        endx = startx-1
    
    x = startx
    y = starty
    z = startz

    if zscan:
        zmotor = moveAxis.setup(motorZ)
        move_zmotor(z)

    while bScanning:
        move_motors(x,y) # todo
        if zscan:
            move_zmotor( z )

        vals = txc_obj.queryFlux()

        if vals == -1:          # An error
            vals = [-99999.99, 99999.99]; # Flip signs to help flag error
        else:
            vals = [float(x) for x in vals.strip().split()];

        if zscan:
            saveToDisk(fname, x,z,vals)    
        else:    
            saveToDisk(fname, x,y,vals)


        x += stepx
        if x+stepx > endx:
            if scantype == kScanTypeSerpentine:
               stepx = -stepx
               x += stepx
               y += stepy
            elif scantype == kScanTypeRaster:
               x = startx
               y += stepy

            if x < startx:
                if scantype == kScanTypeSerpentine:
                    stepx = -stepx
                    x += stepx
                    y += stepy
            
            if (y > endy):
                if zscan:
                    z += stepz
                    if z>endz:
                        done = 1
                        break
                else:    
                    # we are done
                    done = 1
                    break
    if xmotor:
        moveAxis.close(xmotor)
    if ymotor:
        moveAxis.close(ymotor)
    if zmotor:
        moveAxis.close(zmotor)


def scanner (scanType):
    global hscan, vscan, zscan
    initVal()
    print("RasterScanTXC 03Oct2022 V 1.0.0")
  

    if len(scanType) >= 1:
        if scanType == "-vscan":
            vscan = 1
            f = open("vscan.txt", 'w')
        elif scanType == "-hscan":
            hscan = 1    
            f = open("hscan.txt", 'w')
        elif scanType == "-zscan":
            zscan = 1
            hscan = 1
            f = open("zscan.txt", 'w')
        elif scanType == "-raster":
            f = open('TXCraster'+ ".txt", 'w')


        else:
            ShowHelp()
            sys.exit()
    # 
    createHeader( f )

    scan( f )
    f.close()
    #serialPort.close()
     

#
#
def main(argv):
    scanner(argv[0])
     
      
  
      
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
   
