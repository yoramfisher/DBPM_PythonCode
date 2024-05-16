import Keithley
import sys
import time
import subprocess
import scipy
import scipy.stats

def epics_caput(prefix, record, pv_name, val):
    full_pv_name = prefix + record + pv_name;

    cmd_result = subprocess.run(["caput", full_pv_name, str(val)])
    return cmd_result.returncode

def epics_caget(prefix, record, pv_name):
    full_pv_name = prefix + record + pv_name;
    cmd_result = subprocess.run(["caget", full_pv_name], capture_output=True)
    return (cmd_result.returncode, cmd_result.stdout.decode().split()[1])

EPICS_PREFIX = "QE1_"
EPICS_RECORD = "T4U_EM_"
CURR_SLEEP = 1.0;               # How long to sleep after setting current
EPICS_SCALE_FACTOR = 1e9;       # How the currents are scaled

KEITHLEY_COM_PORT = "/dev/ttyUSB0"
MEASURE_FILENAME = "t4u_raw_measure.txt"
CALIBRATION_FILENAME = "t4u_sn_cal.txt"

my_keithley = Keithley.Keithley(KEITHLEY_COM_PORT);

gain_array = [('low',0), ('medium',1), ('high',2)]

# NOTE WELL The absolute values of the currents must be in non-descending order
current_array = {}
current_array['low'] = [ 500e-9, -500e-9, 1e-6, -1e-6, 100e-6, -100e-6, 500e-6, -500e-6, 1e-3, -1e-3, 2e-3, -2e-3, 4e-3, -4e-3]
current_array['medium'] = [50e-12, -50e-12, 100e-9, -100e-9, 1e-6, -1e-6, 20e-6, -20e-6, 50e-6, -50e-6]
current_array['high'] = [50e-12, -50e-12, 100e-12, -100e-12, 500e-12, -500e-12, 1e-9, -1e-9, 50e-9, -50e-9, 100e-9, -100e-9, 200e-9, -200e-9]

num_channels = 4;

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
    
    # Set the scale factors for EPICS
    scale_pv_name = "CurrentScale{}".format(channel_idx+1)
    epics_caput(EPICS_PREFIX, EPICS_RECORD, scale_pv_name, EPICS_SCALE_FACTOR)
    
    my_keithley.enable_output(True);
    time.sleep(1.0)

    # XXX May change if Autorange is added to T4U
    for gain_pair in gain_array:
        curr_gain = gain_pair[0] # The gain name
        curr_gain_val = gain_pair[1] # The EPICS number for the gain

        cmd_result = epics_caput(EPICS_PREFIX, EPICS_RECORD, "Range", curr_gain_val);
        if cmd_result != 0:
            print("Error setting EPICS range.")
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
            current_read_pv = "ReadData.PROC";
            epics_caput(EPICS_PREFIX, EPICS_RECORD, current_read_pv, 1); # Send the command to read the currents and flush old values
            time.sleep(3.0)     # Wait for the old values to flush
            epics_caput(EPICS_PREFIX, EPICS_RECORD, current_read_pv, 1); # We should now have 10000 fresh current values
            
            # Now we can read the current
            cmd_result = epics_caget(EPICS_PREFIX, EPICS_RECORD, "Current{}:MeanValue_RBV".format(channel_idx+1))
            if cmd_result[0] != 0:
                print("Error reading current.");
                sys.exit(1)

            channel_current = float(cmd_result[1])/EPICS_SCALE_FACTOR
            current_x_val.append(current);
            current_y_val.append(channel_current);

            measure_file.write('{}, {}, {}, {}\n'.format(channel_idx, curr_gain, current, channel_current));

            
        linreg_results = scipy.stats.linregress(current_x_val, current_y_val);
        calibration_file.write("{}, {}, {}, {}, {}, {}\n".format(channel_idx, curr_gain, curr_gain_val, linreg_results.slope, linreg_results.intercept, linreg_results.rvalue*linreg_results.rvalue))

    measure_file.close();
    calibration_file.close()
