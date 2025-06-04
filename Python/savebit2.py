import sys

def savebit(input_filename, output_filename, hex_start_offset, hex_end_offset):
    # Convert hex start and end offsets to integers
    start_offset = int(hex_start_offset, 16)
    end_offset = int(hex_end_offset, 16)
    length = end_offset - start_offset + 1
    
    try:
        # Open the input file in binary mode and read the specified portion
        with open(input_filename, 'rb') as infile:
            infile.seek(start_offset)
            data = infile.read(length)
        
        # Write the read data to the output file
        with open(output_filename, 'wb') as outfile:
            outfile.write(data)
        
        print(f"Successfully saved {length} bytes from {input_filename} (offset {hex_start_offset}) to {output_filename}")
        print(f"Data saved from offset {hex(start_offset)} to {hex(end_offset)}")
    
    except FileNotFoundError:
        print(f"Error: File '{input_filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: savebit2.py <input_filename> <output_filename> <hex_start_offset> <hex_end_offset>")
    else:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
        hex_start_offset = sys.argv[3]
        hex_end_offset = sys.argv[4]
        savebit(input_filename, output_filename, hex_start_offset, hex_end_offset)
