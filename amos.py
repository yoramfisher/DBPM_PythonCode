#created 06/14/2022 BWM 
#program to view 4 channels of Bias in loop for manual diamond alignment
# Align_Mode_On_Steroids == AMoS.py
# Version 1.0 YF 5/16/2024
# Write four values on one line, and remove LF so can update value w/o scrolling
# Add X,Y,Z to select motor to move.   1,2,3 to select step size, use +/- to move selected motor
# 'P' to pause and relinquish COM ports and Motors
# 'C' to record the current X,Y,Z motor positions as the new Center in the INI file.
#  Use text scroll bars [------|----] to show the relative position using A,B,C,D values
#########################
###import T4U_read
import sys
import moveAxis
import time
#import all functions from T4U read
import pandas as pd 

iniFile = ("T4UParsPD.ini")
ini = pd.read_csv(iniFile, header="infer")
thecomport= ini.loc[0,"COM"]


def test_the_code():
    import random
    for i in range(100):
        xpos  = (i - 50) / 100
        ypos  = (i - 50) / 100 
        A = int(random.randint(-10000, 10000))
        B = int(random.randint(-10000, 10000))
        C = int(random.randint(-10000, 10000))
        D = int(random.randint(-10000, 10000))
        
        barH = generate_bar_graph(xpos)
        barV = generate_bar_graph(ypos)

        print( f"{A:06d} {B:06d} {C:06d} {D:06d} {barH} {barV} \r", end="")
        time.sleep(.1)



#thecomport = "com18"
#
#
#
def generate_bar_graph(x):
    # Define the total number of dashes
    total_dashes = 11
    
    # Calculate the position of the pipe based on the value of x
    pipe_position = int(round((x + 1) * (total_dashes - 1) / 2))
    
    # Ensure the pipe position is within the valid range
    pipe_position = max(0, min(pipe_position, total_dashes - 1))
    
    # Generate the bar graph string
    bar_graph = "-" * pipe_position + "|" + "-" * (total_dashes - pipe_position - 1)
    
    return bar_graph

def main(argv):
    repeat = 0
    bQuery = 1
    T4U_read.sendCommand( thecomport, "wr 3 0", 1 )
    setas = T4U_read.sendCommand( thecomport, "rr 3", 1 )
    print (f"GAIN:{setas}. (If 0, you are in highest gain and all is right with the world.)")
    
    print("Press 'X,Y,Z' to select a motor.   Press '1,2,3' to select step size of 1,10,100")
    print("   Use '+/-' to move selected motor.")
    print("Press: ")
    print("  C to set current position to be the new Center.")
    print("  P to Pause / Unpause. When paused, motor and COM port are free'd")

    while True:  
        if len(argv)<1:
            resp = T4U_read.readvlwc(thecomport)
            A = resp["ch1"]
            B = resp["ch2"]
            C = resp["ch3"]
            D = resp["ch4"]
            sum = A + B + C + D
            # This isn't technically correct - oit should probaby be (C + D - A - B)/sum - but the 
            # other plot codes use abs() as shown.
            xpos = (abs(C + D)  - abs(A + B )) / sum
            ypos = (abs(A + D)  - abs(B + C )) / sum
            barH = generate_bar_graph(xpos)
            barV = generate_bar_graph(ypos)
            
            motorsPos = moveAxis.pollMotorStatus(doPrint=0)
            
            print( f"{A:06d}  {B:06d}  {C:06d}  {D:06d}   X:[{barH}] Y:[{barV}]  "
                  f"MX:{motorsPos[0]:06f}  MY:{motorsPos[1]:06f} ", end="")
            
            
            
        elif argv[0] == "read":
            time.sleep(.75)
            resp = T4U_read.readvlwc(thecomport)
            print("Ch1 " + resp['ch1'] + " Ch4 " + resp['ch4'] + "      ")
            print("Ch2" + resp['ch2'] + " Ch3" + resp['ch3'] + "      ")
            
        elif argv[0] == "pos":
            moveAxis.showMotorStatus()
            print("\033[A",end="")  # \033[A  is the Move Up one line esc seq.



#
#
#
if __name__ == "__main__":
    
   ##test_the_code()
   ##exit()
   
   argv = sys.argv
   main(argv[1:])