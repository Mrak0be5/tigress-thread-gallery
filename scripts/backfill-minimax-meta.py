import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GAL = HERE.parent
spec = importlib.util.spec_from_file_location("publish_add", HERE / "publish-add.py")
pa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pa)

MCP = Path(r"C:\Users\hebp\AppData\Roaming\StabilityMatrix\Packages\ComfyUI\input\mcp")
FRAMES = Path(r"C:\Users\hebp\OneDrive\Desktop\manager\hops-and-honey-bar-manager-3d\minimax-material\frames")
COMFY_IN = Path(r"C:\Users\hebp\AppData\Roaming\StabilityMatrix\Packages\ComfyUI\input")

TURBO = "MiniMax H3 Turbo 4-step|https://huggingface.co/Comfy-Org/MiniMax-H3_ComfyUI|1.0"
NAUGHTY = "SexGod NaughtyTimes MiniMax H3|https://civitai.com/models/2836176?modelVersionId=3200994|0.45"
RIDING = "Riding POV H3 I2V|https://civitai.com/models/2446218?modelVersionId=3203205|0.5"
HMNSFW = "HMNSFW AIO V2|https://civitai.com/models/2834417?modelVersionId=3206518|0.5"

SCENE = MCP / "tigra-scene-part1.png"
MALE = MCP / "ref-male-sheet-style-matched.png"
PENIS = MCP / "ref-penis-sheet-2.png"
TABLE = MCP / "tigra-table-anal-new.png"
PART2 = MCP / "tigra-part2-start.jpg"
HAND = FRAMES / "first-frame-standing-white.png"
CITY = MCP / "first-frame-city-blogger-standing.png"
CITY5 = COMFY_IN / "tigra_city_blogger_first_frame_5s.png"
SHEET = MCP / "tigra_sheet_clean.png"
POOL = MCP / "tigra-pool-anal-first.png"
HAND_IN = COMFY_IN / "tigra_handstand_first_frame.png"

V4_PROMPT = (
    "Cinematic 24fps medium-wide cabin shot. Keep the exact framing, camera distance, and composition of <Picture 1> for the entire clip. "
    "Do not zoom into genitals. Do not fill the frame with a penis close-up. Do not copy any character-sheet or anatomy-sheet layout. "
    "The camera slowly orbits a little to the right around Tigra, revealing more of the man behind her while staying a medium-wide shot of the table scene. "
    "<Picture 1> is the starting scene and the only composition reference. Tigra (female anthropomorphic tiger, orange fur, black stripes, white belly, short white hair) is bent over a wooden table. "
    "Her left leg stays raised high exactly as in <Picture 1>, do not lower her leg. A coffee mug sits on the table. "
    "Behind her a muscular human male performs deep anal sex using the penis already visible in <Picture 1>. "
    "<Picture 2> is identity reference only for the man's face, beard, muscular body, and skin tone. Do not copy <Picture 2> turnaround layout. "
    "Tigra looks bored and looks at the camera. She picks up the coffee mug with her right hand and drinks. "
    "While drinking she arches her lower back and shows her breasts to the camera. "
    "The man makes exactly 3 very strong deep thrusts. On every thrust Tigra winces in discomfort. "
    "Highly detailed textures, anatomically precise, natural body motion."
)

V3_PROMPT = (
    "Cinematic 24fps shot. The camera slowly orbits horizontally to the right, showing more of the man's penis. "
    "IMPORTANT: Tigra MUST keep her left leg raised high up exactly as in <Picture 1>, do not lower her leg! "
    "<Picture 1> is the starting scene. Tigra (female anthropomorphic tiger, orange fur, black stripes) is bent over a wooden table, her leg stays UP. "
    "Behind her, a muscular human male is performing deep, forceful anal sex. "
    "<Picture 2> is the precise visual reference for his huge, thick penis. "
    "<Picture 3> is the precise visual reference for the human male's body and skin tone. "
    "Tigra has a bored facial expression. She picks up the coffee mug with her right hand and drinks from it. "
    "While drinking, she arches her back down heavily, proudly showing off her bare breasts to the camera. She looks directly at the camera. "
    "The man makes exactly 3 very strong, deep, forceful thrusts over the duration. "
    "With every single hard thrust, Tigra visibly winces in pain. "
    "Highly detailed textures, anatomically precise, natural body motion."
)

V2_PROMPT = (
    "Cinematic 24fps shot. The camera slowly orbits to the right. "
    "<Picture 1> is the starting scene. Tigra (female anthropomorphic tiger, orange fur, black stripes, white hair) is bent over a wooden table. "
    "Behind her, a muscular human male is performing deep anal sex. "
    "<Picture 2> is the precise visual reference for his huge, thick penis. "
    "<Picture 3> is the precise visual reference for the human male's body, muscular build, and skin tone. "
    "Tigra has a bored, displeased facial expression, looking around out of boredom. "
    "Then she picks up the coffee mug from the table and drinks from it. She looks directly at the camera the entire time. "
    "He makes exactly 4 slow, deep, forceful thrusts over the duration. "
    "With every single thrust of his penis penetrating her, Tigra winces in discomfort. "
    "Highly detailed textures, anatomically precise, natural body motion."
)

COFFEE15_PROMPT = (
    "Cinematic 24fps medium-wide cabin shot. Keep the exact framing of <Picture 1>. "
    "<Picture 1> is the starting scene. Tigra drinks coffee bored while a man anally fucks her at the wooden table. "
    "<Picture 2> is penis anatomy identity only; do not copy sheet layout or fill the frame with a penis. "
    "Exactly 3 strong thrusts. Tigra winces on each thrust. Pull-out and gape at the end. "
    "Highly detailed textures, anatomically precise, natural body motion."
)

PART2_PROMPT = (
    "Cinematic 24fps shot. The scene continues seamlessly from <Picture 1>. "
    "Tigra is at the wooden table. The camera slowly pushes in towards her anus. "
    "Behind her, the muscular human male pushes his huge, thick penis as deeply as possible into her anus and holds it there for 3 seconds. "
    "Tigra's facial expression changes to intense disgust and revulsion. "
    "After the deep hold, the man slowly pulls his penis completely out of her anus. "
    "When the penis is removed, her anus remains stretched open, showing a visible gaping hole (rosebud). "
    "Highly detailed textures, anatomically precise, natural body motion."
)

HAND_PROMPT = (
    "Single continuous shot, exactly one adult anthropomorphic female tigress character "
    "on a seamless pure white background. "
    "0-3 seconds: the character shifts her weight forward, places both hands on the floor, "
    "and smoothly lifts into a controlled handstand. "
    "3-6 seconds: she stabilizes in a straight vertical handstand, arms locked, body balanced, "
    "striped tiger tail moving naturally for balance. "
    "6-10 seconds: while maintaining the handstand, she slowly opens both legs into a wide "
    "symmetrical straddle split and holds the pose. "
    "Static full-body camera, the entire character remains visible, smooth realistic motion, "
    "stable identity and anatomy matching the first frame exactly."
)


def ref(*pairs):
    out = []
    for label, path in pairs:
        p = Path(path)
        if p.is_file():
            out.append(f"{label}|{p}")
    return out


def pack(prompt="", refs=None, loras=None, model=None):
    return {
        "prompt": prompt,
        "refs": refs or [],
        "loras": loras or [],
        "model": model,
    }


MAP = {
    "minimax-ref2va-10s-wan-bbc-switch-pull-out-walk-r-bbc-enters": pack(
        loras=[],
        model="MiniMax-H3 Ref2VA Non-Turbo",
    ),
    "part-1-bored-coffee-ref2va-v4-10s": pack(
        V4_PROMPT,
        ref(("Picture 1 scene", SCENE), ("Picture 2 male identity", MALE)),
        [],
        "MiniMax-H3 Ref2VA Non-Turbo",
    ),
    "part-1-bored-coffee-ref2va-v4-10s-2": pack(
        V4_PROMPT,
        ref(("Picture 1 scene", SCENE), ("Picture 2 male identity", MALE)),
        [],
        "MiniMax-H3 Ref2VA Non-Turbo",
    ),
    "part-1-bored-coffee-ref2va-v3-10s": pack(
        V3_PROMPT,
        ref(("Picture 1 scene", SCENE), ("Picture 2 penis", PENIS), ("Picture 3 male", MALE)),
        [],
        "MiniMax-H3 Ref2VA Non-Turbo",
    ),
    "part-1-bored-coffee-ref2va-v2-10s": pack(
        V2_PROMPT,
        ref(("Picture 1 scene", SCENE), ("Picture 2 penis", PENIS), ("Picture 3 male", MALE)),
        [],
        "MiniMax-H3 Ref2VA Non-Turbo",
    ),
    "bored-coffee-anal-ref2va-non-turbo-15s": pack(
        COFFEE15_PROMPT,
        ref(("Picture 1 scene", TABLE), ("Picture 2 penis", PENIS)),
        [],
        "MiniMax-H3 Ref2VA Non-Turbo",
    ),
    "part-2-deep-hold-pullout-fl2va-10s": pack(
        PART2_PROMPT,
        ref(("Picture 1 last frame", PART2)),
        [],
        "MiniMax-H3 FL2VA Non-Turbo",
    ),
    "part-2-deep-hold-pullout-fl2va-10s-2": pack(
        PART2_PROMPT,
        ref(("Picture 1 last frame", PART2)),
        [],
        "MiniMax-H3 FL2VA Non-Turbo",
    ),
    "part-1-bored-coffee-fl2va-10s": pack(
        V4_PROMPT.replace("<Picture 2>", "the man"),
        ref(("first frame", SCENE)),
        [],
        "MiniMax-H3 FL2VA Non-Turbo",
    ),
    "black-man-continuation-fl2va-non-turbo-15s": pack(
        "Continuation from last frame. A nude black man enters from the right and anally fucks Tigra at the table. Keep identity from <Picture 1>.",
        ref(("first frame", PART2 if PART2.is_file() else SCENE)),
        [],
        "MiniMax-H3 FL2VA Non-Turbo",
    ),
    "table-anal-hole-fl2va-non-turbo-5s": pack(
        "Keep <Picture 1> pose. Anal penetration at the wooden table, gaping hole visible.",
        ref(("first frame", TABLE)),
        [],
        "MiniMax-H3 FL2VA Non-Turbo",
    ),
    "table-anal-hole-ref2va-non-turbo": pack(
        "Keep <Picture 1> composition. Gaping anal hole. <Picture 2> penis identity only, do not copy sheet layout.",
        ref(("Picture 1 scene", TABLE), ("Picture 2 penis", PENIS)),
        [],
        "MiniMax-H3 Ref2VA Non-Turbo",
    ),
    "table-anal-hole-ref2va-patched": pack(
        "Keep <Picture 1> composition. Gaping anal hole. <Picture 2> penis identity only.",
        ref(("Picture 1 scene", TABLE), ("Picture 2 penis", PENIS)),
        [TURBO],
        "MiniMax-H3 Ref2VA Turbo Q4",
    ),
    "pool-anal-hole-ref2va-patched": pack(
        "Orbit around Tigra at the pool table. Anal, wincing, gaping hole. <Picture 1> scene, <Picture 2> penis identity only.",
        ref(("Picture 1 scene", POOL), ("Picture 2 penis", PENIS)),
        [TURBO],
        "MiniMax-H3 Ref2VA Turbo Q4",
    ),
    "pool-anal-ref2va-turbo-v1": pack(
        "Pool table anal, 3 thrusts, pull-out. Keep <Picture 1> framing.",
        ref(("Picture 1 scene", POOL)),
        [TURBO],
        "MiniMax-H3 Ref2VA Turbo Q4",
    ),
    "pool-anal-fl2va-non-turbo": pack(
        "Orbit, wincing, looks at ball. Keep first frame identity.",
        ref(("first frame", POOL)),
        [],
        "MiniMax-H3 FL2VA Non-Turbo",
    ),
    "pool-anal-hole-ref2va": pack(
        "Orbit, wincing, gaping hole. <Picture 1> scene, <Picture 2> penis identity only.",
        ref(("Picture 1 scene", POOL), ("Picture 2 penis", PENIS)),
        [TURBO],
        "MiniMax-H3 Ref2VA Turbo Q4",
    ),
    "handstand-straddle-10s": pack(
        "",
        ref(("first frame", HAND if HAND.is_file() else HAND_IN)),
        [],
        "MiniMax-H3 I2V",
    ),
    "handstand-straddle-10s-exact": pack(
        "",
        ref(("first frame", HAND if HAND.is_file() else HAND_IN)),
        [],
        "MiniMax-H3 I2V",
    ),
    "handstand-split-h3-10s": pack(
        "",
        ref(("first frame", HAND if HAND.is_file() else HAND_IN)),
        [],
        "MiniMax-H3 I2V",
    ),
    "handstand-split-h3-exact-10s": pack(
        "",
        ref(("first frame", HAND if HAND.is_file() else HAND_IN)),
        [],
        "MiniMax-H3 I2V",
    ),
    "handstand-8s": pack(
        HAND_PROMPT,
        ref(("first frame", HAND if HAND.is_file() else HAND_IN)),
        [],
        "MiniMax-H3 I2V",
    ),
    "city-blogger-handstand-5s": pack(
        "",
        ref(("first frame", CITY5 if CITY5.is_file() else CITY)),
        [],
        "MiniMax-H3 I2V",
    ),
    "sheet-city-blogger-handstand-10s": pack(
        "",
        ref(("sheet / first frame", SHEET if SHEET.is_file() else CITY)),
        [],
        "MiniMax-H3 I2V",
    ),
    "city-allfours-anal-15s": pack(
        "City street, Tigra on all fours, anal, identity from first frame.",
        ref(("first frame", CITY if CITY.is_file() else HAND)),
        [],
        "MiniMax-H3 I2V",
    ),
    "fl2va-turbo-q4-test": pack(
        "FL2VA Turbo Q4 test from first frame.",
        ref(("first frame", TABLE if TABLE.is_file() else SCENE)),
        [TURBO],
        "MiniMax-H3 FL2VA Turbo Q4",
    ),
    "bored-anal-naughtytimes-15s": pack(
        "Bored coffee anal at the table. Keep first frame. Trigger: NaughtyTimes sex motion.",
        ref(("first frame", TABLE if TABLE.is_file() else SCENE)),
        [TURBO, NAUGHTY],
        "MiniMax-H3 FL2VA Turbo + NaughtyTimes",
    ),
    "bored-anal-ridingpov-15s": pack(
        "Bored coffee anal at the table. Keep first frame. Riding POV motion LoRA.",
        ref(("first frame", TABLE if TABLE.is_file() else SCENE)),
        [TURBO, RIDING],
        "MiniMax-H3 FL2VA Turbo + Riding POV",
    ),
    "bored-anal-baseline-15s": pack(
        "Bored coffee anal baseline, no concept LoRA. Keep first frame.",
        ref(("first frame", TABLE if TABLE.is_file() else SCENE)),
        [],
        "MiniMax-H3 FL2VA Non-Turbo",
    ),
    "table-anal-3thrust-10s": pack(
        "Table anal, 3 thrusts. Keep first frame.",
        ref(("first frame", TABLE)),
        [],
        "MiniMax-H3 I2V",
    ),
    "anal-hmnsfw-aio-v2": pack(
        "Table anal. Trigger hmmotion. Keep first frame.",
        ref(("first frame", TABLE)),
        [HMNSFW],
        "MiniMax-H3 FL2VA + HMNSFW AIO V2",
    ),
    "anal-penisref-hard-hmnsfw": pack(
        "Hard anal thrusts. First frame lock + penis text/ref. Trigger hmmotion.",
        ref(("first frame", TABLE), ("penis", PENIS)),
        [HMNSFW],
        "MiniMax-H3 FL2VA + HMNSFW AIO V2",
    ),
    "anal-fl2va-hard-fixref": pack(
        "Hard anal, first-frame lock.",
        ref(("first frame", TABLE)),
        [HMNSFW],
        "MiniMax-H3 FL2VA + HMNSFW AIO V2",
    ),
    "pool-anal-fl2va-orbit-ball": pack(
        "Pool anal, orbit, look at ball. Keep first frame.",
        ref(("first frame", POOL)),
        [],
        "MiniMax-H3 FL2VA Non-Turbo",
    ),
    "naughtytimes-fl2va-turbo": pack(
        "NaughtyTimes FL2VA Turbo sex motion. Keep first frame.",
        ref(("first frame", TABLE if TABLE.is_file() else SCENE)),
        [TURBO, NAUGHTY],
        "MiniMax-H3 FL2VA Turbo + NaughtyTimes",
    ),
}


def is_minimax(it: dict) -> bool:
    blob = " ".join(str(it.get(k) or "") for k in ("model", "id", "note", "title", "service")).lower()
    return any(x in blob for x in ("minimax", "fl2va", "ref2va")) or (
        str(it.get("file") or "").endswith(".mp4") and "h3" in blob
    )


def main() -> None:
    data = pa.load_manifest()
    n = 0
    for it in data.get("items") or []:
        if it.get("category") == "story":
            continue
        if not (is_minimax(it) or it.get("id") in MAP):
            continue
        meta = MAP.get(it["id"])
        if meta:
            prompt = "" if it.get("prompt") else meta["prompt"]
            refs = [] if it.get("refs") else meta["refs"]
            pa.apply_prompt_and_refs(it, prompt, refs)
            if meta["loras"]:
                pa.apply_loras(it, meta["loras"])
            else:
                it["loras"] = it.get("loras") or []
            if meta["model"]:
                it["model"] = meta["model"]
        elif "loras" not in it:
            it["loras"] = []
        it["service"] = "Local ComfyUI MiniMax-H3 (this PC)"
        it["service_url"] = "pc-video.html"
        n += 1
        print(it["id"], "refs", len(it.get("refs") or []), "loras", len(it.get("loras") or []), "prompt", bool(it.get("prompt")))
    data["howto"] = {"pc_video": "pc-video.html", "title": "Подключение к генерации видео на этом ПК"}
    services = data.get("services")
    if not isinstance(services, dict):
        services = {}
        data["services"] = services
    services["local-comfyui-minimax"] = {
        "name": "ПК видео (MiniMax ComfyUI)",
        "url": "pc-video.html",
        "docs": "pc-video.html",
        "model_url": "https://huggingface.co/Comfy-Org/MiniMax-H3_ComfyUI",
    }
    pa.save_manifest(data)
    print("updated", n)


if __name__ == "__main__":
    main()
