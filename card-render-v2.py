import json
import re
import os
import sys
import io
from PIL import Image, ImageDraw, ImageFont
import textwrap

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CARDS_JSON = "C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json"
DECK_DIR = "C:/Users/layja/obsidian/worldbuilding/card-game"
IMG_DIR = "C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/img-ai-v2"
OUTPUT_DIR = "C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards-final-v2"

# Card dimensions (MTG-like ratio)
CARD_W, CARD_H = 488, 680
ART_W, ART_H = 430, 300
ART_X, ART_Y = 29, 55

# Faction colors (MTG-style gradients)
FACTION_COLORS = {
    "pa": {
        "primary": (30, 60, 90),
        "secondary": (20, 40, 60),
        "accent": (0, 180, 220),
        "frame": (40, 80, 120),
        "name": "實驗體",
        "symbol": "S",
    },
    "pb": {
        "primary": (90, 20, 20),
        "secondary": (60, 15, 15),
        "accent": (200, 50, 50),
        "frame": (120, 30, 30),
        "name": "認知科學局",
        "symbol": "C",
    },
    "pc": {
        "primary": (90, 70, 20),
        "secondary": (60, 45, 15),
        "accent": (220, 180, 50),
        "frame": (140, 110, 30),
        "name": "回聖會",
        "symbol": "R",
    },
    "pd": {
        "primary": (20, 70, 30),
        "secondary": (15, 50, 20),
        "accent": (50, 180, 80),
        "frame": (40, 100, 50),
        "name": "歸獸者",
        "symbol": "B",
    },
}

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

def parse_deck_file(filepath):
    cards = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    creature_pattern = r'\|\s*(\d+)\s*\|\s*\*\*(.+?)\*\*\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|'
    for match in re.finditer(creature_pattern, content):
        num, name, cost, atk, hp, effect = match.groups()
        card_id = None
        for cid, cdata in json.load(open(CARDS_JSON, 'r', encoding='utf-8')).items():
            if cdata['name'] == name.strip():
                card_id = cid
                break
        if card_id:
            cards[card_id] = {
                'id': card_id,
                'name': name.strip(),
                'type': '生物',
                'cost': int(cost),
                'atk': int(atk),
                'hp': int(hp),
                'effect': effect.strip().replace('**', ''),
            }

    spell_pattern = r'\|\s*(\d+)\s*\|\s*\*\*(.+?)\*\*\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|'
    for match in re.finditer(spell_pattern, content):
        num, name, cost, effect = match.groups()
        card_id = None
        for cid, cdata in json.load(open(CARDS_JSON, 'r', encoding='utf-8')).items():
            if cdata['name'] == name.strip():
                card_id = cid
                break
        if card_id and card_id not in cards:
            cards[card_id] = {
                'id': card_id,
                'name': name.strip(),
                'type': '法術',
                'cost': int(cost),
                'effect': effect.strip().replace('**', ''),
            }

    return cards

def load_all_cards():
    all_cards = {}
    deck_files = [
        "預組A-主角組·觀測之眼.md",
        "預組B-清理組·暗紅色者.md",
        "預組C-回聖會·先知之歌.md",
        "預組D-歸獸者·野性本能.md",
    ]
    for df in deck_files:
        path = os.path.join(DECK_DIR, df)
        if os.path.exists(path):
            cards = parse_deck_file(path)
            all_cards.update(cards)
    return all_cards

def get_faction(card_id):
    prefix = card_id.split('_')[0]
    return prefix, FACTION_COLORS.get(prefix, FACTION_COLORS["pa"])

def draw_gradient_rect(draw, bbox, color1, color2, direction='vertical'):
    x0, y0, x1, y1 = bbox
    if direction == 'vertical':
        for y in range(y0, y1):
            ratio = (y - y0) / max(1, (y1 - y0))
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            draw.line([(x0, y), (x1, y)], fill=(r, g, b))
    else:
        for x in range(x0, x1):
            ratio = (x - x0) / max(1, (x1 - x0))
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            draw.line([(x, y0), (x, y1)], fill=(r, g, b))

def render_card(card_data):
    card_id = card_data['id']
    prefix, faction = get_faction(card_id)

    # Create card background
    card = Image.new('RGB', (CARD_W, CARD_H), faction['secondary'])
    draw = ImageDraw.Draw(card)

    # Draw frame border
    draw.rounded_rectangle([0, 0, CARD_W-1, CARD_H-1], radius=12, fill=None, outline=faction['accent'], width=2)

    # Inner frame background
    draw.rounded_rectangle([4, 4, CARD_W-5, CARD_H-5], radius=10, fill=faction['primary'], outline=None)

    # Name bar (top left) - MTG style
    name_bar_w = 300
    draw.rounded_rectangle([8, 8, 8 + name_bar_w, 42], radius=6, fill=faction['frame'])
    draw.rounded_rectangle([8, 8, 8 + name_bar_w, 42], radius=6, fill=None, outline=faction['accent'], width=1)

    # Cost symbol (top right) - like MTG mana symbols
    cost = card_data['cost']
    cost_x, cost_y = CARD_W - 35, 25
    draw.ellipse([cost_x - 20, cost_y - 20, cost_x + 20, cost_y + 20], fill=faction['accent'], outline=(255, 255, 255), width=2)
    font_cost = get_font(22, bold=True)
    cost_text = str(cost)
    bbox = draw.textbbox((0, 0), cost_text, font=font_cost)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cost_x - tw//2, cost_y - th//2 - 1), cost_text, fill=(255, 255, 255), font=font_cost)

    # Card name
    name = card_data['name']
    font_name = get_font(18, bold=True)
    if len(name) > 16:
        name = name[:15] + "..."
    draw.text((15, 12), name, fill=(255, 255, 255), font=font_name)

    # Art area background
    art_bg_y = 48
    draw.rounded_rectangle([ART_X-3, art_bg_y, ART_X+ART_W+3, art_bg_y+ART_H+6], radius=8, fill=(10, 10, 15))

    # Load and paste artwork
    img_path = os.path.join(IMG_DIR, f"{card_id}.png")
    if os.path.exists(img_path):
        art = Image.open(img_path).resize((ART_W, ART_H), Image.LANCZOS)
        card.paste(art, (ART_X, art_bg_y + 3))

    # Art border
    draw.rounded_rectangle([ART_X-1, art_bg_y+1, ART_X+ART_W+1, art_bg_y+ART_H+5], radius=6, fill=None, outline=faction['accent'], width=1)

    # Type line (below art) - MTG style
    type_y = art_bg_y + ART_H + 12
    type_bar_h = 28
    draw.rounded_rectangle([ART_X-3, type_y, ART_X+ART_W+3, type_y + type_bar_h], radius=4, fill=faction['frame'])
    draw.rounded_rectangle([ART_X-3, type_y, ART_X+ART_W+3, type_y + type_bar_h], radius=4, fill=None, outline=faction['accent'], width=1)

    # Type text
    type_text = card_data['type']
    if card_data['type'] == '生物':
        type_text += f" — {card_data['atk']}/{card_data['hp']}"
    font_type = get_font(14, bold=True)
    bbox = draw.textbbox((0, 0), type_text, font=font_type)
    tw = bbox[2] - bbox[0]
    draw.text(((CARD_W - tw) // 2, type_y + 6), type_text, fill=(255, 255, 255), font=font_type)

    # Text box (below type) - MTG style
    text_box_y = type_y + type_bar_h + 8
    text_box_h = CARD_H - text_box_y - 45
    draw.rounded_rectangle([ART_X-3, text_box_y, ART_X+ART_W+3, text_box_y + text_box_h], radius=6, fill=(15, 15, 20))
    draw.rounded_rectangle([ART_X-3, text_box_y, ART_X+ART_W+3, text_box_y + text_box_h], radius=6, fill=None, outline=faction['accent'], width=1)

    # Effect text
    effect = card_data.get('effect', '')
    font_effect = get_font(12)
    effect_y = text_box_y + 8
    max_chars = 32
    lines = []
    for paragraph in effect.split('\n'):
        wrapped = textwrap.wrap(paragraph, width=max_chars)
        lines.extend(wrapped)

    for i, line in enumerate(lines[:8]):
        draw.text((ART_X + 5, effect_y + i * 16), line, fill=(200, 200, 200), font=font_effect)

    # Faction symbol (bottom left) - like MTG color indicator
    symbol_x = 25
    symbol_y = CARD_H - 30
    draw.ellipse([symbol_x - 12, symbol_y - 12, symbol_x + 12, symbol_y + 12], fill=faction['accent'], outline=(255, 255, 255), width=1)
    font_symbol = get_font(14, bold=True)
    draw.text((symbol_x - 5, symbol_y - 8), faction['symbol'], fill=(255, 255, 255), font=font_symbol)

    # Faction name (bottom center)
    faction_name = faction['name']
    font_faction = get_font(11)
    bbox = draw.textbbox((0, 0), faction_name, font=font_faction)
    tw = bbox[2] - bbox[0]
    draw.text(((CARD_W - tw) // 2, CARD_H - 28), faction_name, fill=faction['accent'], font=font_faction)

    # Card number (bottom right)
    card_num = card_id.split('_')[1]
    font_num = get_font(10)
    draw.text((CARD_W - 35, CARD_H - 26), f"#{card_num}", fill=(150, 150, 150), font=font_num)

    return card

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading card data...")
    all_cards = load_all_cards()
    print(f"Found {len(all_cards)} cards")

    generated = 0
    failed = 0

    for card_id, card_data in sorted(all_cards.items()):
        output_path = os.path.join(OUTPUT_DIR, f"{card_id}.png")

        if os.path.exists(output_path):
            print(f"SKIP: {card_id}")
            generated += 1
            continue

        try:
            card_img = render_card(card_data)
            card_img.save(output_path, "PNG")
            print(f"OK: {card_id} - {card_data['name']}")
            generated += 1
        except Exception as e:
            print(f"FAIL: {card_id} - {e}")
            failed += 1

    print(f"\nDone! Generated: {generated}, Failed: {failed}")

if __name__ == "__main__":
    main()
