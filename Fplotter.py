#created 06/14/2022 BWM 
#program to view 4 channels of Bias in loop for manual diamond alignment
#########################
import sys
from FplotRaster import *
from FplotBScans import *

cwd = os.getcwd()
T4Upars = np.loadtxt(r"T4UPars.ini",dtype = str, delimiter = None, comments = '%')

def main(argv):
    repeat = 0
    bQuery = 1
    if len(argv) >=2 : 
        if argv[0] == "all":
            plot_Raster(argv[1], float(T4Upars[4]))
            plot_Raster(argv[1], float(T4Upars[5]))
            plot_Bscan(argv[1])
        elif argv [0] == "2d":
           # plot_Raster(argv[1], float(T4Upars[4]))
            plot_Raster(argv[1], float(T4Upars[5]))
        elif argv [0] == "bias":
            plot_Bscan(argv[1])
    else: 
        print("Please don't suck and enter what type of plot you want (all, 2d, or bias) followed by device serial number")


#
#
#
if __name__ == "__main__":
   argv = sys.argv
   main(argv[1:])