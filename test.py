#!/usr/bin/env python3

import serial
import os
import sys

# These files should transpile successfully and produce the following output
good_gcode_files = ['spacing.gcode', 'negative_nums.gcode']
good_gcode_bytes = [b'\x80<\x94\x06\x06\x06\x80\x14\x14', b'\x80T\x94\x06']

# These files should error 
bad_gcode_files = ['bad-args.gcode']

def main():
    if len(sys.argv) != 4:
        print(f"USAGE: {sys.argv[0]} <input serial> <output serial> <gcode example path>")
        exit(1)

    input_ser = serial.Serial(sys.argv[1], timeout=1)


    print("Trying to run correct files")
    for i in range(len(good_gcode_files)):
        file = good_gcode_files[i]
        ans = good_gcode_bytes[i]
        os.system(os.getcwd() + "/transpiler.py " + sys.argv[3] + "/" + file + " " + sys.argv[2] + " >/dev/null 2>&1")

        read_bytes = b''
        buf = b':P'

        while buf:
            buf = input_ser.read(10)
            read_bytes += buf

        if read_bytes == ans:
            print(f"{file}: PASS")
        else:
            print(f"{file}: FAIL")

    print("\n-----------\nRunning files with errors, a PASS indicates the file did not compile")
    for i in range(len(bad_gcode_files)):
        file = bad_gcode_files[i]
        os.system(os.getcwd() + "/transpiler.py " + sys.argv[3] + "/" + file + " " + sys.argv[2] + " >/dev/null 2>&1")

        read_bytes = b''
        buf = b':P'

        while buf:
            buf = input_ser.read(10)
            read_bytes += buf

        if len(read_bytes) == 0:
            print(f"{file}: PASS")
        else:
            print(f"{file}: FAIL")

if __name__ == '__main__':
    main()
