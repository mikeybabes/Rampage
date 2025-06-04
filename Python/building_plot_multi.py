from PIL import Image
import argparse
import struct

def read_palette(palette_path):
    with open(palette_path, "rb") as f:
        pal_data = f.read()
    palette = []
    for i in range(len(pal_data) // 3):
        r = pal_data[i * 3 + 0]
        g = pal_data[i * 3 + 1]
        b = pal_data[i * 3 + 2]
        palette.append((r, g, b))
    return palette

def get_pixel(tile_bytes, x, y, xflip, yflip):
    if xflip: x = 7 - x
    if yflip: y = 7 - y
    index = y * 4 + (x // 2)
    b = tile_bytes[index]
    return (b >> 4) & 0xF if x % 2 == 0 else b & 0xF

def parse_tile_entry(word):
    code = (word & 0x03FF) | ((word >> 4) & 0x0400)
    xflip = (word >> 10) & 1
    yflip = (word >> 11) & 1
    palette = 3 - ((word >> 12) & 0x03)
    return code, yflip, xflip, palette

def plot_building(char_data, palette, building_data, out_png):
    width = building_data[0]
    height = building_data[1]
    high_byte = building_data[2]
    num_chars = len(char_data) // 32

    img = Image.new("RGB", (width * 8, height * 8))

    if high_byte == 0xFF:
        # Special case: 2-byte full words per tile
        expected_len = 3 + width * height * 2
        tile_data = building_data[3:]
        if len(tile_data) < width * height * 2:
            print(f"⚠️ Incomplete tile data in special case.")
            return
        for iy in range(height):
            for ix in range(width):
                tile_idx = (height - 1 - iy) * width + ix
                word = tile_data[tile_idx * 2] | (tile_data[tile_idx * 2 + 1] << 8)
                code, yflip, xflip, palette_idx = parse_tile_entry(word)
                tile_bytes = char_data[code * 32:(code + 1) * 32] if code < num_chars else bytes([0]*32)
                for ty in range(8):
                    for tx in range(8):
                        cidx = get_pixel(tile_bytes, tx, ty, xflip, yflip)
                        color_index = palette_idx * 16 + cidx
                        rgb = palette[color_index] if color_index < len(palette) else (255, 0, 255)
                        img.putpixel((ix * 8 + tx, iy * 8 + ty), rgb)
    else:
        # Common case: one byte per tile, use high_byte
        tile_data = building_data[3:3 + width * height]
        for iy in range(height):
            for ix in range(width):
                tile_idx = (height - 1 - iy) * width + ix
                tile_lo = tile_data[tile_idx]
                word = tile_lo | (high_byte << 8)
                code, yflip, xflip, palette_idx = parse_tile_entry(word)
                tile_bytes = char_data[code * 32:(code + 1) * 32] if code < num_chars else bytes([0]*32)
                for ty in range(8):
                    for tx in range(8):
                        cidx = get_pixel(tile_bytes, tx, ty, xflip, yflip)
                        color_index = palette_idx * 16 + cidx
                        rgb = palette[color_index] if color_index < len(palette) else (255, 0, 255)
                        img.putpixel((ix * 8 + tx, iy * 8 + ty), rgb)

    img.save(out_png)
    print(f"✅ Saved {out_png} ({width}x{height}){' [fullword]' if high_byte==0xFF else ''}")


def main():
    parser = argparse.ArgumentParser(description="Rampage multi-building plotter using pointer table")
    parser.add_argument("characters", help="characters.bin (4bpp tiles)")
    parser.add_argument("palette", help="palette.bin")
    parser.add_argument("map", help="building data binary (with offset table and building data)")
    parser.add_argument("offset", help="Hex offset to building offset table (e.g., 95B6)")
    parser.add_argument("output_prefix", help="Output filename prefix, e.g. building")
    parser.add_argument("--count", type=int, default=45, help="Number of buildings to extract (default 45)")
    args = parser.parse_args()

    # Parse hex offset
    table_offset = int(args.offset, 16)

    with open(args.map, "rb") as f:
        map_data = f.read()
    with open(args.characters, "rb") as f:
        char_data = f.read()
    palette = read_palette(args.palette)

    for i in range(args.count):
        entry_offset = table_offset + i * 2
        if entry_offset + 2 > len(map_data):
            print(f"❌ Table entry {i+1} out of bounds at {entry_offset:04X}")
            break

        # Read building offset (little endian)
        bld_offset = struct.unpack_from("<H", map_data, entry_offset)[0]

        if bld_offset + 3 > len(map_data):
            print(f"❌ Skipping building {i+1}: offset {bld_offset:04X} invalid")
            continue

        width = map_data[bld_offset]
        height = map_data[bld_offset + 1]
        high_byte = map_data[bld_offset + 2]

        if high_byte == 0xFF:
            size = 3 + (width * height * 2)
        else:
            size = 3 + (width * height)


        if bld_offset + size > len(map_data):
            print(f"❌ Skipping building {i+1}: incomplete data at offset {bld_offset:04X}")
            continue

        building_data = map_data[bld_offset : bld_offset + size]
        out_file = f"{args.output_prefix}_{i+1:02d}.png"
        plot_building(char_data, palette, building_data, out_file)

if __name__ == "__main__":
    main()
