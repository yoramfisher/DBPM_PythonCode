import TXC_read
import Keithley
import sys
import time

def compute_current(flux_on, flux_off, resistor, kVREF=1.5):
    total_flux = (flux_on-flux_off)/2.0;
    # Correction for no diamond
    total_flux = flux_on;
    current = total_flux/524288.0*kVREF/resistor;
    return current;

TXC_ADDR = '192.168.11.61';
TXC_ADDR = '192.168.11.116';
KEITHLEY_COM_PORT = '/dev/ttyUSB0';
MEASURE_FILENAME = 'txc_sweep.txt';

my_txc = TXC_read.TXC_read(TXC_ADDR);
my_keithley = Keithley.Keithley(KEITHLEY_COM_PORT);
CURR_SLEEP = 1;               # How long to sleep after setting current

gain_array = ['low', 'medium', 'high'];
current_array = {};

# -=-= XXX The analysis code depends on there being an equal
# number of currents for each gain
# NOTE WELL -- The currents must be in ascending order
current_array['low'] = [50e-12, 50e-9, 1e-6, 500e-6, 1e-3];
current_array['medium'] = [50e-12, 500e-12, 100e-9, 1e-6, 50e-6];
current_array['high'] = [50e-12, 100e-12, 500e-12, 1e-9, 100e-9];

resistor_vals = {};
resistor_vals['high'] = 5e6;
resistor_vals['medium'] = 14955.13;
resistor_vals['low'] = 47;
                    
num_channels = 32;

my_txc.bsReg(0, 0x600);

# Prepare the file for logging
measure_file = open(MEASURE_FILENAME, "w"); # Truncate and open
measure_file.close();                       # Close for later append

for channel_idx in range(num_channels):
    # Prepare the Keithley
    my_keithley.set_current(0.0);
    my_keithley.enable_output(False);
    
    # Prepare for logging
    measure_file = open(MEASURE_FILENAME, "a"); # Open in append

    # Prompt user for connection
    print("Connect current source to channel {} and press Enter.".format(channel_idx));
    sys.stdin.readline();       # -=-= TODO Should I use input()?

    my_keithley.enable_output(True);
    time.sleep(1.0);

    # -=-= XXX May change if Autorange is added to TXC
    for curr_gain in gain_array:
        if curr_gain == 'low':
            my_txc.writeReg(3, 2);
        elif curr_gain == 'medium':
            my_txc.writeReg(3, 1);
        elif curr_gain == 'high':
            my_txc.writeReg(3,0);
        else:
            print('Invalid gain.  Aborting.');
            sys.exit(1);

        # Time to set current ranging
        # First set to minimum current, then enable autoranging
        # so that we only upscale for a given range.
        # This assumes the currents for a range are in ascending order.
        my_keithley.send_cmd(':SOUR:CURR:RANG {}\r\n'.format(current_array[curr_gain][0]));
        time.sleep(1.0);
        my_keithley.send_cmd(':SOUR:CURR:RANG:AUTO ON\r\n');
        time.sleep(1.0);
            
        channel_curr_idx = -1;  # Index of current applied to channel
        for current in current_array[curr_gain]:
            channel_curr_idx += 1;
            # Set the current
            my_keithley.set_current(current);
            time.sleep(CURR_SLEEP);

            # Get the column ADU
            txc_current_string = my_txc.queryCol(channel_idx);
            txc_current  = int(txc_current_string);
            
            measure_file.write('{}, {}, {}, {}, {}\n'.format(channel_idx, curr_gain, channel_curr_idx, current, txc_current));

    measure_file.close();        # Close to commit values in case of later loss


    
