#!/usr/bin/python
#File: rasterScan.py
# 5/6/22

# V1.1.0  5/6/22- start coding -vline and -hline cmd line params
# V1.2.0  5/16/22 - Add options to read in and convert data file
# V1.3.0  6/12/2024 - Rewrite with classes

#Requires External file moveAxis.py
#Requires T4U_read.py


# USAGE: Call STScanner with a Controller class object parameter.
# Then call STScanner.scanner_ex()

import time
import sys
from RigolDP712 import Rigol_ReadVoltage, Rigol_SetVoltage, Rigol_tryConnect
import T4U_read
import moveAxis
import os
import numpy as np
import pandas as pd


verbose =1



# global constants
kScanTypeSerpentine = 1 # seemed like a good idea but its not
kScanTypeRaster = 2     # use this!


class STScanner:
    def __init__(self, controller) -> None:
        self.iniFile = ("config/T4UParsPD.ini")
        self.controller = controller   # the Controller class defined in amos.py
        self.verbose = verbose      
        self.scantype = kScanTypeRaster # 2 = Serpentine, 2 = Raster 
        # scantype not be be confused with scanType a string one of: "-hscan", "-vscan,  "-zscan", ... 

       
        
    

# #make python recal values
    def initVal (self):
        ini = pd.read_csv(self.iniFile, header="infer")
        self.centerX = ini.loc[0,"x"]
        self.centerY = ini.loc[0,"y"]
        
        self.width = ini.loc[0,"width"]
        self.N_samples = ini.loc[0,"precision"]
        self.Vsupply = ini.loc[0,"s1v"]



        self.vscan = 0
        self.hscan = 0
        self.zscan = 0

    
        self.startx = self.centerX  - (self.width/2.0)
        self.endx   = self.centerX  + (self.width/2.0)
        self.starty = self.centerY  - (self.width/2.0)
        self.endy   = self.centerY  + (self.width/2.0)
        self.stepx  = (self.endx - self.startx) / self.N_samples
        self.stepy  = (self.endy - self.starty) / self.N_samples

        # the following are used with option -zscan only
        # z scan parameters
        self.startz = 0
        self.endz = 10
        self.stepz = 1



    def ShowHelp(self):
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
    #   Move x,y motors
    #
    def move_motors(self, x,y):
       
        #if self.verbose:
        #    print("   X,Y:", "{:.3f}".format(x), "{:.3f}".format(y), end = "" ) 
        moveAxis.move( self.controller.motors[0],x)
        moveAxis.move( self.controller.motors[1],y)


    def move_zmotor(self, z):
        #if self.verbose:
        #    print("   Z:",  "{:.3f}".format(z), end = "" )
        moveAxis.move(self.controller.motors[2],z)


    def saveToDisk(self, x,y,vals):
        f = self.file
        if f:
            s = "{:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f}".\
                format(x,y, vals[0],vals[1], vals[2], vals[3] )
            f.write( s + "\n" )
            f.flush() 
            os.fsync(f)
            
            print("   " +  s  + "\r", end="") # over write same line
            self.controller.updateLivePlot( [ x,y, vals[0],vals[1], vals[2], vals[3] ], filename = f.name )


    def createHeader(self):
        """ Save Date Time Gain, and also save a background data set
        """
        import datetime
        now = datetime.datetime.now()   
        f = self.file
        f.write ("%" + now.strftime("%Y-%m-%d %H:%M:%S \n"))
        resp = T4U_read.readreg_ex(1, self.controller) 
        f.write("% Deci  {} \n".format(resp))

        resp = T4U_read.readreg_ex(3, self.controller) 
        f.write("% Gain  {} \n".format(resp))
        
        resp = T4U_read.readreg_ex(32, self.controller) # TODO
        f.write("% FWVer  {}.{}.{}.{} \n".format((resp >> 24) & 0x08, \
            (resp >> 16) & 0x08, (resp>>8) & 0x08 , resp & 0x8))
        
        # the next line must be formatted with 6 integers, but contains special information
        f.write("{} {} {} {} {} {} \n".format(self.startx, self.starty, self.endx, self.endy, self.stepx, self.stepy));

        # TODO - read 100 or 1000 points, with shutter closed? maybe not here  - somewhere.

    def scan( self):
        
        xmotor = self.controller.motors[0]
        ymotor = self.controller.motors[1]

        bScanning = True
        if self.hscan:
            self.starty = self.centerY  
            self.stepy = 0
            self.endy = self.starty-1
        elif self.vscan:
            self.startx = self.centerX
            self.stepx = 0
            self.endx = self.startx-1
        
        x = self.startx
        y = self.starty
        z = self.startz

        if self.zscan:
            zmotor =self.controller.motors[2]
         

        self.controller.updateLivePlot( [0,0,0,0,0,0 ], filename =self.file.name,  reset = 1 )
        while bScanning:
            if self.controller.interrupted:
                bScanning = False
                break
                
            self.move_motors(x,y) 
            if self.zscan:
                self.move_zmotor( z )

            tvals = T4U_read.readvlwc( self.controller.ser) #
            vals = [ tvals["ch1"], tvals["ch2"], tvals["ch3"], tvals["ch4"] ]
            
            if self.controller.ser.__class__.__name__ == "DummyT4U":
                vals = [1000+x+y, 1000+x-y, 1000, 1000]

            if self.zscan:
                self.saveToDisk(x,z,vals)    
            else:    
                self.saveToDisk(x,y,vals)


            x += self.stepx
            if x+ self.stepx > self.endx:
                if self.scantype == kScanTypeSerpentine:
                    self.stepx = -self.stepx
                    x += self.stepx
                    y += self.stepy
                elif self.scantype == kScanTypeRaster:
                    x = self.startx
                    y += self.stepy

                if x < self.startx:
                    if self.scantype == kScanTypeSerpentine:
                        self.stepx = -self.stepx
                        x += self.stepx
                        y += self.stepy
                
                if (y > self.endy):
                    if self.zscan:
                        z += self.stepz
                        if z>self.endz:
                            done = 1
                            break
                    else:    
                        # we are done
                        done = 1
                        break
                    
        if self.controller.interrupted:
            print("!! Routine aborted !!")
            self.controller.interrupted = False
        

      
# #
# #  Utility to convert original data files into something latex can parse more easily
# #
# def doConvert(fin,  convertType):
#     """ convertType is a string. Expect one of:hscan, vscan, raster, <future:bias, zscan>
#         f is file for reading in
#         Returns 0 on success
#     """
#     ncols = 0
#     skip = 0
#     test = fin.name
#     fout = open(fin.name +".conv", 'w')

#     if convertType == "hscan":
#         ncols = 6
#         skip = 1
#         header = "%X\tAD\tBC\n"
#         abcd =   [ z + 1 for z in [1,4,2,3] ]   # A D B C 
#     elif convertType == "vscan":
#         ncols = 6
#         skip = 1
#         header = "%Y\tAB\tCD\n"
#         abcd = [ z + 1 for z in [1,2,3,4] ]   # A B C D 
#     elif convertType == "raster":
#         ncols = 6
#         skip = 1
#         header = "%X\tY\tSUM\n"

#     elif convertType == "bias":
#         ncols = 5
#         skip = 1
#         header = "%V\tSUM\n"

#      #todo handle 'bias'   

    
#     #reading data rows
#     for line in fin:
#         if line.find("%") >= 0:
#             fout.write( line )  # write out comments straight through
#             continue
#         if skip>0:
#             skip -= 1  # skip the lines after comment
#             continue

#         if header:
#             fout.write(header)
#             header = None

#         chunks = line.split(' ')
#         if len(chunks) >= ncols:
#             if ( convertType == 'hscan') or (convertType == 'vscan'):
#                 X = float(chunks[0])
#                 Y = float(chunks[ abcd[0] ]) + float(chunks[  abcd[1] ])
#                 Z = float(chunks[ abcd[2] ]) + float(chunks[ abcd[3] ])
#             elif convertType == 'raster':
#                 X = float(chunks[0])
#                 Y = float(chunks[1])
#                 Z = float( chunks[2] ) + float( chunks[3] ) + \
#                     float( chunks[4] ) + float( chunks[5] ) 
#             elif convertType == 'bias':
#                 X = float(chunks[0])
#                 Y = 0
#                 Z = float( chunks[1] ) + float( chunks[2] ) + \
#                     float( chunks[3] ) + float( chunks[4] ) 
                
            
#             # hline expects X Y A B C D
#             s = "{:.3f}\t{:.3f}\t{:.3f}\n".\
#                 format(X, Y, Z )
#             fout.write( s )
                    
#     #
#     fout.close()
#     fin.close()
#     return 0

    # controller should contain args, bias and cmd properties
    # Will default to use parameters in ini file
    # but can ocverride values by defining a args object with startZ, endZ, startX, emdX, stepX params.
    def scanner_ex (self):
        
        
        self.initVal()
        scanType  = self.controller.cmd
        biasV = self.controller.bias1V
        
        # After initVal()...
        for k,v in self.controller.args.items():
            print(f"debug k = {k} v= {v}")
            if k == "startZ":
                self.startz = v

            elif k == "endZ":
                self.endz = v

            elif k == "stepZ":
                self.stepz = v
                
            elif k == "startX":
                self.startx = v
            elif k == "endX": 
                self.endx = v
            elif k == "stepX": 
                self.stepx = v


        if self.startz<0:
            self.startz = 0
        if self.endz <= self.startz:
            self.endz = self.startz    
            
        print("RasterScan 12JUN2024 V 1.3.0.  Running", scanType)
        print("   press 'q' to abort ")
        
        T4U_read.send( self.controller.ser, "wr 3 0", 0) 
        
        Rigol_SetVoltage(self.controller.Rigol_serialPort , biasV) 
            
           

    # if (v == 0):
    #     print("PLEASE CHECK THAT THE BIAS IS ON")

        if len(scanType) >= 1:
            if scanType == "-vscan":
                self.vscan = 1
                f = open("txts/vscan.txt", 'w')
            elif scanType == "-hscan":
                self.hscan = 1    
                f = open("txts/hscan.txt", 'w')
            elif scanType == "-zscan":
                self.zscan = 1
                self.hscan = 1
                f = open("txts/zscan.txt", 'w')
            elif scanType == "-raster":
                f = open('txts/raster'+ str(biasV)+".txt", 'w')


            else:
                self.ShowHelp()
                sys.exit()
        #
        
        self.file = f
        self.createHeader()
    ################### add in move to set z position in t4upars.ini T4UPars[6]
    
        self.scan(  )
        f.close()
        
     
