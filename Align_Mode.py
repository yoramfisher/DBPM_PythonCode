#created 06/14/2022 BWM 
#program to view 4 channels of Bias in loop for manual diamond alignment
#########################
import T4U_read
import sys
import moveAxis
import time
#import all functions from T4U read
import pandas as pd 

iniFile = ("T4UParsPD.ini")
ini = pd.read_csv(iniFile, header="infer")
thecomport= ini.loc[0,"COM"]


#thecomport = "com18"

def main(argv):
    repeat = 0
    bQuery = 1
    T4U_read.sendCommand( thecomport, "wr 3 0", 1 )
    setas = T4U_read.sendCommand( thecomport, "rr 3", 1 )
    print (str(setas)+ "if 0 you are in highest gain and all is right with the world")
    
    while True:  
        if len(argv)<1:
            resp = T4U_read.readvlwc(thecomport)
            print(resp)
            moveAxis.pollMotorStatus()
        elif argv[0] == "read":
            time.sleep(.75)
            resp = T4U_read.readvlwc(thecomport)
            print("Ch1 " + resp['ch1'] + " Ch4 " + resp['ch4'] + "      ")
            print("Ch2" + resp['ch2'] + " Ch3" + resp['ch3'] + "      ")
            
        elif argv[0] == "pos":
            moveAxis.showMotorStatus()
            print("\033[A",end="")



#
#
#
if __name__ == "__main__":
   argv = sys.argv
   main(argv[1:])