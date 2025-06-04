# Updated script with fixed table offset, fixed count, and explicit reversed column list

import argparse
from PIL import Image, ImageDraw, ImageFont

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
                if c != 0:
                    dst_x = 31 - xx if flip_x else xx
                    px[dst_x, yy] = (*palette[c], 255)
    return img

def read_table_entry(rom_data, offset):
    e = rom_data[offset:offset+6]
    return list(e[2:6])

def compose_block(sprites, palette, ids, flip_flags):
    block = Image.new('RGBA', (64, 64), (0,0,0,0))
    positions = [(0,0), (32,0), (0,32), (32,32)]  # TL, TR, BL, BR
    for sid, pos, flip in zip(ids, positions, flip_flags):
        img = decode_tile32(sprites, palette, sid, flip_x=flip)
        block.paste(img, pos, img)
    return block

def main():
    parser = argparse.ArgumentParser(description="Rampage character strip with controlled X-flip logic")
    parser.add_argument('rom_file')
    parser.add_argument('sprites_file')
    parser.add_argument('palette_file')
    parser.add_argument('output_png')
    args = parser.parse_args()

    table_offset = 0x290D
    count = 68
    reversed_columns = {1,3,5,7,9,11,13,14,17,18,21,23,25,27,29,31,33,35,37,39,41,43,47,49,51,53,55,57,59,60,63,65,67}

    rom     = open(args.rom_file, 'rb').read()
    sprites = open(args.sprites_file, 'rb').read()
    palette = read_palette(args.palette_file)

    variants = [[], [], []]
    offsets = []

    for i in range(count):
        off = table_offset + i*6
        base_ids = read_table_entry(rom, off)

        # Flip condition only if column is in list
        flip_flags = [True]*4 if i in reversed_columns else [False]*4

        for v_offset, row in [(0,0), (0x100,1), (0x180,2)]:
            ids = [sid + v_offset for sid in base_ids]
            block = compose_block(sprites, palette, ids, flip_flags)
            variants[row].append(block)

        offsets.append(off)

    block_size = 64
    cols = count
    text_h = 12
    W = cols * block_size
    H = 3 * block_size + text_h

    out = Image.new('RGBA', (W, H), (255,255,255,255))
    draw = ImageDraw.Draw(out)
    font = ImageFont.load_default()

    # Paste blocks
    for row in range(3):
        for col in range(cols):
            x, y = col*block_size, row*block_size
            out.paste(variants[row][col], (x,y), variants[row][col])

    # Draw labels
    for col, off in enumerate(offsets):
        text = f"{col} {off:04X}"
        bbox = draw.textbbox((0,0), text, font=font)
        w = bbox[2] - bbox[0]
        dx = col*block_size + (block_size - w)//2
        draw.text((dx, 3*block_size), text, fill='black', font=font)

    out.save(args.output_png)
    print(f"Saved 68-strip sprite sheet with controlled X-flip to {args.output_png}")

if __name__ == '__main__':
    main()
