import sys

def merge_binaries(file1, file2, file3, file4, output_file):
    try:
        # Open all the input binary files and the output binary file
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2, open(file3, 'rb') as f3, open(file4, 'rb') as f4, open(output_file, 'wb') as out:
            # Loop over each byte in the input files
            while True:
                # Read one byte from each file
                b1 = f1.read(1)
                b2 = f2.read(1)
                b3 = f3.read(1)
                b4 = f4.read(1)
                
                # If we've reached the end of any file, stop merging
                if not b1 or not b2 or not b3 or not b4:
                    break

                # Write one byte from each file to the output file
                out.write(b1)
                out.write(b2)
                out.write(b3)
                out.write(b4)

        print(f"Merged files into {output_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Ensure the correct number of arguments are passed
    if len(sys.argv) != 6:
        print("Usage: python merge_binaries.py <file1> <file2> <file3> <file4> <output_file>")
        sys.exit(1)
    
    # Get the file names from the command line arguments
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    file3 = sys.argv[3]
    file4 = sys.argv[4]
    output_file = sys.argv[5]
    
    # Merge the binary files
    merge_binaries(file1, file2, file3, file4, output_file)
