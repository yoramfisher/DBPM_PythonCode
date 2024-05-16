import numpy as np
from scipy.stats import linregress
import statistics

NUM_CURRENTS = 5;
NUM_GAINS = 3;
NUM_CHANS = 32;

MEASURE_FILENAME = 'txc_calibration.txt';

def line_to_data_split(file_line):
    channel_idx = int(file_line.split(',')[0]);
    gain_idx = int(file_line.split(',')[1]);
    current_idx = int(file_line.split(',')[2]);
    nominal_current = float(file_line.split(',')[3]);
    recorded_current = float(file_line.split(',')[4]);
    return channel_idx, gain_idx, current_idx, nominal_current, recorded_current

def xlate_csv_line(curr_line):
    new_string = curr_line.replace('low', '0');
    new_string = new_string.replace('medium', '1');
    new_string = new_string.replace('high', '2');
    return new_string

# Create the array -- all currents are indexed in this array
data_array = np.ndarray((NUM_CHANS, NUM_GAINS, NUM_CURRENTS, 2),dtype=np.double);

# Now load and populate each part of the array
measure_file = open(MEASURE_FILENAME, "r");
for curr_line in measure_file:
    chan, gain, curr_idx, i_x, i_y = line_to_data_split(xlate_csv_line(curr_line));
    data_array[chan, gain, curr_idx, 0] = i_x;
    data_array[chan, gain, curr_idx, 1] = i_y;

# Create the output files
out_files = [];
out_files.append(open('gain_low.txt', 'w'));
out_files.append(open('gain_medium.txt', 'w'));
out_files.append(open('gain_high.txt', 'w'));

# Create arrays to hold some collected statistics
slope_array = np.ndarray([NUM_GAINS, NUM_CHANS])
offset_array = np.ndarray([NUM_GAINS, NUM_CHANS])
gain_names = ['Low', 'Medium', 'High']

# With the data loaded, we can now do the analysis
for channel_idx in range(NUM_CHANS):
    for gain_idx in range(NUM_GAINS):
        x_curr = data_array[channel_idx, gain_idx, :, 0];
        y_curr = data_array[channel_idx, gain_idx, :, 1];
        slope, intercept, r_value, p_value, std_err = linregress(x_curr, y_curr);
        out_files[gain_idx].write('{:2d}, {:8.5f}, {:12.5e}, {:8.5f}\n'.format(channel_idx, slope, intercept, r_value*r_value));
        slope_array[gain_idx, channel_idx] = slope
        offset_array[gain_idx, channel_idx] = intercept

for curr_file in out_files:
    curr_file.close();

# Now print out statistics for the slopes and offsets
for gain_idx in range(NUM_GAINS):
    slope_mean = np.mean(slope_array[gain_idx, :])
    slope_std = np.std(slope_array[gain_idx, :])

    offset_mean = np.mean(offset_array[gain_idx, :])
    offset_std = np.std(offset_array[gain_idx, :])

    print("{} Gain".format(gain_names[gain_idx]))
    print("Slope -- Mean: {:8.5f} Std: {:12.5e}".format(slope_mean, slope_std))
    print("Offset -- Mean: {:12.5e} Std: {:12.5e}\n".format(offset_mean, offset_std))

