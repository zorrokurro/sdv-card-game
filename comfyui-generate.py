import json
import urllib.request
import urllib.parse
import time
import os
import uuid
import random
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

COMFYUI_URL = "http://127.0.0.1:8188"
CARDS_FILE = "C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json"
OUTPUT_DIR = "C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/img-ai-v2"
CHECKPOINT = "animagine-xl-4.0.safetensors"

QUALITY_TAGS = "masterpiece, best quality, highres, absurdres"

STYLE_TAGS = (
    "fantasy card game illustration, painterly brushwork, "
    "saturated colors, rich midtones, magical atmosphere, "
    "detailed textures, vibrant lighting"
)

NEGATIVE_PROMPT = (
    "worst quality, low quality, blurry, text, watermark, signature, "
    "frame, border, logo, multiple views, grid, mosaic, collage, "
    "deformed, ugly, duplicate, extra fingers, mutated hands, "
    "poorly drawn hands, poorly drawn face, bad anatomy, "
    "bad proportions, extra limbs, disfigured, nsfw, "
    "multiple people, crowd, many objects"
)

# ---- Card-specific prompts (name -> English description) ----
CARD_PROMPTS = {
    # ===== PA: Subject-21 / Protagonist (sci-fi + awakening) =====
    "pa_01": "1boy, young experiment subject, short dark hair, wearing a white lab jumpsuit with glowing blue circuit markings, standing in a dimly lit futuristic laboratory, mysterious cyan glow emanating from his chest, single character, centered composition",
    "pa_02": "glowing ancient rune tablet, floating golden runic inscriptions swirling around a stone slab, mystical energy, dark background with warm amber light, single object focus",
    "pa_03": "1boy, surveillance observer in a sleek dark uniform, cybernetic eye implant glowing red, monitoring wall of holographic screens, sci-fi control room, single character",
    "pa_04": "1boy, running through a dark emergency-lit corridor, wearing a torn white lab coat, red alarm lights flashing behind him, motion blur, dramatic escape scene, single character",
    "pa_05": "1boy, experiment subject awakening, glowing cyan eyes, energy radiating from body, lab coat dissolving into light particles, power awakening scene, dramatic pose, single character centered",
    "pa_06": "1girl, young woman with short brown hair, wearing a green field jacket, standing in a misty forest clearing, soft dawn light filtering through trees, gentle expression, single character",
    "pa_07": "1girl, elderly grandmother figure, warm smile, silver hair in a bun, wearing a traditional embroidered shawl, holding a glowing lantern, cozy cottage interior, warm lighting, single character",
    "pa_08": "magical warm orange memory sphere, swirling amber and gold light particles, nostalgic scene inside a crystal orb, warm color palette, soft glow, single object centered",
    "pa_09": "hidden safe house in an old urban building, dim warm lighting, dusty shelves with supplies, a small window letting in moonlight, secret hideout atmosphere, environment illustration",
    "pa_10": "abstract color perception art, swirling rainbow spectrum, a human eye surrounded by prismatic light rays, vivid hue separation, chromatic aberration effect, single focal point",
    "pa_11": "1boy and 1girl, two characters sharing a moment of trust, reaching hands toward each other, warm golden light between them, emotional scene, soft painterly style",
    "pa_12": "dark red shadowy figure stalking from behind, ominous crimson aura, a silhouette pursuing through dark alley, red and black color scheme, dramatic tension, two figures in scene",
    "pa_13": "1boy, young man with fiery red hair and red eyes, wearing a crimson armored jacket, standing confidently with arms crossed, bold red lighting, powerful aura, single character centered",
    "pa_14": "1girl, young woman with bright blue-green hair, wearing a teal combat suit, glowing cyan energy in her hands, confident battle pose, cool blue-green color scheme, single character",
    "pa_15": "abstract texture perception, swirling tactile surfaces, fur, metal, glass, wood textures blending together, a floating eye analyzing materials, surreal composition, single focal point",
    "pa_16": "futuristic military base interior, reinforced steel walls, holographic tactical displays, soldiers in enhancement pods, cold blue lighting, sci-fi laboratory facility, environment",
    "pa_17": "1man, mysterious scientist in a long dark coat, holding a glowing data pad, standing in shadows, half-face illuminated by screen light, secretive expression, single character",
    "pa_18": "dramatic reveal scene, a glowing classified document floating in mid-air, red classified stamps, scattered papers, dramatic spotlight, conspiracy reveal atmosphere, single focus",
    "pa_19": "southern node facility, a massive glowing crystal structure in a desert landscape, energy beams connecting to the sky, epic scale, warm sunset lighting, environment with central focus",
    "pa_20": "1oldman, elderly man with silver white hair and beard, wearing a flowing white robe, wise eyes, holding a glowing crystal staff, standing in a grand library, dignified pose, single character",
    "pa_21": "1boy, experiment subject with visible cybernetic enhancements, glowing circuit patterns on skin, walking forward through a destroyed laboratory, debris floating, determination in eyes, single character",
    "pa_22": "abstract layered perception, multiple translucent color layers overlapping, depth visualization, a mystical eye seeing through dimensions, purple and blue hues, single focal point",
    "pa_23": "seven ghostly spirits gathered in a circle, translucent ethereal figures glowing with different colored auras, summoning ritual, dark misty environment, dramatic lighting, group composition",
    "pa_24": "1boy, experiment subject in a transcendent state, body dissolving into colorful light particles, arms spread wide, reality warping around him, cosmic energy, dramatic climax scene, single character",
    # PA Spells
    "pa_25": "emotional color magic, swirling warm and cool color waves emanating from a glowing orb, emotional energy visualization, rainbow spectrum, single magical effect centered",
    "pa_26": "intuition flash, a bright lightning bolt of golden insight striking a crystal brain, sparkles and light particles, sudden realization moment, single magical effect",
    "pa_27": "texture reading spell, magical hands touching an invisible surface, material properties revealed as glowing outlines, stone, metal, wood patterns visible, single spell effect",
    "pa_28": "structural intuition, a glowing geometric blueprint materializing in mid-air, architectural lines and angles floating, holographic 3D structure, single magical visualization",
    "pa_29": "direction intuition, a glowing magical compass with runic markings, golden arrow pointing forward, path illuminated ahead, navigation magic, single object centered",
    "pa_30": "echo reading, sound waves visualized as colorful ripples emanating from a point, audio magic, waveform patterns in golden light, single spell effect",
    "pa_31": "hue observation spell, a floating crystal prism splitting white light into rainbow spectrum, color magic, prismatic rays, single magical object",
    "pa_32": "texture observation, magical scanning beam revealing material composition, layers of matter visible, scientific magic effect, single spell visualization",
    "pa_33": "layer observation, magical X-ray vision effect showing depth layers, translucent overlapping planes, perception magic, single spell effect centered",
    "pa_34": "rune inscription stabilization, glowing protective runes forming a circle, golden magical symbols locking into place, ward magic, single spell effect",
    "pa_35": "color shielding, a shimmering iridescent barrier dome, rainbow light refracting through energy shield, defensive magic, single spell effect",
    "pa_36": "grey-coated investigator searching with a glowing magnifying device, detective scene, scanning light beam, single character in action",
    "pa_37": "distraction spell, multiple glowing illusion copies scattering in different directions, decoy magic, light duplicates, single spell effect",
    "pa_38": "virtual particle shield, swirling quantum energy barrier, shimmering translucent force field with particle effects, defensive magic, single spell centered",
    "pa_39": "dynamic Faraday cage, electric arcs contained within a rotating magnetic barrier, lightning trapped in geometry, electromagnetic magic, single spell effect",
    "pa_40": "echo gold resonance, golden sound waves vibrating a crystalline structure, harmonic magic, glowing gold frequency patterns, single spell effect",
    "pa_41": "critical burst, massive energy explosion radiating outward, dramatic shockwave, blinding light at center, ultimate attack magic, single spell effect centered",
    "pa_42": "micro-physical interference shockwave, tiny energy pulses creating visible ripples in space, quantum disruption magic, single spell effect",
    "pa_43": "sonic pulse, visible sound wave rings expanding outward from a point, blue energy waves, acoustic magic, single spell effect centered",
    "pa_44": "dark red color perception, a glowing eye perceiving crimson energy patterns, dark red magical aura, perception spell, single spell effect",
    "pa_45": "sonic focus anti-air, upward-pointing sound amplification device, concentrated beam of sonic energy shooting skyward, single spell effect",
    "pa_46": "probability touch, a hand reaching through a veil of shimmering probability particles, reality-bending magic, quantum uncertainty visualization, single spell effect",
    "pa_47": "resonance shatter, a crystalline structure cracking with visible sound waves, destructive resonance magic, fragments flying, single spell effect",
    "pa_48": "thermoelectric phonon coupling, heat energy and sound waves merging, thermal-acoustic magic effect, warm and cool energy mixing, single spell effect",
    "pa_49": "quantum entanglement resonance, two linked glowing orbs connected by energy threads, spooky action at distance, magical connection, single spell effect",
    "pa_50": "eye of negation, a massive mystical eye with a void pupil, reality distortion around it, anti-magic symbol, ominous power, single magical object centered",
    "pa_51": "path convergence, multiple light trails merging into one brilliant beam, roads of energy meeting at a focal point, destiny magic, single spell effect",
    "pa_52": "dimensional透视, looking through a magical portal into another realm, impossible geometry, Escher-like space bending, single spell effect centered",
    "pa_53": "memory fragment, a glowing shard of crystallized memory showing a scene inside, nostalgic warm light, magical keepsake, single object",
    "pa_54": "life heat source, a warm glowing heart-shaped flame, vital energy radiating outward, healing warmth,生命 magic, single spell effect centered",
    "pa_55": "enzymatic tunneling acceleration, speed lines and molecular structures, accelerated motion magic, green energy boosting, single spell effect",
    "pa_56": "magnetic reception resonance, magnetic field lines visualized as glowing patterns, a lodestone pulsing with power, electromagnetic magic, single spell effect",
    "pa_57": "bioluminescence regulation, a glowing creature adjusting its light output, colorful bioluminescent patterns, underwater-like glow, single spell effect",
    "pa_58": "reincarnation path, a glowing spiral of souls ascending through light, cycle of rebirth visualization, warm golden energy, single spell effect centered",
    "pa_59": "doctor's final redemption, a figure releasing golden energy from their hands,赎罪 gesture, light dissolving darkness, emotional magical scene, single character",
    "pa_60": "name spell, Strada维尔索, a massive glowing name inscription materializing in cosmic space, ultimate naming magic, reality-defining text, single spell effect centered",
}

# Add generic prompts for cards not in the dict
def get_generic_creature(prefix, name, cost):
    faction_subjects = {
        "pa": [
            "a young experiment subject with glowing cyan markings on skin, wearing a white lab coat, sci-fi setting, mysterious aura",
            "a bio-engineered humanoid with luminous eyes, futuristic laboratory background, experimental creature, ethereal glow",
            "a person with cybernetic enhancements and glowing circuit patterns, standing in a sci-fi corridor, determined expression",
        ],
        "pb": [
            "a stern military officer in a dark grey uniform with red accents, surveillance equipment, cold expression, authoritative pose",
            "an armored tactical soldier with a visor helmet, red energy weapon, dark industrial setting, menacing presence",
            "a grey-coated agent with glowing red cybernetic eye, surveillance drone companion, dark corridor, threatening stance",
        ],
        "pc": [
            "a holy monk in golden robes, sacred runes floating around, temple setting, serene expression, divine light emanating",
            "a prophet figure with a glowing third eye, ancient temple background, mystical aura, prophetic vision, golden light",
            "a sacred guardian in ornate golden armor, holding a holy relic, cathedral setting, divine power, majestic pose",
        ],
        "pd": [
            "a tribal warrior with face paint and bone accessories, standing in a wild forest, primal power, feral energy",
            "a massive beast tamer standing beside a giant wolf, wilderness backdrop, tribal markings, savage strength",
            "a feral warrior with animal pelts and totemic weapons, moonlit clearing, wild howl, untamed power",
        ],
    }
    subjects = faction_subjects.get(prefix, faction_subjects["pa"])
    subject = subjects[cost % len(subjects)]
    return f"1{'boy' if cost % 2 == 0 else 'girl'}, {subject}, single character, centered composition, full body"

def get_generic_spell(prefix, name, cost):
    faction_spells = {
        "pa": [
            "a glowing energy beam of cyan light shooting forward, sci-fi magic, particle effects, single spell effect centered",
            "swirling runic symbols forming a magical circle, glowing blue runes, cognitive magic, single spell effect",
            "a burst of colorful perception energy, prismatic light rays, vision magic, single spell effect centered",
        ],
        "pb": [
            "a suppression beam of dark red energy, military magic, targeting reticle, single spell effect centered",
            "a tactical strike visualization, red energy converging on a point, precision attack magic, single spell effect",
            "an electric containment field crackling with red lightning, barrier magic, single spell effect centered",
        ],
        "pc": [
            "golden holy runes inscribing themselves in mid-air, sacred geometry, divine blessing magic, single spell effect centered",
            "echoing sound waves made visible as golden ripples, resonance magic, cathedral acoustics, single spell effect",
            "a beam of divine light descending from above, holy magic, sacred power, single spell effect centered",
        ],
        "pd": [
            "a primal howl visualized as shockwaves of green energy, wild magic, nature power, single spell effect centered",
            "a beast charge effect with motion lines and claw marks, savage attack magic, single spell effect",
            "a tribal war cry visualization, sonic energy with totemic symbols, wild magic, single spell effect centered",
        ],
    }
    spells = faction_spells.get(prefix, faction_spells["pa"])
    spell = spells[cost % len(spells)]
    return f"{spell}, no people, focused composition"


def build_prompt(card):
    card_id = card["id"]
    name = card["name"]
    card_type = card["type"]
    cost = card.get("cost", 1)
    prefix = card_id.split("_")[0]

    if card_id in CARD_PROMPTS:
        subject = CARD_PROMPTS[card_id]
    elif card_type == "生物":
        subject = get_generic_creature(prefix, name, cost)
    else:
        subject = get_generic_spell(prefix, name, cost)

    prompt = f"{QUALITY_TAGS}, {subject}, {STYLE_TAGS}"
    return prompt


def create_workflow(prompt, seed=None):
    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 7,
                "denoise": 1.0,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "seed": seed,
                "steps": 20,
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": CHECKPOINT},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": 832, "width": 624},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": prompt},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": NEGATIVE_PROMPT},
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "card",
                "images": ["8", 0],
            },
        },
    }
    return workflow


def queue_prompt(workflow):
    client_id = str(uuid.uuid4())
    payload = json.dumps({"prompt": workflow, "client_id": client_id}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result.get("prompt_id"), client_id


def wait_for_completion(prompt_id, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(f"{COMFYUI_URL}/history/{prompt_id}")
            with urllib.request.urlopen(req) as resp:
                history = json.loads(resp.read())
            if prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})
                for node_id, node_output in outputs.items():
                    if "images" in node_output:
                        return node_output["images"]
            time.sleep(1)
        except Exception:
            time.sleep(2)
    return None


def download_image(filename, subfolder, output_path):
    params = urllib.parse.urlencode(
        {"filename": filename, "subfolder": subfolder, "type": "output"}
    )
    req = urllib.request.Request(f"{COMFYUI_URL}/view?{params}")
    with urllib.request.urlopen(req) as resp:
        with open(output_path, "wb") as f:
            f.write(resp.read())


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cards = load_cards()

    card_list = list(cards.values())
    total = len(card_list)
    print(f"Total cards to generate: {total}")

    generated = 0
    failed = 0

    for i, card in enumerate(card_list):
        card_id = card["id"]
        name = card["name"]
        output_file = os.path.join(OUTPUT_DIR, f"{card_id}.png")

        if os.path.exists(output_file):
            print(f"[{i+1}/{total}] SKIP (exists): {card_id}")
            generated += 1
            continue

        prompt = build_prompt(card)
        workflow = create_workflow(prompt)

        print(f"[{i+1}/{total}] {card_id} - {name}")

        try:
            prompt_id, client_id = queue_prompt(workflow)
            if not prompt_id:
                print(f"  ERROR: Failed to queue prompt")
                failed += 1
                continue

            images = wait_for_completion(prompt_id, timeout=300)
            if not images:
                print(f"  ERROR: Generation timed out")
                failed += 1
                continue

            img_info = images[0]
            download_image(
                img_info["filename"],
                img_info.get("subfolder", ""),
                output_file,
            )
            print(f"  OK")
            generated += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

        time.sleep(2)

    print(f"\nDone! Generated: {generated}, Failed: {failed}, Total: {total}")


def load_cards():
    with open(CARDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
