import sys

INI_FILENAME = "DBPM_Settings.ini"
CAL_FILENAME = "t4u_sn_cal.txt"

cal_file = open(CAL_FILENAME, "r")

NUM_CHAN = 4
NUM_RANGE = 3

cal_array = [];
for range_idx in range(NUM_RANGE):
    cal_pairs = []
    for chan_idx in range(NUM_CHAN):
        cal_pairs.append((1234,2345)); # Append obviously wrong values
    cal_array.append(cal_pairs)

for curr_line in cal_file:
    split_line = curr_line.split(","); # Comma delimited
    print(curr_line)
    curr_chan = int(split_line[0])
    curr_range = int(split_line[2])
    curr_range_let = chr(curr_range+ord('A'))
    cal_array[curr_range][curr_chan] = (float(split_line[3]),float(split_line[4]))

# Iterate over all ranges to produce only the direct calibration
ini_file = open(INI_FILENAME, "w")

for range_idx in range(NUM_RANGE):
    ini_file.write("[direct_range{}]\n".format(range_idx))
    for channel_idx in range(NUM_CHAN):
        curr_range_let = chr(channel_idx+ord('A'))
        ini_file.write('Channel{}="{}, {}"\n'.format(curr_range_let, cal_array[range_idx][channel_idx][0], cal_array[range_idx][channel_idx][1]))

    ini_file.write('\n')

    
