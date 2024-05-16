#created 06/14/2022 BWM 
#program to view 4 channels of Bias in loop for manual diamond alignment
#########################
import sys
from BiasScan import *
from plotRaster import *
from plotHVscan import *
from plotBScans import *



def main(argv):
    repeat = 0
    bQuery = 1
    if len(argv) >=2:
        
        if argv[0] == "all":
            plot_Raster(argv[1], T4Upars[4])
            plot_Raster(argv[1], T4Upars[5])
            plot_Bscan(argv[1])
            plot_HV(argv[1])
        elif argv [0] == "2d":
            plot_Raster(argv[1], T4Upars[4])
            plot_Raster(argv[1], T4Upars[5])
        elif argv [0] == "bias":
            plot_Bscan(argv[1])
        elif argv [0] == "line":
            plot_HV(argv[1])
        else: 
            print("try again but this time follow directions")
    else:
        print("Please try again with type of plot you want (all, 2d, bias, or line) and the device serial number with a space between the two like a good little boy or girl ")

#
#
#
if __name__ == "__main__":
   argv = sys.argv
   main(argv[1:])