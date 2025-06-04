#!/usr/bin/env python3
import sys

def reverse_nibble(n):
    """Reverse the bit order of a 4-bit nibble.
       For example, 0b1010 becomes 0b0101.
    """
    return ((n & 1) << 3) | ((n & 2) << 1) | ((n & 4) >> 1) | ((n & 8) >> 3)

def swap_nybbles(infile, outfile, xor_val=0):
    data = infile.read()
    output = bytearray()
    for byte in data:
        # Extract the upper and lower 4-bit nybbles.
        top = (byte >> 4) & 0xF
        bottom = byte & 0xF
        # Reverse the bit order of each nibble.
        top_reversed = reverse_nibble(top)
        bottom_reversed = reverse_nibble(bottom)
        # Combine the reversed nybbles into one byte.
        new_byte = (top_reversed << 4) | bottom_reversed
        # Optionally XOR the result with the provided xor_val.
        new_byte ^= xor_val
        output.append(new_byte)
    outfile.write(output)

if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        sys.exit("Usage: python swap_nybble.py input.bin output.bin [xor_hex_value]")
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    xor_val = 0
    if len(sys.argv) == 4:
        try:
            xor_val = int(sys.argv[3], 16)
        except Exception as e:
            sys.exit("Error: Invalid XOR hex value. Please supply a valid hexadecimal number.")
    
    with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
        swap_nybbles(fin, fout, xor_val)

