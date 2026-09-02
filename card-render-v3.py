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
OUTPUT_DIR = "C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards-final-v3"

# Special term explanations
TERM_EXPLANATIONS = {
    "守護": "此生物可阻擋攻擊",
    "飛行": "僅可被飛行生物防守",
    "疾襲": "進場即可攻擊",
    "觸發": "滿足條件時自動發動",
    "被動": "持續生效的效果",
    "起動": "可主動使用的能力",
    "橫置": "橫置表示已使用",
    "場地": "持續存在的場地效果",
    "獸化": "攻擊時獲得獸化指示物",
    "回聲": "施放法術時獲得回聲指示物",
}

# Card dimensions (Yu-Gi-Oh style)
CARD_W, CARD_H = 488, 680
ART_W, ART_H = 460, 460  # Larger art area
ART_X, ART_Y = 14, 60

# Darker faction colors
FACTION_COLORS = {
    "pa": {
        "primary": (15, 25, 40),
        "accent": (0, 180, 220),
        "glow": (0, 120, 160),
        "name": "實驗體",
        "symbol": "S",
    },
    "pb": {
        "primary": (40, 10, 10),
        "accent": (200, 50, 50),
        "glow": (150, 30, 30),
        "name": "認知科學局",
        "symbol": "C",
    },
    "pc": {
        "primary": (40, 30, 10),
        "accent": (220, 180, 50),
        "glow": (180, 140, 30),
        "name": "回聖會",
        "symbol": "R",
    },
    "pd": {
        "primary": (10, 35, 15),
        "accent": (50, 180, 80),
        "glow": (30, 130, 50),
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

def render_card(card_data):
    card_id = card_data['id']
    prefix, faction = get_faction(card_id)

    # Dark background
    card = Image.new('RGB', (CARD_W, CARD_H), faction['primary'])
    draw = ImageDraw.Draw(card)

    # Outer frame border (darker)
    draw.rounded_rectangle([0, 0, CARD_W-1, CARD_H-1], radius=16, fill=None, outline=faction['glow'], width=3)

    # Art area - extended to edges (超框 style)
    art_y = ART_Y
    draw.rectangle([0, art_y, CARD_W, art_y + ART_H], fill=(10, 10, 15))

    # Load and paste artwork (extended beyond normal bounds)
    img_path = os.path.join(IMG_DIR, f"{card_id}.png")
    if os.path.exists(img_path):
        art = Image.open(img_path).resize((ART_W, ART_H), Image.LANCZOS)
        card.paste(art, (ART_X, art_y))

    # Subtle frame overlay (like Yu-Gi-Oh frame break effect)
    for i in range(3):
        draw.rectangle([i, art_y + i, CARD_W - i, art_y + i + 1], fill=(*faction['glow'][:3], 50))

    # Cost circle (top right) - glowing effect
    cost = card_data['cost']
    cost_x, cost_y = CARD_W - 35, 30
    # Glow effect
    for r in range(25, 15, -1):
        alpha = int(100 * (1 - (r - 15) / 10))
        glow_color = tuple(min(255, c + 50) for c in faction['accent'])
        draw.ellipse([cost_x - r, cost_y - r, cost_x + r, cost_y + r], fill=glow_color)
    draw.ellipse([cost_x - 18, cost_y - 18, cost_x + 18, cost_y + 18], fill=faction['accent'], outline=(255, 255, 255), width=2)
    font_cost = get_font(24, bold=True)
    cost_text = str(cost)
    bbox = draw.textbbox((0, 0), cost_text, font=font_cost)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cost_x - tw//2, cost_y - th//2 - 2), cost_text, fill=(255, 255, 255), font=font_cost)

    # Card name (top left) - no background, just text
    name = card_data['name']
    font_name = get_font(16, bold=True)
    if len(name) > 16:
        name = name[:15] + "..."
    draw.text((15, 12), name, fill=(255, 255, 255), font=font_name)

    # Text box (below art) - contains type + effect
    text_box_y = art_y + ART_H + 10
    text_box_h = 150
    draw.rounded_rectangle([10, text_box_y, CARD_W - 10, text_box_y + text_box_h], radius=6, fill=(5, 5, 10))
    draw.rounded_rectangle([10, text_box_y, CARD_W - 10, text_box_y + text_box_h], radius=6, fill=None, outline=faction['glow'], width=1)

    # Type line (top of text box) - MTG style
    type_text = card_data['type']
    font_type = get_font(16, bold=True)
    draw.text((18, text_box_y + 8), type_text, fill=faction['accent'], font=font_type)

    # Effect text (below type)
    effect = card_data.get('effect', '')
    font_effect = get_font(15)
    effect_y = text_box_y + 32
    max_chars = 32
    lines = []
    for paragraph in effect.split('\n'):
        wrapped = textwrap.wrap(paragraph, width=max_chars)
        lines.extend(wrapped)

    for i, line in enumerate(lines[:5]):
        draw.text((18, effect_y + i * 20), line, fill=(220, 220, 220), font=font_effect)

    # Term explanations (bottom of text box, smaller font)
    font_term = get_font(10)
    used_terms = [t for t in TERM_EXPLANATIONS if t in effect]
    if used_terms:
        term_y = text_box_y + 128
        term_text = "／".join([f"{t}: {TERM_EXPLANATIONS[t]}" for t in used_terms])
        wrapped_terms = textwrap.wrap(term_text, width=48)
        for i, line in enumerate(wrapped_terms[:2]):
            draw.text((18, term_y + i * 12), line, fill=(160, 160, 180), font=font_term)

    # Power/Toughness box (bottom center) - MTG style
    if card_data['type'] == '生物':
        pt_x = CARD_W // 2
        pt_y = CARD_H - 35
        # Draw P/T box
        draw.rounded_rectangle([pt_x - 40, pt_y - 14, pt_x + 40, pt_y + 14], radius=6, fill=faction['accent'])
        draw.rounded_rectangle([pt_x - 40, pt_y - 14, pt_x + 40, pt_y + 14], radius=6, fill=None, outline=(255, 255, 255), width=1)
        pt_text = f"{card_data['atk']}/{card_data['hp']}"
        font_pt = get_font(18, bold=True)
        bbox = draw.textbbox((0, 0), pt_text, font=font_pt)
        tw = bbox[2] - bbox[0]
        draw.text((pt_x - tw//2, pt_y - 10), pt_text, fill=(255, 255, 255), font=font_pt)

    # Faction symbol (bottom left)
    symbol_x = 25
    symbol_y = CARD_H - 25
    draw.ellipse([symbol_x - 10, symbol_y - 10, symbol_x + 10, symbol_y + 10], fill=faction['accent'])
    font_symbol = get_font(12, bold=True)
    draw.text((symbol_x - 4, symbol_y - 7), faction['symbol'], fill=(255, 255, 255), font=font_symbol)

    # Faction name (bottom center)
    faction_name = faction['name']
    font_faction = get_font(10)
    bbox = draw.textbbox((0, 0), faction_name, font=font_faction)
    tw = bbox[2] - bbox[0]
    draw.text(((CARD_W - tw) // 2, CARD_H - 22), faction_name, fill=faction['accent'], font=font_faction)

    # Card number (bottom right)
    card_num = card_id.split('_')[1]
    font_num = get_font(9)
    draw.text((CARD_W - 35, CARD_H - 22), f"#{card_num}", fill=(100, 100, 100), font=font_num)

    return card

def main():
    force = '--force' in sys.argv
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading card data...")
    all_cards = load_all_cards()
    print(f"Found {len(all_cards)} cards")

    generated = 0
    failed = 0

    for card_id, card_data in sorted(all_cards.items()):
        output_path = os.path.join(OUTPUT_DIR, f"{card_id}.png")

        if os.path.exists(output_path) and not force:
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
