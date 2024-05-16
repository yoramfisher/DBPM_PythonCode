import serial

class Keithley:
    def __init__(self, com_port):
        self.k_serial = serial.Serial(com_port, 19200, timeout=2);
        return
    def read_port(self):
        in_bytes = b'';

        while True:
            curr_byte = self.k_serial.read();
            if len(curr_byte) == 0: # A timeout
                return -1;
            elif curr_byte == b'\n': # End of response
                in_bytes += curr_byte;
                return in_bytes;
            else:               # An ordinary bytes
                in_bytes += curr_byte;
                
    def set_current(self, new_current):
        set_i_str = ':SOUR:CURR:LEV:IMM:AMPL {}\r\n'.format(new_current);
        set_i_bytes = set_i_str.encode();
        self.k_serial.write(set_i_bytes); # Send the bytes
        # No response expected
        return;

    def enable_output(self, bOn):
        if bOn:
            on_num = 1;
            on_str = 'ON';
        else:
            on_num = 0;
            on_str = 'OFF';

        cmd_str = ':OUTP:STAT '+ str(on_num) + '\r\n';
        print(cmd_str);
        cmd_bytes = cmd_str.encode();
        self.k_serial.write(cmd_bytes);
        return;
    
    def send_cmd(self, cmd_str):
        cmd_bytes = cmd_str.encode();
        self.k_serial.write(cmd_bytes);
        return;
