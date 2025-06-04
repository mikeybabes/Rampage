import sys
from PIL import Image, ImageDraw

def read_palette(pal_path):
    raw = open(pal_path, 'rb').read()
    return [tuple(raw[i*3:i*3+3]) for i in range(16)]

def get_pixel_4bpp(data, width, x, y):
    idx = y * (width // 2) + (x // 2)
    byte = data[idx]
    return (byte >> 4) & 0xF if x % 2 == 0 else byte & 0xF

def decode_tile32(sprite_data, palette, index, flip_x=False):
    tile_bytes_per = 32*32//2
    total_tiles = len(sprite_data) // tile_bytes_per
    img = Image.new('RGBA', (32, 32), (0,0,0,0))
    if 0 <= index < total_tiles:
        start = index * tile_bytes_per
        tile = sprite_data[start:start+tile_bytes_per]
        px = img.load()
        for yy in range(32):
            for xx in range(32):
                try:
                    c = get_pixel_4bpp(tile, 32, xx, yy)
                except IndexError:
                    c = 0
                dst_x = 31 - xx if flip_x else xx
                if c != 0:
                    px[dst_x, yy] = (*palette[c], 255)
                else:
                    px[dst_x, yy] = (0, 0, 0, 0)
    return img

def read_table_entry(rom_data, offset):
    e = rom_data[offset:offset+6]
    dx, dy = e[0], e[1]
    dx = dx - 256 if dx > 127 else dx
    dy = dy - 256 if dy > 127 else dy
    dy = -dy  # flip for bottom-up screen
    return dx, dy, list(e[2:6])

def compose_block(sprites, palette, ids, flip_flags):
    block = Image.new('RGBA', (64, 64), (0,0,0,0))
    positions = [(0,0), (32,0), (0,32), (32,32)]
    for sid, pos, flip in zip(ids, positions, flip_flags):
        img = decode_tile32(sprites, palette, sid, flip_x=flip)
        block.paste(img, pos, img)
    return block

def compose_full_sprite(rom, sprites, palette, col1, col2, mode):
    base_offset = 0x290D
    offset1 = base_offset + col1 * 6
    offset2 = base_offset + col2 * 6

    variants = []
    debug_info = []

    for variant_add in [0x000, 0x100, 0x180]:
        dx, dy, ids2 = read_table_entry(rom, offset2)
        _, _, ids1 = read_table_entry(rom, offset1)

        ids1 = [i + variant_add for i in ids1]
        ids2 = [i + variant_add for i in ids2]

        debug_info.append(f"Variant +{variant_add:03X}:")
        debug_info.append(f"  Base IDs : {ids1}")
        debug_info.append(f"  Head IDs : {ids2}")
        debug_info.append(f"  Offset   : dx={dx}, dy={dy}")
        debug_info.append("")

        block1 = compose_block(sprites, palette, ids1, [False]*4)
        block2 = compose_block(sprites, palette, ids2, [False]*4)

        dy_px = dy
        dx_px = dx

        min_w = max(64, 64 + abs(dx_px)) + 64 + 16
        min_h = max(128, 64 + abs(dy_px))

        canvas = Image.new('RGBA', (min_w, min_h), (0,0,0,0))
        y_base = min_h - 64

        if mode in ["both", "base"]:
            canvas.paste(block1, (16, y_base), block1)
        if mode in ["both", "head"]:
            canvas.paste(block2, (16 + dx_px, y_base - dy_px - 48), block2)

        variants.append(canvas)

    spacing = 8
    full_height = sum(v.height for v in variants) + spacing * 2
    full_width = max(v.width for v in variants)
    final_img = Image.new('RGBA', (full_width, full_height), (0,0,0,0))

    y = 0
    for v in variants:
        final_img.paste(v, (0, y), v)
        y += v.height + spacing

    return final_img, debug_info

def main():
    if len(sys.argv) < 6:
        print("Usage: python compose_rampage_overlay_pairs_space.py rom.bin sprites.bin palette.bin pairs.txt output.png [both|base|head] [--gapx 32] [--gapy 32]")
        return

    rom = open(sys.argv[1], 'rb').read()
    sprites = open(sys.argv[2], 'rb').read()
    palette = read_palette(sys.argv[3])
    pairs_file = sys.argv[4]
    output = sys.argv[5]
    mode = "both"
    gapx, gapy = 96, 8

    i = 6
    while i < len(sys.argv):
        if sys.argv[i] in ["both", "base", "head"]:
            mode = sys.argv[i]
        elif sys.argv[i] == "--gapx":
            i += 1
            gapx = int(sys.argv[i])
        elif sys.argv[i] == "--gapy":
            i += 1
            gapy = int(sys.argv[i])
        i += 1

    with open(pairs_file) as f:
        lines = [line.strip() for line in f if line.strip()]
        pairs = [tuple(map(int, line.split())) for line in lines]

    columns = []
    debug_output = []

    for idx, (col1, col2) in enumerate(pairs):
        img, debug = compose_full_sprite(rom, sprites, palette, col1, col2, mode)
        draw = ImageDraw.Draw(img)
        #draw.text((2, img.height - 5), f"{idx} {col1:04X} {col2:04X}", fill=(0,0,0,255))
        columns.append(img)
        debug_output.extend(debug)

    total_width = len(columns) * gapx
    max_height = max(im.height for im in columns) + gapy
    canvas = Image.new("RGBA", (total_width, max_height), (0,0,0,0))

    x = 0
    for img in columns:
        canvas.paste(img, (x, 0), img)
        x += gapx

    canvas.save(output)
    print(f"Saved: {output}")
    print("\n".join(debug_output))

if __name__ == "__main__":
    main()
