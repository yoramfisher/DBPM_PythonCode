#
#   Description  - Automated Calibration of T4U
#   Talks directly to T4U hardware over Serial or Ethernet
#   Does not use EPICS or comms via the T4U Viewer app.
#  
# History
# v1.0 YF 03MAR2023 Based on IM t4u_calibration.py
#
# To install scipy type: python -m pip install scipy

import Keithley
import sys
import time
#import subprocess
from comObject import comObject 

import scipy
import scipy.stats


# USER SETTINGS
#  # Example on Windows:"COM4"
#  # Example on Linux:"/dev/ttyUSB0"
KEITHLEY_COM_PORT = "/dev/ttyUSB0" 

#
VERBOSE = 2  # set to 0 to be silent, set to 1 to get some debug output, 2 to get more


# Enter a value of 1 for TCP or 2 for Serial Port
CONNECTION_TYPE = 1  

# SET the device IP Address below # Only used if CONNECTION_TYPE == 1
TCP_SOCKET_PORT=23
#IP_ADDR="192.168.11.58"
IP_ADDR="192.168.11.100"
#
## or set serial port # Only used if CONNECTION_TYPE == 2
#
T4U_PORT="com3"

CURR_SLEEP = 1.0;               # How long to sleep after setting current
#EPICS_SCALE_FACTOR = 1e9;       # How the currents are scaled

MEASURE_FILENAME = "t4u_raw_measure.txt"
CALIBRATION_FILENAME = "t4u_sn_cal.txt"

my_keithley = Keithley.Keithley(KEITHLEY_COM_PORT);

#-=-= FIXME The labels in current_array are RANGE, while below is for GAIN
#gain_array = [('low',0), ('medium',1), ('high',2)]
gain_array = [('low',2), ('medium',1), ('high',0)]


# NOTE WELL The absolute values of the currents must be in non-descending order
current_array = {}
current_array['low'] = [ 500e-9, -500e-9, 1e-6, -1e-6, 100e-6, -100e-6, 500e-6, -500e-6, 1e-3, -1e-3, 2e-3, -2e-3, 4e-3, -4e-3]
current_array['medium'] = [50e-12, -50e-12, 100e-9, -100e-9, 1e-6, -1e-6, 20e-6, -20e-6, 50e-6, -50e-6]
current_array['high'] = [50e-12, -50e-12, 100e-12, -100e-12, 500e-12, -500e-12, 1e-9, -1e-9, 50e-9, -50e-9, 100e-9, -100e-9, 200e-9, -200e-9]

num_channels = 4;

def toCurrent(counts, range):
    """ Given raw CVounts - return nanoAmps
        range is 0,1,2
    """
    # Resistor values are 5Meg, (5M || 15k) = 14955.13, and (5M || 47) = 46.99955
    kGainResistors = [  5e6, 14955.13, 47, 0 ] # 3 is not valid
    kVREF = 1.50 # Volts
    fcalSlope = 1.0
    fcalOffset = 0
    kMAX_COUNTS = 524288.0

    # 00 = Highest Gain (R = 5M)
    # 01 = Mid Gain (R = 5M || 15k)
    # 10 = Low Gain (R = 5M || 47)

    adcResistor = kGainResistors[ range ]
    maxAmpsPerPixel = kVREF / adcResistor

    f = ( counts / kMAX_COUNTS) * maxAmpsPerPixel
    nA = (f - fcalOffset)/fcalSlope    
    return nA


def doCalib( comObject ):
    # Prepare the files for logging
    measure_file = open(MEASURE_FILENAME, "w"); # Truncate and open
    measure_file.close();                       # Close for later append
    calibration_file = open(CALIBRATION_FILENAME, "w") # Truncate and open
    calibration_file.close();

    for channel_idx in range(num_channels):
        # Prepare the Keithley
        my_keithley.set_current(0.0)
        my_keithley.enable_output(False)

        # Prepare for logging
        measure_file = open(MEASURE_FILENAME, "a"); # Open in append
        calibration_file = open(CALIBRATION_FILENAME, "a");

        print("Connect current source to channel {} and press Enter.".format(channel_idx+1))

        sys.stdin.readline();
        
        
        my_keithley.enable_output(True);
        time.sleep(1.0)

        # XXX May change if Autorange is added to T4U
        for gain_pair in gain_array:
            curr_gain = gain_pair[0] # The gain name
            curr_gain_val = gain_pair[1] # The EPICS number for the gain

            result = comObject.setRange(curr_gain_val);
            if result == None:          
                print("Error setting range.")
                sys.exit(1)

            # Time to set currenet ranging
            # First set to minimum current, then enable autoranging
            # so that we only upscale for a given range.
            # This assumes the absolute values of the currents are non-decreasing
            my_keithley.send_cmd(":SOUR:CURR:RANG {}\r\n".format(current_array[curr_gain][0]))
            time.sleep(1.0);
            my_keithley.send_cmd(":SOUR:CURR:RANG:AUTO ON\r\n");
            time.sleep(1.0)

            current_x_val = [];
            current_y_val = [];     # The input and measured currents

            for current in current_array[curr_gain]:
                my_keithley.set_current(current);
                time.sleep(CURR_SLEEP)
                
                # Now we have to get the currents
                val = comObject.read4Many(10, channel_idx)
                val_na = toCurrent( val , curr_gain_val) 
               
                channel_current = val_na
                if VERBOSE:
                    print("Set:{}, Read:{}".format(current, channel_current))

                current_x_val.append(current);
                current_y_val.append(channel_current);

                measure_file.write('{}, {}, {}, {}\n'.format(channel_idx, curr_gain, current, channel_current));

                
            linreg_results = scipy.stats.linregress(current_x_val, current_y_val);
            calibration_file.write("{}, {}, {}, {}, {}, {}\n".format(channel_idx, curr_gain, curr_gain_val, linreg_results.slope, linreg_results.intercept, linreg_results.rvalue*linreg_results.rvalue))

        measure_file.close();
        calibration_file.close()


   
#
#
#
def main(argv):
    r = None
    if CONNECTION_TYPE == 1:
        c = comObject( 1, IP_ADDR, TCP_SOCKET_PORT, VERBOSE )
        r = c.tryConnect()
   
    if CONNECTION_TYPE == 2:
        c = comObject( 1, None, T4U_PORT, VERBOSE )
        r = c.tryConnect()

    if (r):
        #now = datetime.now() # current date and time
        doCalib( c )
        pass

    else:
        if c.verbose:
            print("Error, Could not connect")


    if r:
        if c.verbose:
            print("Close connection")
        c.comms.close()


    print("DONE!")
#
#
#
if __name__ == "__main__":
   main(sys.argv[1:])

