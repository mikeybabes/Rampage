#!/usr/bin/env python3
import sys

def merge_bitplanes(file1, file2, outfile):
    # Read the entire contents of both input files.
    data1 = file1.read()
    data2 = file2.read()

    if len(data1) != len(data2):
        sys.exit("Error: Input files must have the same length.")

    out_bytes = bytearray()
    
    # Each input byte encodes 4 pixels, with 2 bits per pixel.
    # We process each corresponding pair of bytes.
    # For each of the 4 pixels:
    #   pixel1 = (data1_byte >> (6 - 2*j)) & 0x03  (j = 0,1,2,3)
    #   pixel2 = (data2_byte >> (6 - 2*j)) & 0x03
    #   merged_pixel = (pixel2 << 2) | pixel1
    # Since each merged pixel is 4 bits, pack 2 pixels per output byte.
    for b1, b2 in zip(data1, data2):
        merged_pixels = []
        for j in range(4):
            shift = 6 - (j * 2)
            pixel1 = (b1 >> shift) & 0x03
            pixel2 = (b2 >> shift) & 0x03
            merged = (pixel2 << 2) | pixel1
            merged_pixels.append(merged)
        
        # Pack the 4 merged pixels (each 4 bits) into 2 bytes:
        # First output byte: merged_pixels[0] in high nibble, merged_pixels[1] in low nibble.
        # Second output byte: merged_pixels[2] in high nibble, merged_pixels[3] in low nibble.
        out_byte1 = (merged_pixels[0] << 4) | merged_pixels[1]
        out_byte2 = (merged_pixels[2] << 4) | merged_pixels[3]
        out_bytes.append(out_byte1)
        out_bytes.append(out_byte2)
    
    outfile.write(out_bytes)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit("Usage: python merge2bits.py input1.bin input2.bin output.bin")

    input1_path = sys.argv[1]
    input2_path = sys.argv[2]
    output_path = sys.argv[3]

    with open(input1_path, "rb") as f1, open(input2_path, "rb") as f2, open(output_path, "wb") as outf:
        merge_bitplanes(f1, f2, outf)
