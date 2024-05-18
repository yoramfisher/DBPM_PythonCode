#!/usr/bin/python
#File: rasterScan.py
# 5/6/22

# V1.1.0  5/6/22- start coding -vline and -hline cmd line params
# V1.2.0  5/16/22 - Add options to read in and convert data file
#Requires External file moveAxis.py
#Requires T4U_read.py

import serial
import time
import sys
from RigolDP712 import Rigol_ReadVoltage, Rigol_SetVoltage, Rigol_tryConnect
import T4U_read
import moveAxis
import os
import numpy as np
import pandas as pd

################################
#modifying code to use pandas for start values 
#
# Edit values below
#
iniFile = ("config/T4UParsPD.ini")
ini = pd.read_csv(iniFile, header="infer")

guesscenterX = ini.loc[0,"x"]
guesscenterY = ini.loc[0,"y"]
#centerZ = ini.loc[0,"z"]
# if you want to be a winner and hard code your numbers
#guesscenterX = 0.815
#guesscenterY = 0.327
centerZ = 3.15

width = ini.loc[0,"width"]
N_samples = ini.loc[0,"precision"]
Vsupply = ini.loc[0,"s1v"]

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
    # z scan parameters
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
      s = "{:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f} \n".\
          format(x,y, vals[0],vals[1], vals[2], vals[3] )
      f.write( s )
      f.flush() 
      print( s , end="") # debug info


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
    
    # the next line must be formatted with 6 integers, but contains special information
    f.write("{} {} {} {} {} {} \n".format(startx, starty, endx, endy, stepx, stepy));

    # TODO - read 100 or 1000 points, with shutter closed? maybe not here  - somewhere.

def scan( fname):
    global stepx,stepy
    global xmotor, ymotor, zmotor
    global startx, starty
    global endx, endy
    global startz, enz, stepz
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

        vals = T4U_read.readv()

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
#
#  Utility to convert original data files into something latex can parse more easily
#
def doConvert(fin,  convertType):
    """ convertType is a string. Expect one of:hscan, vscan, raster, <future:bias, zscan>
        f is file for reading in
        Returns 0 on success
    """
    ncols = 0
    skip = 0
    test = fin.name
    fout = open(fin.name +".conv", 'w')

    if convertType == "hscan":
        ncols = 6
        skip = 1
        header = "%X\tAD\tBC\n"
        abcd =   [ z + 1 for z in [1,4,2,3] ]   # A D B C 
    elif convertType == "vscan":
        ncols = 6
        skip = 1
        header = "%Y\tAB\tCD\n"
        abcd = [ z + 1 for z in [1,2,3,4] ]   # A B C D 
    elif convertType == "raster":
        ncols = 6
        skip = 1
        header = "%X\tY\tSUM\n"

    elif convertType == "bias":
        ncols = 5
        skip = 1
        header = "%V\tSUM\n"

     #todo handle 'bias'   

    
    #reading data rows
    for line in fin:
        if line.find("%") >= 0:
            fout.write( line )  # write out comments straight through
            continue
        if skip>0:
            skip -= 1  # skip the lines after comment
            continue

        if header:
            fout.write(header)
            header = None

        chunks = line.split(' ')
        if len(chunks) >= ncols:
            if ( convertType == 'hscan') or (convertType == 'vscan'):
                X = float(chunks[0])
                Y = float(chunks[ abcd[0] ]) + float(chunks[  abcd[1] ])
                Z = float(chunks[ abcd[2] ]) + float(chunks[ abcd[3] ])
            elif convertType == 'raster':
                X = float(chunks[0])
                Y = float(chunks[1])
                Z = float( chunks[2] ) + float( chunks[3] ) + \
                    float( chunks[4] ) + float( chunks[5] ) 
            elif convertType == 'bias':
                X = float(chunks[0])
                Y = 0
                Z = float( chunks[1] ) + float( chunks[2] ) + \
                    float( chunks[3] ) + float( chunks[4] ) 
                
            
            # hline expects X Y A B C D
            s = "{:.3f}\t{:.3f}\t{:.3f}\n".\
                format(X, Y, Z )
            fout.write( s )
                    
    #
    fout.close()
    fin.close()
    return 0

def scanner (scanType, biasV):
    global hscan, vscan, zscan
    initVal()
    print("RasterScan 19July2022 V 1.2.0")
    T4U_read.main("wr 3 0")
    working = 3
    while working >0:
        
        # Check that Bias is ON!
        serialPort = Rigol_tryConnect()
       
        if serialPort == None:
            time.sleep(1)
            working -=1
        else:
           # v = Rigol_ReadVoltage(serialPort)
        #set the voltage on supply
            Rigol_SetVoltage(serialPort, biasV)
            break
        
        if working < 1:
            print("Voltage no worky, Check Voltage supply")
            sys.exit()
        

   # if (v == 0):
   #     print("PLEASE CHECK THAT THE BIAS IS ON")

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
            f = open('raster'+ str(biasV)+".txt", 'w')


        else:
            ShowHelp()
            sys.exit()
    # 
    createHeader( f )
################### add in move to set z position in t4upars.ini T4UPars[6]
   
    scan( f )
    f.close()
    serialPort.close()
     

#
#
def main(argv):
    theAxisToMoveSN = motorZ
    motor = moveAxis.setup(theAxisToMoveSN)
    moveAxis.move(motor,centerZ)
    scanner(argv[0],float(argv[1]))
     
      
  
      
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
   
