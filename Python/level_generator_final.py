import struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse

"""
Rampage Arcade Level Plotter and Data Decoder
=============================================

Now with support for top two rows ("sky"/header) from packed data at $7613!

Each layer is plotted in this order:
    1. Background silhouette (rows 3–31)
    2. Top rows (rows 0–1, using packed data at $7613)
    3. Foliage
    4. Buildings
    5. Terrain strip (rows 29–30, always last)
"""

# Constants
LEVEL_TABLE_OFFSET = 0x8DAE
LEVEL_ENTRY_SIZE = 10
MAX_LEVELS = 132
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 240
CHAR_WIDTH = 8
CHAR_HEIGHT = 8

def load_characters(char_data):
    return [char_data[i:i+32] for i in range(0, len(char_data), 32)]

def load_palette(pal_data):
    return [(pal_data[i], pal_data[i+1], pal_data[i+2]) for i in range(0, len(pal_data), 3)]

def get_level_buildings(cpu_data, level):
    building_list = []
    entry_offset = LEVEL_TABLE_OFFSET + level * LEVEL_ENTRY_SIZE
    table_ptr = struct.unpack_from("<H", cpu_data, entry_offset)[0]
    background_number = (cpu_data[entry_offset + 2] & 0xF0) >> 4  # High nibble
    terrain_byte = cpu_data[entry_offset + 3]
    foliage_index = cpu_data[entry_offset + 4]
    ptr = table_ptr

    while ptr + 3 <= len(cpu_data):
        b0 = cpu_data[ptr]
        if b0 == 0xFF:
            break
        elif b0 in (0xFA, 0xFB, 0xFC, 0xFD):
            ptr += 2
            continue

        building_id = b0
        x_char = cpu_data[ptr + 1]
        palette_code = cpu_data[ptr + 2]
        building_list.append((building_id, x_char, palette_code))
        ptr += 3

    return background_number, terrain_byte, foliage_index, building_list

def get_pixel(tile_bytes, x, y, xflip, yflip):
    if xflip: x = 7 - x
    if yflip: y = 7 - y
    index = y * 4 + (x // 2)
    b = tile_bytes[index]
    return (b >> 4) & 0xF if x % 2 == 0 else b & 0xF

def decode_character_data(data):
    i = 0
    out = []
    while i < len(data):
        control = data[i]
        i += 1
        if control == 0x00:
            break
        if control & 0x80:
            count = control & 0x7F
            for _ in range(count):
                if i + 1 >= len(data): break
                out.extend([data[i], data[i+1] & 0x3F])
                i += 2
        else:
            count = control
            if i + 1 >= len(data): break
            lo, hi = data[i], data[i+1] & 0x3F
            i += 2
            out.extend([lo, hi] * count)
    return out

def decode_bottom_strip(cpu_data, terrain_byte):
    index = terrain_byte
    if index > 10:
        print(f"⚠️ Invalid terrain index {terrain_byte:02X}, skipping.")
        return []
    table_offset = 0x8928 + terrain_byte
    data_offset = struct.unpack_from("<H", cpu_data, table_offset)[0]
    print(f"🌍 Bottom terrain index {terrain_byte:02X} → offset ${data_offset:04X}")
    return decode_character_data(cpu_data[data_offset:])

def decode_background(cpu_data, background_number):
    index = background_number & 0x0F  # background_number already high nibble
    table_offset = 0x8934 + index
    data_offset = struct.unpack_from("<H", cpu_data, table_offset)[0]
    print(f"🎨 Background silhouette {index:02d} → offset ${data_offset:04X}")
    return decode_character_data(cpu_data[data_offset:])

def decode_top_strip(cpu_data):
    data_offset = 0x7613
    print(f"☁️ Decoding top rows (sky) from offset ${data_offset:04X}")
    return decode_character_data(cpu_data[data_offset:])

def plot_foliage(cpu_data, foliage_index, characters, palette, pixels):
    valid_indices = {0, 2, 4, 6, 8}
    if foliage_index not in valid_indices:
        print(f"🌲 Foliage index {foliage_index} not valid, skipping.")
        return

    table_offset = 0x95AA + foliage_index
    data_offset = struct.unpack_from("<H", cpu_data, table_offset)[0]
    if foliage_index > 4:
        rows = 2
        start_row = 27
    else:
        rows = 3
        start_row = 26

    print(f"🌲 Foliage index {foliage_index} → offset ${data_offset:04X}, rows={rows}, y={start_row}")

    for row in range(rows):
        for col in range(32):
            entry_off = data_offset + (row * 32 + col) * 2
            word = struct.unpack_from("<H", cpu_data, entry_off)[0]
            tile_index = (word & 0x03FF) | ((word >> 4) & 0x0400)
            flip_x = (word >> 10) & 1
            flip_y = (word >> 11) & 1
            palette_index = 3 - ((word >> 12) & 0x03)
            if tile_index >= len(characters): continue
            tile = characters[tile_index]
            tx = col
            ty = start_row + row
            for y in range(8):
                for x in range(8):
                    px = tx * 8 + x
                    py = (ty - 1) * 8 + y
                    if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
                        color_index = get_pixel(tile, x, y, flip_x, flip_y)
                        pixels[px, py] = palette[palette_index * 16 + color_index]

def plot_level(cpu_data, background_number, terrain_byte, foliage_index, buildings, characters, palette, output_file):
    image = Image.new("RGB", (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0))
    pixels = image.load()

    # 🎨 Background (rows 3–31)
    if buildings:
        bg_data = decode_background(cpu_data, background_number)
        for i in range(0, len(bg_data) & ~1, 2):
            lo, hi = bg_data[i], bg_data[i+1] & 0x3F
            word = lo | (hi << 8)
            tile_index = (word & 0x03FF) | ((word >> 4) & 0x0400)
            flip_x = (word >> 10) & 1
            flip_y = (word >> 11) & 1
            palette_index = 3 - ((word >> 12) & 0x03)
            if tile_index >= len(characters): continue
            tile = characters[tile_index]
            pos = i // 2
            tx = pos % 32
            ty = pos // 32 + 3
            for y in range(8):
                for x in range(8):
                    px = tx * 8 + x
                    py = (ty - 1) * 8 + y
                    if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
                        color_index = get_pixel(tile, x, y, flip_x, flip_y)
                        pixels[px, py] = palette[palette_index * 16 + color_index]

    # ☁️ Top rows (rows 0–1, RLE decoded)
    top_data = decode_top_strip(cpu_data)
    for pos in range(0, len(top_data), 2):
        lo, hi = top_data[pos], top_data[pos+1] & 0x3F
        word = lo | (hi << 8)
        tx = (pos // 2) % 32
        ty = (pos // 2) // 32  # 0 or 1
        tile_index = (word & 0x03FF) | ((word >> 4) & 0x0400)
        flip_x = (word >> 10) & 1
        flip_y = (word >> 11) & 1
        palette_index = 3 - ((word >> 12) & 0x03)
        if tile_index >= len(characters): continue
        tile = characters[tile_index]
        for y in range(8):
            for x in range(8):
                px = tx * 8 + x
                py = ty * 8 + y
                if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
                    color_index = get_pixel(tile, x, y, flip_x, flip_y)
                    pixels[px, py] = palette[palette_index * 16 + color_index]

    # 🌲 Foliage (before buildings)
    plot_foliage(cpu_data, foliage_index, characters, palette, pixels)

    # 🧱 Buildings
    print(f"\n🧱 Plotting {len(buildings)} buildings...")
    for building_id, x_char, palette_code in buildings:
        btable = 0x95B6
        bptr_offset = struct.unpack_from("<H", cpu_data, btable + (building_id - 1) * 2)[0]
        width = cpu_data[bptr_offset]
        height = cpu_data[bptr_offset + 1]
        mode = cpu_data[bptr_offset + 2]
        ptr = bptr_offset + 3
        palette_index = (palette_code & 0xF0) >> 4
        tile_palette = 3 - palette_index
        print(f"  ▶ Building ID {building_id:02d} @ ${bptr_offset:04X}: {width}x{height}, x_char={x_char}, palette={palette_code:02X} → index {tile_palette}")
        for y in range(height):
            for x in range(width):
                word = (struct.unpack_from("<H", cpu_data, ptr)[0] if mode == 0xFF
                        else (mode << 8) | cpu_data[ptr])
                ptr += 2 if mode == 0xFF else 1
                tile_index = (word & 0x03FF) | ((word >> 4) & 0x0400)
                flip_x = (word >> 10) & 1
                flip_y = (word >> 11) & 1
                if tile_index >= len(characters): continue
                tile = characters[tile_index]
                for ty in range(8):
                    for tx in range(8):
                        px = x_char * 4 + x * CHAR_WIDTH + tx
                        py = (28 - y - 1) * 8 + ty  # corrected
                        if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
                            color_index = get_pixel(tile, tx, ty, flip_x, flip_y)
                            pixels[px, py] = palette[tile_palette * 16 + color_index]

    # 🌍 Terrain strip (rows 29–30) -- PLOT LAST!
    strip_data = decode_bottom_strip(cpu_data, terrain_byte)
    for i in range(0, len(strip_data) & ~1, 2):
        lo, hi = strip_data[i], strip_data[i+1] & 0x3F
        word = lo | (hi << 8)
        tile_index = (word & 0x03FF) | ((word >> 4) & 0x0400)
        flip_x = (word >> 10) & 1
        flip_y = (word >> 11) & 1
        palette_index = 3 - ((word >> 12) & 0x03)
        if tile_index >= len(characters): continue
        tile = characters[tile_index]
        pos = i // 2
        tx = pos % 32
        ty = pos // 32 + 29
        for y in range(8):
            for x in range(8):
                px = tx * 8 + x
                py = (ty - 1) * 8 + y
                if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
                    color_index = get_pixel(tile, x, y, flip_x, flip_y)
                    pixels[px, py] = palette[palette_index * 16 + color_index]

    image.save(output_file)
    print(f"💾 Saved PNG to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cpu", help="cpu.bin")
    parser.add_argument("characters", help="background.bin")
    parser.add_argument("palette", help="palettes.pal")
    parser.add_argument("output", help="output filename base (no extension)")
    parser.add_argument("--level", type=int, default=None, help="single level number to process (1-based, 1–132)")
    parser.add_argument("--levels", type=int, default=None, help="number of levels to process (default: all found)")
    args = parser.parse_args()

    cpu = Path(args.cpu).read_bytes()
    chars = Path(args.characters).read_bytes()
    pals = Path(args.palette).read_bytes()
    tiles = load_characters(chars)
    palette = load_palette(pals)

    # Determine how many levels in total (hard cap at 132)
    detected_levels = (len(cpu) - LEVEL_TABLE_OFFSET) // LEVEL_ENTRY_SIZE
    total_levels = min(MAX_LEVELS, detected_levels)

    # Priority: --level > --levels > all
    if args.level is not None:
        if not (1 <= args.level <= total_levels):
            print(f"ERROR: --level must be between 1 and {total_levels} (inclusive).")
            exit(1)
        levels_to_do = [args.level - 1]  # Convert 1-based to 0-based
    elif args.levels is not None:
        levels_to_do = list(range(min(total_levels, args.levels)))
    else:
        levels_to_do = list(range(total_levels))

    for level in levels_to_do:
        background_number, terrain, foliage_index, buildings = get_level_buildings(cpu, level)
        shown_level = level + 1
        filename = f"{args.output}_{shown_level:03d}.png"  # filenames stay padded!
        display_level = str(int(f"{shown_level:03d}"))     # strip any leading zeros for display/print
        print(f"\n--- Generating level {display_level} to {filename} ---")
        plot_level(cpu, background_number, terrain, foliage_index, buildings, tiles, palette, filename)
