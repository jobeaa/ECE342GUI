#!/usr/bin/env python3

import sys
import serial
import re

# Leave for now
DEBUG = True


CMD_M = 0 << 7
CMD_G = 1 << 7

ARG_X = 0 << 7
ARG_Y = 1 << 7


# Maps a command to a number of arguments that our arm will accept
cmd2nargs = {
    "G": {
        0: 2,
        1: 2,
        20: 0,
        21: 0,
        90: 0,
        91: 0
    },
    "M": {
        2: 0,
        6: 0,
        72: 0
    }
}


def compile_gcode(source_lines: str) -> bytes:
    compiled_bytes = b''
    line_num = 0

    for line in source_lines:
        line_num += 1

        # Get rid of whitespace and ignore case
        line = line.strip()
        line = re.sub(' +', ' ', line)
        line = line.upper()
    
        # ignore comments
        if len(line) == 0 or line[0] == '#':
            continue

        # Get the command type
        cmd_type = line[0]
        line = line[1:]

        # make sure this is a valid command (G or M)
        if not cmd_type in cmd2nargs:
            raise Exception(f"Line {line_num}: unrecognized command type")

        # Get the command number and make sure it's implemented
        args = line.split(' ')
        try:
            cmd_num = int(args[0])
        except:
            raise Exception(f"Line {line_num}: command number is not a number")

        if not cmd_num in cmd2nargs[cmd_type]:
            raise Exception(f"Line {line_num}: command has not been implemented")

        args.pop(0)

        # Make sure the right number of arguments are passed
        if len(args) != cmd2nargs[cmd_type][cmd_num]:
            raise Exception(f"Line {line_num}: command {cmd_type}{cmd_num} takes {cmd2nargs[cmd_type][cmd_num]} arguments but was passed {len(args)} arguments")

        # Build the byte representing the command
        if cmd_type == 'M':
            byte_to_push = CMD_M | cmd_num
        else:
            byte_to_push = CMD_G | cmd_num

        compiled_bytes += byte_to_push.to_bytes(1, byteorder="big")

        for arg in args:
            # Get axis and arg number
            axis = arg[0]
            arg = arg[1:]

            try:
                arg_number = int(arg)
            except:
                raise Exception(f"Line {line_num}: Argument is not a number")

            # Make sure the arg number is small enough
            arg_number_mag = abs(arg_number)

            if arg_number_mag > 63:
                raise Exception(f"Line {line_num}: Argument is too large (must be [-63, 63])")

            # convert to 7 bit signed int
            if arg_number < 0:
                arg_number = arg_number_mag | 1<<6

            # build arg byte
            if axis == 'X':
                byte_to_push = ARG_X | arg_number
            elif axis == 'Y':
                byte_to_push = ARG_Y | arg_number
            else:
                raise Exception(f"Line {line_num}: Invalid axis")


            compiled_bytes += byte_to_push.to_bytes(1, byteorder="big")

    return compiled_bytes


def main():
    # Check args
    if len(sys.argv) != 3:
        print(f"USAGE: {sys.argv[0]} input.gcode SERIALDEV")
        exit(1)

    # Read source file
    try:
        f = open(sys.argv[1])
        lines = f.readlines()
        f.close()
    except Exception as e:
        print(f"Could not read the source file: {e}")
        exit(1)
    
    # Try to open serial device 
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

    print(f"Successfully wrote {len(compiled_bytes)} bytes to {sys.argv[2]}")


if __name__ == '__main__':
    main()
