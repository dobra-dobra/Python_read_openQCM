"""
    Program to read and save data from openQCM microbalance
    by
    Szymon Jakubiak
    Twitter: @SzymonJakubiak
    LinkedIn: https://pl.linkedin.com/in/szymon-jakubiak
    ver. 0.91
    
    MIT License

    Copyright (c) 2020 Szymon Jakubiak
    
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
import serial, time

# Specify serial port
device_port = "COM46"

# Specify output file name, comment and header for data
output_file = "SL_output.txt"
comment = "Output data from openQCM microbalance"
data_header = "date,time,frequency,temperature" # Separate data columns by commas
data_units = "yyyy:mm:dd,hh:mm:ss,Hz,deg.C" # Separate data columns by commas

# Create object for serial port
device_ser = serial.Serial(device_port, baudrate=9600, stopbits=1, parity="N",  timeout=2)
device_ser.flushInput()

def quality_check(data):
    """
    Expects string, returns tuple with valid data
    or False when data was invalid
    """
    if data != False:
        if "RAWMONITOR" in data:
            data = data.replace("RAWMONITOR","")
            data = data.split("_")
            frequency = 2 * 8000000 - int(data[0])
            temperature = int(data[1]) / 10
            return (frequency, temperature)
    else:
        return False

def ser_data(ser):
    """
    Expects serial port object as an input, returns data from serial device
    or False when there was no data to read
    """
    # Wait for the begginning of the message
    if ser.inWaiting() > 0:
        data = b""
        last_byte = b""
        # Loop untill the end character was read
        while last_byte != b"\xff":
            last_byte = ser.read()
            data += last_byte
        data = data[:-1].decode().rstrip()
        return quality_check(data)
    else:
        return False

def time_stamp():
    """
    Expects nothing, returns time stamp in format dd:mm:yyyy,hh:mm:ss
    """
    date = time.localtime()
    stamp = "{0:4}.{1:02}.{2:02},{3:02}:{4:02}:{5:02}".format(date[0], date[1], date[2], date[3], date[4], date[5])
    return stamp

header = "\n* * * *\n" + comment + "\n* * * *\n"
header += data_header + "\n" + data_units
print(header)
file = open(output_file, "a")
file.write(header + "\n")
file.close()

try:
    while True:
        output = ser_data(device_ser)
        if output != False:
            output_data = time_stamp() + ",{0},{1:.1f}".format(output[0], output[1])
            file = open(output_file, "a")
            file.write(output_data + "\n")
            file.close()
            print(output_data)

except KeyboardInterrupt:
    device_ser.close()
    print("Data logging stopped")
