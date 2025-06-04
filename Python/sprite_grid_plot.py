from PIL import Image, ImageDraw, ImageFont

def read_palette(palette_path):
    with open(palette_path, "rb") as f:
        pal_data = f.read()
    palette = []
    for i in range(16):
        r = pal_data[i*3 + 0]
        g = pal_data[i*3 + 1]
        b = pal_data[i*3 + 2]
        palette += [r, g, b]
    palette += [0, 0, 0] * (256 - 16)
    return palette

def get_sprite_pixel(sprite_bytes, x, y):
    index = y * 16 + (x // 2)
    b = sprite_bytes[index]
    return (b >> 4) & 0xF if x % 2 == 0 else b & 0xF

def draw_grid_lines(draw, img_width, img_height, cell_size=32):
    for x in range(0, img_width, cell_size):
        draw.line([(x, 0), (x, img_height)], fill=(0, 0, 0))
    for y in range(0, img_height, cell_size):
        draw.line([(0, y), (img_width, y)], fill=(0, 0, 0))

def main(sprite_fn, palette_fn, out_fn, width=8, show_numbers=False, show_grid=False):
    with open(sprite_fn, "rb") as f:
        sprite_data = f.read()
    num_sprites = len(sprite_data) // 512
    height = (num_sprites + width - 1) // width

    img = Image.new("P", (width * 32, height * 32))
    palette = read_palette(palette_fn)
    img.putpalette(palette)

    for s in range(num_sprites):
        sprite_bytes = sprite_data[s*512:(s+1)*512]
        sx, sy = s % width, s // width
        base_x = sx * 32
        base_y = sy * 32
        for y in range(32):
            for x in range(32):
                cidx = get_sprite_pixel(sprite_bytes, x, y)
                img.putpixel((base_x + x, base_y + y), cidx)

    # Convert to RGB if either grid or numbers are needed
    if show_grid or show_numbers:
        rgb_img = img.convert("RGB")
        draw = ImageDraw.Draw(rgb_img)
        if show_grid:
            draw_grid_lines(draw, rgb_img.width, rgb_img.height)
        if show_numbers:
            font = ImageFont.load_default()
            for s in range(num_sprites):
                sx, sy = s % width, s // width
                base_x = sx * 32
                base_y = sy * 32
                label = f"{s:02X}"
                draw.text((base_x + 1, base_y + 1), label, fill=(255, 255, 255), font=font)
        rgb_img.save(out_fn, format="PNG")
    else:
        img.save(out_fn, format="PNG")

    print(f"Wrote {out_fn}: {num_sprites} sprites | grid: {'on' if show_grid else 'off'} | numbers: {'on' if show_numbers else 'off'}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Plot 32x32 4bpp sprites as indexed PNG.")
    parser.add_argument("sprites", help="sprites.bin (4bpp, 32x32, 512 bytes/sprite)")
    parser.add_argument("palette", help="palette.bin (48 bytes or more)")
    parser.add_argument("output", help="output PNG filename")
    parser.add_argument("--width", type=int, default=8, help="Sprites per row (default 8)")
    parser.add_argument("--number", action="store_true", help="Show sprite hex number in top-left")
    parser.add_argument("--grid", action="store_true", help="Draw black 1px grid between sprites")
    args = parser.parse_args()
    main(args.sprites, args.palette, args.output, args.width, args.number, args.grid)
