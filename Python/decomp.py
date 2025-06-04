import sys

def decode_character_data(data, base_offset):
    """
    Decode compressed character data and return (output_bytes, end_offset).
    """
    i = 0
    out = []

    while i < len(data):
        control = data[i]
        i += 1

        if control == 0x00:
            break  # End of data

        if control & 0x80:
            count = control & 0x7F
            for _ in range(count):
                if i + 1 >= len(data):
                    break
                lo = data[i]
                hi = data[i + 1] & 0x3F
                out.append(lo)
                out.append(hi)
                i += 2
        else:
            count = control
            if i + 1 >= len(data):
                break
            lo = data[i]
            hi = data[i + 1] & 0x3F
            i += 2
            out.extend([lo, hi] * count)

    end_offset = base_offset + i
    return bytes(out), end_offset


def main():
    if len(sys.argv) != 4:
        print("Usage: python decomp.py input.bin output.bin offset")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    offset_str = sys.argv[3]

    try:
        offset = int(offset_str, 16)
    except ValueError:
        print("Invalid hex offset:", offset_str)
        return

    with open(input_file, "rb") as f:
        f.seek(offset)
        raw = f.read()

    decoded, end_offset = decode_character_data(raw, offset)

    with open(output_file, "wb") as f:
        f.write(decoded)

    print(f"✅ Decoded {len(decoded)} bytes to {output_file}")
    print(f"🧭 Compressed data ended at offset: ${end_offset:04X}")

if __name__ == "__main__":
    main()
