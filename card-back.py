import os
import sys
import io
from PIL import Image, ImageDraw, ImageFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OUTPUT_DIR = "C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards-final-v3"

# Card dimensions (same as front)
CARD_W, CARD_H = 488, 680

# Color scheme
PRIMARY = (15, 20, 30)
ACCENT = (0, 180, 220)
DARK = (8, 12, 18)

def get_font(size, bold=False):
    if bold:
        font_paths = ["C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc"]
    else:
        font_paths = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/msyhbd.ttc"]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except:
                continue
    return ImageFont.load_default()

def render_card_back():
    # Create card background
    card = Image.new('RGB', (CARD_W, CARD_H), PRIMARY)
    draw = ImageDraw.Draw(card)

    # Outer frame
    draw.rounded_rectangle([0, 0, CARD_W-1, CARD_H-1], radius=16, fill=None, outline=ACCENT, width=3)

    # Inner frame
    draw.rounded_rectangle([8, 8, CARD_W-9, CARD_H-9], radius=12, fill=DARK, outline=ACCENT, width=1)

    # Central design area
    center_x, center_y = CARD_W // 2, CARD_H // 2

    # Draw concentric circles (mystical design)
    for r in range(180, 20, -30):
        alpha = int(50 * (1 - r / 180))
        color = (ACCENT[0], ACCENT[1], ACCENT[2])
        draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], 
                     fill=None, outline=color, width=2)

    # Central hexagon design
    import math
    hex_points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        x = center_x + 80 * math.cos(angle)
        y = center_y + 80 * math.sin(angle)
        hex_points.append((x, y))
    draw.polygon(hex_points, fill=None, outline=ACCENT, width=3)

    # Inner hexagon
    inner_hex = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        x = center_x + 50 * math.cos(angle)
        y = center_y + 50 * math.sin(angle)
        inner_hex.append((x, y))
    draw.polygon(inner_hex, fill=None, outline=ACCENT, width=2)

    # Central symbol
    draw.ellipse([center_x - 25, center_y - 25, center_x + 25, center_y + 25], 
                 fill=ACCENT, outline=(255, 255, 255), width=2)

    # Draw star in center
    star_points = []
    for i in range(5):
        angle = math.radians(72 * i - 90)
        x = center_x + 15 * math.cos(angle)
        y = center_y + 15 * math.sin(angle)
        star_points.append((x, y))
        angle2 = math.radians(72 * i + 36 - 90)
        x2 = center_x + 7 * math.cos(angle2)
        y2 = center_y + 7 * math.sin(angle2)
        star_points.append((x2, y2))
    draw.polygon(star_points, fill=(255, 255, 255))

    # Decorative lines from center
    for i in range(8):
        angle = math.radians(45 * i)
        x1 = center_x + 30 * math.cos(angle)
        y1 = center_y + 30 * math.sin(angle)
        x2 = center_x + 120 * math.cos(angle)
        y2 = center_y + 120 * math.sin(angle)
        draw.line([(x1, y1), (x2, y2)], fill=ACCENT, width=1)

    # Corner decorations
    corner_size = 60
    corners = [(20, 20), (CARD_W - 20 - corner_size, 20), 
               (20, CARD_H - 20 - corner_size), (CARD_W - 20 - corner_size, CARD_H - 20 - corner_size)]
    
    for cx, cy in corners:
        draw.rounded_rectangle([cx, cy, cx + corner_size, cy + corner_size], 
                              radius=8, fill=None, outline=ACCENT, width=2)

    # Top text
    font_title = get_font(24, bold=True)
    title = "SDV TCG"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((CARD_W - tw) // 2, 30), title, fill=ACCENT, font=font_title)

    # Bottom text
    font_subtitle = get_font(14)
    subtitle = "斯特拉達·維爾索"
    bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    tw = bbox[2] - bbox[0]
    draw.text(((CARD_W - tw) // 2, CARD_H - 50), subtitle, fill=ACCENT, font=font_subtitle)

    # Version text
    font_version = get_font(10)
    version = "v1.0"
    bbox = draw.textbbox((0, 0), version, font=font_version)
    tw = bbox[2] - bbox[0]
    draw.text(((CARD_W - tw) // 2, CARD_H - 30), version, fill=(100, 100, 100), font=font_version)

    return card

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate card back
    card_back = render_card_back()
    output_path = os.path.join(OUTPUT_DIR, "card_back.png")
    card_back.save(output_path, "PNG")
    print(f"Saved card back: {output_path}")

if __name__ == "__main__":
    main()
