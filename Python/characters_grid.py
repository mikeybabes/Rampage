import sys
from PIL import Image

def read_palette(palette_path):
    with open(palette_path, "rb") as f:
        pal_data = f.read()
    if len(pal_data) < 48:
        raise ValueError("Palette file is too small (should be at least 48 bytes for 16 RGB entries).")
    palette = []
    for i in range(16):
        r = pal_data[i*3 + 0]
        g = pal_data[i*3 + 1]
        b = pal_data[i*3 + 2]
        palette += [r, g, b]
    # Pad to 256 colors (Photoshop expects a 256-entry palette)
    palette += [0, 0, 0] * (256 - 16)
    return palette

def get_pixel(tile_bytes, x, y):
    # tile_bytes: 32 bytes, 8x8 tile, 2 pixels/byte, row-major
    index = y * 4 + (x // 2)
    b = tile_bytes[index]
    if x % 2 == 0:
        return (b >> 4) & 0xF
    else:
        return b & 0xF

def main(char_fn, pal_fn, out_fn, width=32):
    with open(char_fn, "rb") as f:
        char_data = f.read()
    num_tiles = len(char_data) // 32
    height = (num_tiles + width - 1) // width

    img = Image.new("P", (width * 8, height * 8))
    palette = read_palette(pal_fn)
    img.putpalette(palette)

    for t in range(num_tiles):
        tile_bytes = char_data[t*32:(t+1)*32]
        tx, ty = t % width, t // width
        for y in range(8):
            for x in range(8):
                cidx = get_pixel(tile_bytes, x, y)
                img.putpixel((tx*8 + x, ty*8 + y), cidx)
    img.save(out_fn, format="PNG")
    print(f"Wrote {out_fn} ({img.width}x{img.height}) showing {num_tiles} tiles.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Quick viewer for all 8x8 character tiles as indexed PNG.")
    parser.add_argument("characters", help="characters.bin (4bpp, 8x8, 32 bytes/tile)")
    parser.add_argument("palette", help="palette.bin (16*3=48 bytes, one RGB palette)")
    parser.add_argument("output", help="output PNG filename")
    parser.add_argument("--width", type=int, default=32, help="Tiles per row (default 32)")
    args = parser.parse_args()
    main(args.characters, args.palette, args.output, args.width)
