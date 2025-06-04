from PIL import Image

def read_palette(palette_path):
    with open(palette_path, "rb") as f:
        pal_data = f.read()

    num_entries = len(pal_data) // 3
    if num_entries < 64:
        raise ValueError(f"Palette file too small: {num_entries} colors (need at least 64 for 4 palettes)")

    palette = []
    for i in range(num_entries):
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
    palette = 3 - ((word >> 12) & 0x03)  # REVERSED as we discover the palettes are reversed in storage.
    return code, yflip, xflip, palette

def main(char_fn, pal_fn, map_fn, width, direction, out_fn):
    with open(char_fn, "rb") as f:
        char_data = f.read()
    num_chars = len(char_data) // 32

    palette = read_palette(pal_fn)

    with open(map_fn, "rb") as f:
        map_data = f.read()
    num_tiles = len(map_data) // 2
    height = (num_tiles + width - 1) // width

    img = Image.new("RGB", (width * 8, height * 8))

    def map_index(ix, iy):
        return iy * width + ix if direction == "top" else (height - 1 - iy) * width + ix

    for iy in range(height):
        for ix in range(width):
            tile_idx = map_index(ix, iy)
            if tile_idx >= num_tiles:
                continue
            word = map_data[tile_idx * 2] | (map_data[tile_idx * 2 + 1] << 8)
            code, yflip, xflip, palette_idx = parse_tile_entry(word)

            if code >= num_chars:
                tile_bytes = bytes([0] * 32)
            else:
                tile_bytes = char_data[code * 32:(code + 1) * 32]

            for ty in range(8):
                for tx in range(8):
                    cidx = get_pixel(tile_bytes, tx, ty, xflip, yflip)
                    color_index = palette_idx * 16 + cidx
                    rgb = palette[color_index] if color_index < len(palette) else (255, 0, 255)
                    img.putpixel((ix * 8 + tx, iy * 8 + ty), rgb)

    img.save(out_fn)
    print(f"Wrote {out_fn} with palette fix (192-byte palette, inverted index)")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Rampage/MCR3 tilemap plotter with palette inversion fix.")
    parser.add_argument("characters", help="characters.bin (4bpp, 8x8 tiles, 32 bytes/tile)")
    parser.add_argument("palette", help="palette.bin (192 bytes: 4 palettes of 16 RGB triples)")
    parser.add_argument("map", help="map_data.bin (2 bytes/tile, Rampage format)")
    parser.add_argument("output", help="Output PNG filename")
    parser.add_argument("--width", type=int, default=32, help="Tiles per row (default 32)")
    parser.add_argument("--direction", choices=["top", "bottom"], default="top",
                        help="First map entry is top row (default) or bottom row")
    args = parser.parse_args()
    main(args.characters, args.palette, args.map, args.width, args.direction, args.output)
