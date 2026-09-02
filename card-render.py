import json
import re
import os
import sys
import io
from PIL import Image, ImageDraw, ImageFont
import textwrap

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

CARDS_JSON = "C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json"
DECK_DIR = "C:/Users/layja/obsidian/worldbuilding/card-game"
IMG_DIR = "C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/img-ai-v2"
OUTPUT_DIR = "C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards-final"

# Card dimensions (standard TCG ratio ~5:7)
CARD_W, CARD_H = 500, 700
ART_W, ART_H = 440, 300
ART_X, ART_Y = 30, 80

# Faction colors
FACTION_COLORS = {
    "pa": {"primary": (40, 80, 120), "accent": (0, 180, 220), "name": "實驗體"},
    "pb": {"primary": (100, 20, 20), "accent": (200, 50, 50), "name": "認知科學局"},
    "pc": {"primary": (100, 80, 20), "accent": (220, 180, 50), "name": "回聖會"},
    "pd": {"primary": (30, 80, 40), "accent": (50, 180, 80), "name": "歸獸者"},
}

def parse_deck_file(filepath):
    cards = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse creature cards
    creature_pattern = r'\|\s*(\d+)\s*\|\s*\*\*(.+?)\*\*\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|'
    for match in re.finditer(creature_pattern, content):
        num, name, cost, atk, hp, effect = match.groups()
        card_id = None
        # Find card ID from name
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

    # Parse spell cards
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

def create_gradient(w, h, color1, color2, vertical=True):
    img = Image.new('RGB', (w, h))
    for i in range(h if vertical else w):
        ratio = i / (h if vertical else w)
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        if vertical:
            ImageDraw.Draw(img).line([(0, i), (w, i)], fill=(r, g, b))
        else:
            ImageDraw.Draw(img).line([(i, 0), (i, h)], fill=(r, g, b))
    return img

def draw_rounded_rect(draw, bbox, radius, fill, outline=None):
    x0, y0, x1, y1 = bbox
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline)

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

def render_card(card_data):
    card_id = card_data['id']
    prefix, faction = get_faction(card_id)

    card = Image.new('RGB', (CARD_W, CARD_H), (20, 20, 30))
    draw = ImageDraw.Draw(card)

    primary = faction['primary']
    accent = faction['accent']

    draw.rounded_rectangle([0, 0, CARD_W-1, CARD_H-1], radius=20, fill=None, outline=accent, width=3)
    draw.rounded_rectangle([8, 8, CARD_W-9, CARD_H-9], radius=16, fill=primary, outline=None)
    draw.rounded_rectangle([ART_X-5, ART_Y-5, ART_X+ART_W+5, ART_Y+ART_H+5], radius=10, fill=(10, 10, 15))

    img_path = os.path.join(IMG_DIR, f"{card_id}.png")
    if os.path.exists(img_path):
        art = Image.open(img_path).resize((ART_W, ART_H), Image.LANCZOS)
        card.paste(art, (ART_X, ART_Y))

    draw.rounded_rectangle([ART_X-2, ART_Y-2, ART_X+ART_W+2, ART_Y+ART_H+2], radius=8, fill=None, outline=accent, width=2)

    cost = card_data['cost']
    cost_x, cost_y = 25, 25
    draw.ellipse([cost_x-22, cost_y-22, cost_x+22, cost_y+22], fill=accent, outline=(255,255,255), width=2)
    font_large = get_font(28)
    cost_text = str(cost)
    bbox = draw.textbbox((0, 0), cost_text, font=font_large)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cost_x - tw//2, cost_y - th//2 - 2), cost_text, fill=(255, 255, 255), font=font_large)

    name = card_data['name']
    font_name = get_font(22)
    name_y = ART_Y + ART_H + 15
    if len(name) > 14:
        name = name[:13] + "..."
    bbox = draw.textbbox((0, 0), name, font=font_name)
    tw = bbox[2] - bbox[0]
    draw.text(((CARD_W - tw) // 2, name_y), name, fill=(255, 255, 255), font=font_name)

    font_type = get_font(16)
    type_text = card_data['type']
    if card_data['type'] == '生物':
        type_text += f"  |  {card_data['atk']} / {card_data['hp']}"
    bbox = draw.textbbox((0, 0), type_text, font=font_type)
    tw = bbox[2] - bbox[0]
    type_y = name_y + 35
    draw.text(((CARD_W - tw) // 2, type_y), type_text, fill=accent, font=font_type)

    div_y = type_y + 28
    draw.line([(ART_X, div_y), (ART_X + ART_W, div_y)], fill=accent, width=1)

    effect = card_data.get('effect', '')
    font_effect = get_font(13)
    effect_y = div_y + 10
    max_chars = 30
    lines = []
    for paragraph in effect.split('\n'):
        wrapped = textwrap.wrap(paragraph, width=max_chars)
        lines.extend(wrapped)
    for i, line in enumerate(lines[:7]):
        draw.text((ART_X + 10, effect_y + i * 18), line, fill=(220, 220, 220), font=font_effect)

    faction_name = faction['name']
    font_faction = get_font(12)
    bbox = draw.textbbox((0, 0), faction_name, font=font_faction)
    tw = bbox[2] - bbox[0]
    draw.text(((CARD_W - tw) // 2, CARD_H - 30), faction_name, fill=accent, font=font_faction)

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
