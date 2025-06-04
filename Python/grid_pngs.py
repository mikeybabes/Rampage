import os
import math
import sys
import re
from PIL import Image, ImageDraw, ImageFont

def extract_level_number(filename):
    m = re.search(r'(\d+)', filename)
    if m:
        return m.group(1)
    return ""

def draw_level_number(img, number):
    draw = ImageDraw.Draw(img)
    w, _ = img.size
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except IOError:
        font = ImageFont.load_default()
    # Convert to int to remove leading zeros if number is numeric
    text = str(int(number)) if number.isdigit() else str(number)

    # Robust text sizing: try textbbox (Pillow >=8.0.0), else font.getsize
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except AttributeError:
        tw, th = font.getsize(text)

    tx = (w - tw) // 2
    ty = 8
    # Draw black outline (corners)
    for dx in (-1, 1):
        for dy in (-1, 1):
            draw.text((tx+dx, ty+dy), text, font=font, fill='black')
    # Draw white text
    draw.text((tx, ty), text, font=font, fill='white')

def draw_grid_lines(img, across, rows, img_w, img_h):
    draw = ImageDraw.Draw(img)
    # Draw vertical lines
    for i in range(1, across):
        x = i * img_w
        draw.line([(x, 0), (x, img.size[1]-1)], fill="white", width=1)
    # Draw horizontal lines
    for i in range(1, rows):
        y = i * img_h
        draw.line([(0, y), (img.size[0]-1, y)], fill="white", width=1)

def main(folder, output, across=15, show_number=False, show_grid=False):
    files = sorted([f for f in os.listdir(folder) if f.lower().endswith('.png')])
    if not files:
        print("No PNG files found in", folder)
        return

    img_w, img_h = 250, 240
    total = len(files)
    rows = math.ceil(total / across)
    grid_w = across * img_w
    grid_h = rows * img_h

    print(f"Combining {total} images ({across} across, {rows} down) into {grid_w}x{grid_h} PNG.")

    grid_img = Image.new('RGBA', (grid_w, grid_h), (0, 0, 0, 255))

    for idx, fname in enumerate(files):
        x = (idx % across) * img_w
        y = (idx // across) * img_h
        im = Image.open(os.path.join(folder, fname)).convert('RGBA')
        if show_number:
            level_number = extract_level_number(fname)
            draw_level_number(im, level_number)
        grid_img.paste(im, (x, y))
        im.close()

    if show_grid:
        draw_grid_lines(grid_img, across, rows, img_w, img_h)

    grid_img.save(output)
    print("Saved:", output)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Arrange PNGs in a grid, with options for level numbers and a grid overlay.")
    parser.add_argument('folder', help='Folder with PNG files')
    parser.add_argument('output', help='Output PNG filename')
    parser.add_argument('--across', type=int, default=15, help='How many images across per row (default 15)')
    parser.add_argument('--number', action='store_true', help='Overlay level numbers extracted from filenames')
    parser.add_argument('--grid', action='store_true', help='Draw a white grid between images')
    args = parser.parse_args()
    main(args.folder, args.output, args.across, args.number, args.grid)
