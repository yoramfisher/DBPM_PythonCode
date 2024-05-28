#created 06/14/2022 BWM 
#program to view 4 channels of Bias in loop for manual diamond alignment
# Align_Mode_On_Steroids == AMoS.py
# Version 1.0 YF 5/16/2024
# V 1.1 YF 5/17/2024
#  Add H, V, and R commands.
# Write four values on one line, and remove LF so can update value w/o scrolling
# Add X,Y,Z to select motor to move.   1,2,3 to select step size, use +/- to move selected motor
# 'P' to pause and relinquish COM ports and Motors
# 'C' to record the current X,Y,Z motor positions as the new Center in the INI file.
#  Use text scroll bars [------|----] to show the relative position using A,B,C,D values
#  'H' run a Horizontal scan now, use the current X,Y,Z as center
#  'V' run a vertical scan now, use the current X,Y,Z as center
#  'R' run a raster scan now, use the current X,Y,Z as center
#########################
import T4U_read
import sys
import moveAxis
import time
#import all functions from T4U read
import pandas as pd 
import keyboard

from math import fsum 

import RasterScan as RS
import random

# Requires
# pip install keyboard
VERBOSE = 1

NUM_TO_AVE = 100

# MAKE SURE THESE ARE SET TO ZERO FOR REAL DATA!
TEST_WITH_DUMMY_MOTORS = 0
TEST_WITH_DUMMY_T4U = 0


STEPS_PER_MM = 2.1739e6


class DummyMotor:
    def __init__(self, name) -> None:
        self.name = name
        self.pos = 1.0
    def get_position(self):
        return 1000
    def get_real_value_from_device_unit(self, pos , whatevs):
        return self.pos   
    def move_relative(self, dx):
        self.pos += dx
    def close(self):
        self.IsClosed = True    
    
class DummyT4U:
    def __init__(self) -> None:
        pass
    def write(self, x):
        pass
    def close(self, ):
        pass
        
        

class Controller:
    def __init__(self, iniFilename="") -> None:
        self.iniFilename = iniFilename
        self.quit = False
        self.paused = False
        self.keypressed = ""
        self.selectedMotor = 0
        self.stepSize = 10
        self.ser = None
        self.motors = [None, None, None]
        keyboard.on_press(self.on_key_press)
    
        self.ini = pd.read_csv(iniFilename, header="infer")
        self.comport= self.ini.loc[0,"COM"]
        self.bias1V = float(self.ini.loc[0,"s1v"])
        self.bias2V = float(self.ini.loc[0,"s2v"])
        self.center = [None, None, None]
        
        if TEST_WITH_DUMMY_T4U:
            self.x = 0
            self.y = 0
            self.dx = .011
            self.dy = .022
            
    
    
    def on_key_press(self, event):        
        if event.name == 'Q':
            keyboard.unhook_all()
            self.quit = True
            
        self.keypressed = event.name
            
    def read_t4u(self):

        if TEST_WITH_DUMMY_T4U:
            if  (self.x + self.dx > 10000) or (self.x+self.dx < 0) :
                self.dx = -self.dx 
            if  (self.y + self.dy > 10000) or (self.y+self.dy < 0) :
                self.dy = -self.dy 

            self.x += self.dx
            self.y += self.dy
            
            A = 1.1*(self.x + self.y)
            B = 1.2*(self.x - self.y)
            C = 1.3*(-self.x -self.y)
            D = 1.4*(-self.x + self.y)
                    
            return    (A, B, C, D)
        
        if self.ser:
            resp = T4U_read.send( self.ser, "read", 1 )
            #returns: read>173, 247, 298, 216:OK
            if len(resp)>5:
                a = resp[5:] # remove 'read>'
                b = a.split(':')
                c= b[0].split(',')
                if len(c) == 4:
                    return  ( int(c[0]), int(c[1]), int(c[2]), int(c[3]) )
            
            return(-1,-1,-1,-1) # error!

        else:
            return (0,0,0,0)


    def move_motor(self, axis, stepsize):
        stepsize = int(stepsize)
        if (axis >= 0) and ( axis < len(self.motors) ):
            self.motors[axis].move_relative( stepsize )
            moveAxis.wait( self.motors[axis] )


    def move_to_center(self, moveWhichAxis = [1,1,1]):
        for i in range(3):
            if self.center[i] and (moveWhichAxis[i] == 1):
                moveAxis.move( self.motors[i], self.center[i])
                

    def handle_pause( self, p ):
        if p:
            self.close_motors()
            self.close_t4u()
            if VERBOSE:
                print("### close_motors,  close_t4u ###")
        else:
            if VERBOSE:
                print("*** open_motors,  open_t4u ###")

            self.open_motors()
            self.open_t4u()
                
            

    def handle_keys(self):    
        key = self.keypressed    
        moveBack = None
        if key == 'x':
            self.selectedMotor = 0
        elif key == 'y':
            self.selectedMotor = 1
        elif key == 'z':
            self.selectedMotor = 2
        elif key == '1':
            self.stepSize = STEPS_PER_MM * 0.001  # 1 um
        elif key == '2':
            self.stepSize = STEPS_PER_MM * 0.01
        elif key == '3':
            self.stepSize = STEPS_PER_MM * 0.1
        elif key == '4':
            self.stepSize = STEPS_PER_MM          # 1 mm

        elif key == '+':
            self.move_motor(self.selectedMotor, self.stepSize)
        elif key == '-':
            self.move_motor(self.selectedMotor, -self.stepSize)
        elif key == 'P':
            self.paused =  not self.paused
            self.handle_pause( self.paused) 
            
        elif ( key == 'H'  or  key == 'V' 
              or key == 'R' or key == 'Z'):
            
            self.write_to_config()    

            self.paused = True
            self.handle_pause( self.paused) 
            cmd= None
            if key == 'H':
                cmd = "-hscan"
                moveBack = [1,0,0]
            elif key == 'V':
                cmd = "-vscan"    
                moveBack = [0,1,0]
            elif key == 'R':
                cmd = "-raster" 
                moveBack = [1,1,0]   
            elif key == 'Z':
                cmd = "-zscan" 
                moveBack = [0,0,1]   
                
            
            if cmd:
                RS.scanner (cmd, self.bias1V) 

            
            self.paused = False
            self.handle_pause( self.paused)  
            self.move_to_center( moveBack)

        elif ( key == 'C'):
            self.write_to_config()

        self.keypressed = ""     

            

    def test_the_code(self):
      
        while not self.quit:
            for i in range(100):
                
                ret = self.handle_keys( )
                if self.quit:
                    break
                xpos  = (i - 50) / 100
                ypos  = (i - 50) / 100 
                A = int(random.randint(-10000, 10000))
                B = int(random.randint(-10000, 10000))
                C = int(random.randint(-10000, 10000))
                D = int(random.randint(-10000, 10000))
                
                barH = self.generate_bar_graph(xpos)
                barV = self.generate_bar_graph(ypos)

                print( f"{A:06d} {B:06d} {C:06d} {D:06d} {barH} {barV} \r", end="")
                time.sleep(.1)



    #
    #
    #
    def generate_bar_graph(self,x):
        # Define the total number of dashes
        total_dashes = 11
        
        # Calculate the position of the pipe based on the value of x
        pipe_position = int(round((x + 1) * (total_dashes - 1) / 2))
        
        # Ensure the pipe position is within the valid range
        pipe_position = max(0, min(pipe_position, total_dashes - 1))
        
        # Generate the bar graph string
        bar_graph = "-" * pipe_position + "|" + "-" * (total_dashes - pipe_position - 1)
        
        return bar_graph


    #
    #x,y,width,precision,s1v,s2v,z,COM
    #11.487,15.902,5,20,0,40,3,COM20
    #
    def write_to_config(self):
        # Set a new value in the DataFrame
        pos  = [0,0,0]
        real = [0,0,0]
        for i in range(3):
            try:
                pos[i]  = self.motors[i].get_position()
                real[i] = self.motors[i].get_real_value_from_device_unit(pos[i], 'DISTANCE')
                self.center[i] = real[i]
            except Exception as e:
                print("!Exception:", e)

        self.ini['x'] = self.ini['x'].astype(str)
        self.ini['y'] = self.ini['y'].astype(str)
        self.ini['z'] = self.ini['z'].astype(str)
        
        self.ini.loc[0, 'x'] = f"{real[0]:.4f}"
        self.ini.loc[0, 'y'] = f"{real[1]:.4f}"
        self.ini.loc[0, 'z'] = f"{real[2]:.4f}"

        # Write the updated DataFrame back to the file
        self.ini.to_csv(iniFile, index=False)
        if VERBOSE:
            print(f"Wrote: x={ self.ini.loc[0, 'x']} y={self.ini.loc[0, 'y']} z={self.ini.loc[0, 'z']} ")

        

    def open_motors(self):
        if TEST_WITH_DUMMY_MOTORS:
            self.motors[0] = DummyMotor('X')
            self.motors[1] = DummyMotor('Y')
            self.motors[2] = DummyMotor('Y')
        else:   
            self.motors[0] = moveAxis.trysetup( moveAxis.motorX)
            self.motors[1] = moveAxis.trysetup( moveAxis.motorY)
            self.motors[2] = moveAxis.trysetup( moveAxis.motorZ)

    def close_motors(self):
        for i in range(3):
            moveAxis.close(  self.motors[i] )
            # self.motors[i].close()
    
    def open_t4u(self):
        if TEST_WITH_DUMMY_T4U:
            self.ser = DummyT4U()
        else:    
            self.ser = T4U_read.tryConnect(self.comport)

    def close_t4u(self):
        if self.ser:
            self.ser.close()
            self.ser = None

    #
    #
    #
    def main(self,argv):
        repeat = 0
        bQuery = 1
        
        
        if not TEST_WITH_DUMMY_T4U:
            if self.ser:
                T4U_read.send(self.ser, "wr 3 0", 1 )
                setas = T4U_read.send(self.ser, "rr 3", 1 )
                print (f"GAIN:{setas}")
                if setas != 0:
                    print("Warning!  Gain is not set to zero!")
                
            
        
        # TODO: how many steps per mm?   use 1um, 10um , 100um, 1000um steps 
        print("Press 'x,y,z' to select a motor.   Press '1,2,3,4' to select step size of 1, 10, 100, 1000um")
        print("   Use '+/-' to move selected motor.")
        print("Press: ")
        print("  C to set current position to be the new Center.")
        print("  P to Pause / Unpause. When paused, motor and COM port are free'd")
        print("  H to run an HScan from this position")
        print("  V to run a VScan from this position")
        print("  Z to run a Z-Scan from this position")
        print("  R to run a RasterScan from this position")
        print("\n\n   Q to quit.")
        
             

        while True:  
            
            ret = self.handle_keys( )
            if self.quit:
                break

            if self.paused:
                continue
                
            if (self.ser == None) or \
                (self.motors[0] == None) or (self.motors[1] == None) \
                or (self.motors[2] == None):
                continue
            
            
            vec = [self.read_t4u() for _ in range(NUM_TO_AVE)]
            A, B, C, D = [int( round(fsum(x) / len(vec))) for x in zip(*vec)]
                
            #  !!!!!
            # This isn't technically correct - it should probaby be (C + D - A - B)/sum - but the 
            # other plot codes use abs() as shown.
            # !!!!!!
            sum = A + B + C + D
            if sum == 0:
                sum = .0001    # hack
            #xpos = ((C + D)  - (A + B )) / sum
            #ypos = ((A + D)  - (B + C )) / sum

            # 5/28/24 - Switch to same format as used in Oper manuals, and
            # make it agree with the T4U App!
            xpos = -((A + D)  - (B + C )) / sum  # Additional minus sign reqd to match T4u App
            ypos = -((A + B)  - (C + D )) / sum
            
            barH = self.generate_bar_graph(xpos)
            barV = self.generate_bar_graph(ypos)
            pos= [None, None, None]
            real= [None, None, None]
            for i in range(3):
                pos[i] = self.motors[i].get_position()
                real[i] = self.motors[i].get_real_value_from_device_unit(pos[i], 'DISTANCE')
            
            smx = "[MX]" if self.selectedMotor == 0 else "mx"
            smy = "[MY]" if self.selectedMotor == 1 else "my"
            smz = "[MZ]" if self.selectedMotor == 2 else "mz"
            
            print( f"{A:06d}  {B:06d}  {C:06d}  {D:06d}   X:[{barH}] Y:[{barV}]  "
                    f"{smx}:{real[0]:8.4f}  {smy}:{real[1]:8.4f}   {smz}:{real[2]:8.4f}        \r", end="")
                
                
        
    
            
#
#
#
if __name__ == "__main__":
    
    iniFile = ("config/T4UParsPD.ini")
    C = Controller( iniFilename = iniFile )
    C.open_motors()
    C.open_t4u()
    
    
    argv = sys.argv
    C.main(argv[1:])   # Use 'q' . Dont ctrl-c out of this!
    
    C.close_motors()
    
        