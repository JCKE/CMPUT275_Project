import sys
import serial
import time
import argparse

#ser = serial.Serial('/dev/ttyAMC0', 9600)

def parse_args():
    """
    Parses arguments for this program.
    Returns an object with the following members:
    args.
    serialport -- str
    verbose    -- bool
    """
    
    parser = argparse.ArgumentParser(
        description='Assignment 1: Map directions.',
        epilog = 'If SERIALPORT is not specified, stdin/stdout are used.')

    parser.add_argument('-s', '--serial',
                        help='path to serial port',
                        dest='serialport',
                        default=None)
    parser.add_argument('-d', dest='verbose',
                        help='debug',
                        action='store_true')

    return parser.parse_args()

args = parse_args()

if args.serialport:
    print("Opening serial port: %s" % args.serialport)
    ser = serial.Serial(args.serialport, 9600)
    print("OK ITS OPEN NOW")
    timtim = time.time()
    while time.time() - timtim < float(3.5): 1

k = 0
while(True):
    line = ser.readline().decode('ASCII')
    #line = line.split()
    timtim = time.time()
    while time.time() - timtim < float(0.5): 1
    msg = str(len(line.split())) + '\n'
    ser.write(bytes(msg, encoding="ASCII"))
    timtim = time.time()
    while time.time() - timtim < float(.5): 1
    msg = line + '\n'
    ser.write(bytes(msg, encoding="ASCII"))
    ser.flush()
    #ser.write(bytes('5', encoding="ASCII"))
    #ser.write(bytes("-11350000 535022 -11351000 5351000 56789 ", encoding="ASCII"))
    k += 1
    print(line)
    print("OK THAT ONE WENT THROUGH")
    if k == 4:
        while 1: 1
