#!/usr/bin/env python3

import sys
import serial


def compile_gcode(source_lines: str) -> bytes:
    compiled_bytes = b''


    return compiled_bytes


def main():
    # Check args
    if len(sys.argv) != 3:
        print(f"USAGE: {sys.argv[0]} input.gcode SERIALDEV")

    # Read source file
    try:
        f = open(sys.argv[1])
        lines = f.read()
    except Exception as e:
        print(f"Could not read the source file: {e}")
        exit(1)
    
    # Try to open seril device 
    try:
        ser = serial.Serial(sys.argv[2])
    except Exception as e:
        print(f"Could not open serial device: {e}")
        exit(1)

    # Compile source
    try:
        compiled_bytes = compile_gcode(lines)
    except Exception as e:
        print(f"An error occurred during compilation: {e}")
        exit(1)

    # Silently exit if there is nothing to write
    if (len(compiled_bytes) == 0):
        exit(0)

    # try to write to the serial device
    try:
        ser.write(compiled_bytes)
    except Exception as e:
        printf(f"Could not write to serial device: {e}")
        exit(1)

    print(f"Successfully wrote {len(compiled_bytes)} to {sys.argv[2]}")


if __name__ == '__main__':
    main()
