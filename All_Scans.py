#created 07/19/2022 BWM 
#program to run all scans needed for diamond report in one go
#########################
from T4U_read import*
import moveAxis
import time
from RasterScan import*
import BiasScan
import numpy as np
import os
#import all functions from T4U read
iniFile = ("config/T4UParsPD.ini")
ini = pd.read_csv(iniFile, header="infer")

def main(argv):
    
    repeat = 0
    bQuery = 1
    # print("Bias towns")
    #BiasScan.main(argv) 

    # uncomment below for z scann set precisions to 40 pts or else graphs will give bad results (In T4UPars.ini)
    #scanner("-zscan", float(ini.loc[0,"s1v"]))
    print("V and H towns")
    scanner("-vscan", float(ini.loc[0,"s1v"]))
    scanner("-hscan", float(ini.loc[0,"s1v"]))
    print("raster 1 town")
    scanner("-raster", float(ini.loc[0,"s1v"]))
    print("raster 2 ville")
    scanner("-raster", float(ini.loc[0,"s2v"]))
    print("Yoou did it!")
   


#
#
#
if __name__ == "__main__":
   argv = sys.argv
   main(argv[1:])