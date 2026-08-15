#!/usr/bin/env python3
"""Add a new generation to the tigress thread gallery and optionally push to GitHub Pages.

Usage:
  python publish-add.py path/to/image.png --title "Pool v6" --category scene --model "Seedream 5 Pro" --note "fix notes"
  python publish-add.py path/to/video.mp4 --title "..." --category video --prompt-file prompt.txt --ref "Image 1|https://..." --lora "Name|https://civitai.com/models/...|0.45" --push
  python publish-add.py --update-id existing-id --prompt-file prompt.txt --ref "Image 1|url" --push
  python publish-add.py --rebuild-only
  python publish-add.py --extract-posters [--push]
  python publish-add.py --encode-stream [--push]
  python publish-add.py --push-only
  python publish-add.py path/to/STORY-v8.7.md --category story --title "Ночная смена" --id story-gym-night-shift --push

Defaults:
  GAL = C:\\Users\\hebp\\galleries\\tigress-thread-gallery
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

GAL = Path(r"C:\Users\hebp\galleries\tigress-thread-gallery")
IMG = GAL / "images"
POSE_DIR = IMG / "poses"
REFS_DIR = IMG / "refs"
POSTER_DIR = IMG / "posters"
STREAM_DIR = IMG / "stream"
STREAM_INDEX = GAL / "stream-index.js"
PROMPTS = GAL / "prompts"
STORIES = GAL / "stories"
STORY_HTML = GAL / "story.html"
MANIFEST = GAL / "manifest.json"
PUBLIC_MANIFEST = GAL / "manifest-public.json"
RE_LOCAL_PATH = re.compile(r"^[A-Za-z]:[\\/]|^/Users/|^/home/|^\\\\")
MAX_SIDE = 1800
QUALITY = 86
POSTER_MAX_SIDE = 720
POSTER_QUALITY = 72
RE_BOLD = re.compile(r"\*\*(.+?)\*\*")
RE_EM = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
RE_HTML_LINE = re.compile(
    r"^</?(?:div|aside|section|span)\b",
    re.I,
)
ACT_CLASS = {
    "Пролог. Ещё одна": "act-prologue",
    "Акт I. Два сертификата": "act-1",
    "Акт II. Прокачка и ускоренный VIP": "act-2",
    "Акт III. Долг уже внутри": "act-3",
    "Акт IV. Закрытие VIP": "act-4",
}
SCENE_CLASS = {
    "Сообщения": "scene-phone",
    "Чёрный ход": "scene-door",
    "Раздевалка": "scene-locker",
    "Площадка. Устав": "scene-school",
    "Йога": "scene-yoga",
    "Приветствие": "scene-greet",
    "Березка": "scene-birch",
    "Сгибание ног": "scene-sex",
    "Скамья. Ноги за голову": "scene-sex",
    "Велотренажёр": "scene-sex",
    "Коридор. Долг": "scene-debt",
    "Тяга гантели": "scene-sex",
    "Душ": "scene-shower",
    "Уговоры": "scene-trap",
    "Наклоны": "scene-sex",
    "Планка": "scene-sex",
    "Жим": "scene-sex",
    "Растяжка": "scene-yoga",
    "Командный финал": "scene-finale",
    "Aftercare": "scene-after",
    "Диван": "scene-beat",
}


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9а-яё]+", "-", s, flags=re.I)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:60] or "img"


def to_web_jpeg(src: Path, dest: Path) -> tuple[int, int]:
    im = Image.open(src)
    if im.mode in ("RGBA", "P"):
        bg = Image.new("RGB", im.size, (20, 22, 28))
        if im.mode == "P":
            im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
        im = bg
    elif im.mode != "RGB":
        im = im.convert("RGB")
    w, h = im.size
    scale = min(1.0, MAX_SIDE / max(w, h))
    if scale < 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return im.size


def load_manifest() -> dict:
    if MANIFEST.is_file():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {
        "title": "Tigress thread gallery",
        "description": "Thread generations",
        "created": datetime.now().strftime("%Y-%m-%d"),
        "items": [],
    }


def item_sort_key(it: dict) -> str:
    return str(it.get("date") or it.get("created") or "")


def sort_items_newest_first(data: dict) -> None:
    data["items"] = sorted(
        data.get("items") or [],
        key=item_sort_key,
        reverse=True,
    )


def is_video_item(it: dict) -> bool:
    return (it.get("category") or "") == "video" or str(it.get("file") or "").lower().endswith(".mp4")


def poster_rel(iid: str) -> str:
    return f"images/posters/{iid}.jpg"


def extract_poster(video_path: Path, dest: Path) -> tuple[int, int]:
    import cv2

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"cannot open {video_path}")
    frame = None
    for msec in (0, 400, 1200):
        if msec:
            cap.set(cv2.CAP_PROP_POS_MSEC, float(msec))
        ok, raw = cap.read()
        if not ok or raw is None or not getattr(raw, "size", 0):
            continue
        mean = float(raw.mean())
        if frame is None or mean > 8:
            frame = raw
        if mean > 8:
            break
    cap.release()
    if frame is None:
        raise RuntimeError(f"no frame from {video_path}")
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    im = Image.fromarray(rgb)
    w, h = im.size
    scale = min(1.0, POSTER_MAX_SIDE / max(w, h))
    if scale < 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=POSTER_QUALITY, optimize=True, progressive=True)
    return im.size


def ensure_item_poster(item: dict, force: bool = False) -> bool:
    if not is_video_item(item):
        return False
    iid = str(item.get("id") or "")
    if not iid:
        return False
    src = GAL / str(item.get("file") or "")
    dest = POSTER_DIR / f"{iid}.jpg"
    rel = poster_rel(iid)
    if dest.is_file() and dest.stat().st_size > 0 and not force:
        if item.get("poster") != rel:
            item["poster"] = rel
            return True
        return False
    if not src.is_file():
        print("skip poster, missing video", src, file=sys.stderr)
        return False
    try:
        extract_poster(src, dest)
        item["poster"] = rel
        print("Poster", iid, "->", dest)
        return True
    except Exception as e:
        print("poster fail", iid, e, file=sys.stderr)
        return False


def extract_all_posters(data: dict, force: bool = False) -> int:
    n = 0
    for it in data.get("items") or []:
        if isinstance(it, dict) and ensure_item_poster(it, force=force):
            n += 1
    return n


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    raise RuntimeError("ffmpeg not found")


def stream_rel(iid: str) -> str:
    return f"images/stream/{iid}.mp4"


def process_video_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp.mp4")
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(src),
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "28",
        "-pix_fmt",
        "yuv420p",
        "-g",
        "48",
        "-keyint_min",
        "48",
        "-sc_threshold",
        "0",
        "-movflags",
        "+faststart",
        str(tmp),
    ]
    subprocess.run(cmd, check=True)
    tmp.replace(dest)


def strip_secrets_item(it: dict) -> dict:
    out = {k: v for k, v in it.items() if k not in ("api_key", "key_name", "prompt")}
    src = str(out.get("source") or "")
    if RE_LOCAL_PATH.match(src):
        out.pop("source", None)
    refs = out.get("refs")
    if isinstance(refs, list):
        cleaned = []
        for r in refs:
            if not isinstance(r, dict):
                cleaned.append(r)
                continue
            rr = dict(r)
            rsrc = str(rr.get("source") or "")
            if RE_LOCAL_PATH.match(rsrc):
                rr.pop("source", None)
            cleaned.append(rr)
        out["refs"] = cleaned
    return out


def public_manifest(data: dict) -> dict:
    return {
        "title": data.get("title"),
        "description": data.get("description"),
        "created": data.get("created"),
        "updated": data.get("updated"),
        "items": [
            strip_secrets_item(it) if isinstance(it, dict) else it
            for it in (data.get("items") or [])
        ],
    }


def save_manifest(data: dict) -> None:
    sort_items_newest_first(data)
    data["updated"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="minutes")
    data["local_path"] = str(GAL)
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    PUBLIC_MANIFEST.write_text(
        json.dumps(public_manifest(data), ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def git_push(message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=GAL, check=True)
    st = subprocess.run(["git", "status", "--porcelain"], cwd=GAL, capture_output=True, text=True)
    if not st.stdout.strip():
        print("Nothing to commit.")
        return
    subprocess.run(["git", "commit", "-m", message], cwd=GAL, check=True)
    subprocess.run(["git", "push", "-u", "origin", "HEAD"], cwd=GAL, check=True)
    print("Pushed.")


def parse_ref_spec(spec: str, index: int) -> tuple[str, str]:
    if "|" in spec:
        label, src = spec.split("|", 1)
        label = label.strip() or f"ref {index}"
        return label, src.strip()
    return f"ref {index}", spec.strip()


def fetch_ref_to_temp(src: str) -> Path:
    if src.startswith("http://") or src.startswith("https://"):
        suffix = Path(src.split("?", 1)[0]).suffix or ".img"
        fd, name = tempfile.mkstemp(prefix="galref-", suffix=suffix)
        os.close(fd)
        tmp = Path(name)
        req = urllib.request.Request(src, headers={"User-Agent": "tigress-gallery/1.0"})
        with urllib.request.urlopen(req, timeout=90) as r, open(tmp, "wb") as f:
            f.write(r.read())
        return tmp
    p = Path(src)
    if not p.is_file():
        raise FileNotFoundError(src)
    return p


def ingest_refs(iid: str, specs: list[str]) -> list[dict]:
    out: list[dict] = []
    dest_dir = REFS_DIR / iid
    dest_dir.mkdir(parents=True, exist_ok=True)
    for i, spec in enumerate(specs, start=1):
        if not spec.strip():
            continue
        label, src = parse_ref_spec(spec, i)
        entry = {"label": label, "source": src}
        try:
            tmp = fetch_ref_to_temp(src)
            name = f"{i:02d}-{slugify(label)}.jpg"
            dest = dest_dir / name
            to_web_jpeg(tmp, dest)
            if tmp.parent == Path(tempfile.gettempdir()) and tmp.name.startswith("galref-"):
                try:
                    tmp.unlink(missing_ok=True)
                except OSError:
                    pass
            entry["file"] = f"images/refs/{iid}/{name}"
            print("Ref", label, "->", dest)
        except Exception as e:
            print("Ref ingest failed", label, src, e, file=sys.stderr)
            entry["file"] = src if src.startswith("http") else ""
        out.append(entry)
    return out


def inline_md(text: str) -> str:
    text = html.escape(text)
    text = RE_BOLD.sub(r"<strong>\1</strong>", text)
    text = RE_EM.sub(r"<em>\1</em>", text)
    return text


def _para_class(body: str, scene_cls: str | None) -> str:
    plain = re.sub(r"<[^>]+>", "", body)
    if re.fullmatch(r"<em>.*</em>", body, flags=re.S):
        if scene_cls == "scene-phone":
            return "voice-phone"
        return "voice-thought"
    if plain.startswith("— Срыв.") or plain.startswith("Срыв."):
        return "voice-debt"
    return ""


def md_to_html(src: str) -> str:
    lines = src.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    para: list[str] = []
    scene_cls: str | None = None
    section_open = False

    def flush() -> None:
        if not para:
            return
        body = inline_md("\n".join(para)).replace("\n", "<br>\n")
        cls = _para_class(body, scene_cls)
        attr = f' class="{cls}"' if cls else ""
        out.append(f"<p{attr}>{body}</p>")
        para.clear()

    def close_section() -> None:
        nonlocal section_open, scene_cls
        if section_open:
            out.append("</section>")
            section_open = False
            scene_cls = None

    for line in lines:
        stripped = line.strip()
        if line.startswith("### "):
            flush()
            out.append(f"<h3>{inline_md(line[4:])}</h3>")
        elif line.startswith("## "):
            flush()
            close_section()
            title = line[3:].strip()
            scene_cls = SCENE_CLASS.get(title, "scene-beat")
            out.append(f'<section class="scene {scene_cls}">')
            section_open = True
            out.append(f"<h2>{inline_md(title)}</h2>")
        elif line.startswith("# "):
            flush()
            close_section()
            title = line[2:].strip()
            act_cls = ACT_CLASS.get(title, "")
            attr = f' class="{act_cls}"' if act_cls else ""
            out.append(f"<h1{attr}>{inline_md(title)}</h1>")
        elif re.fullmatch(r"-{3,}", stripped):
            flush()
        elif re.fullmatch(r"Ночная смена", stripped):
            flush()
        elif re.fullmatch(r"Версия\s+[0-9.]+", stripped):
            flush()
        elif RE_HTML_LINE.match(stripped):
            flush()
            out.append(stripped)
        elif stripped == "":
            flush()
        else:
            para.append(line)
    flush()
    close_section()
    return "\n".join(out)


def extract_story_meta(text: str, src: Path, title_arg: str) -> tuple[str, str]:
    title = (title_arg or "").strip()
    if not title:
        m = re.search(r"^#\s+(.+)$", text, re.M)
        title = m.group(1).strip() if m else src.stem
    ver = ""
    vm = re.search(r"(?:\*\*)?Версия\s+([0-9.]+)(?:\*\*)?", text)
    if vm:
        ver = vm.group(1)
    else:
        vm = re.search(r"v(\d+(?:\.\d+)*)", src.stem, re.I)
        if vm:
            ver = vm.group(1)
    return title, ver


def write_story_page(title: str, version: str, md_rel: str, body_html: str) -> None:
    ver_label = f"Версия {html.escape(version)}" if version else "Рассказ"
    page = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex, nofollow" />
  <title>{html.escape(title)} — {html.escape(version or "рассказ")}</title>
  <style>
    :root {{
      --bg: #0d0f12;
      --panel: #161a20;
      --border: #2a313c;
      --text: #e8ecf1;
      --muted: #9aa3b2;
      --accent: #7c9cff;
      --story: #f4d35e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
      background: radial-gradient(1200px 600px at 10% -10%, #1a2233 0%, var(--bg) 55%);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.7;
    }}
    header, article, footer {{
      max-width: 42rem;
      margin: 0 auto;
      padding: 0 1.25rem;
    }}
    header {{ padding-top: 1.5rem; padding-bottom: 0.5rem; }}
    header a {{ color: var(--accent); text-decoration: none; font-size: 0.9rem; }}
    header a:hover {{ text-decoration: underline; }}
    header h1 {{
      margin: 0.7rem 0 0.25rem;
      font-size: clamp(1.5rem, 3vw, 2rem);
      letter-spacing: -0.02em;
      font-weight: 650;
    }}
    header p {{ margin: 0.2rem 0; color: var(--muted); font-size: 0.95rem; }}
    article {{
      padding: 1rem 1.25rem 3rem;
      font-size: 1.05rem;
    }}
    article h1 {{
      font-size: 1.45rem;
      margin: 2rem 0 0.8rem;
      letter-spacing: -0.02em;
    }}
    article h1:first-child {{ margin-top: 0; }}
    article h2 {{
      font-size: 1.15rem;
      margin: 1.6rem 0 0.7rem;
      font-weight: 600;
    }}
    article h3 {{ font-size: 1.02rem; margin: 1.3rem 0 0.5rem; }}
    article p {{ margin: 0.75rem 0; }}
    article hr {{
      border: 0;
      border-top: 1px solid var(--border);
      margin: 1.6rem 0;
    }}
    article .legend {{
      display: none;
    }}
    article section.scene {{
      margin: 1.45rem 0 1.9rem;
      padding: 0.1rem 0 0.45rem 1.05rem;
      border-left: 3px solid var(--border);
      border-radius: 0 10px 10px 0;
    }}
    article .voice-whisper,
    article div.voice-whisper p {{
      font-family: Georgia, "Palatino Linotype", serif;
    }}
    article .voice-school,
    article div.voice-school p {{
      font-family: "Segoe UI", system-ui, sans-serif;
      font-weight: 500;
    }}
    article .voice-vip,
    article div.voice-vip p {{
      font-family: Georgia, serif;
    }}
    article p.voice-debt,
    article div.voice-debt p {{
      font-family: ui-monospace, Consolas, monospace;
      font-variant-numeric: tabular-nums;
    }}
    footer {{
      padding-bottom: 2.5rem;
      color: var(--muted);
      font-size: 0.8rem;
    }}
    footer a {{ color: var(--accent); }}
  </style>
</head>
<body>
  <header>
    <p><a href="index.html#story">Галерея / Рассказы</a></p>
    <h1>{html.escape(title)}</h1>
    <p>{ver_label} · NSFW 18+</p>
  </header>
  <article>
{body_html}
  </article>
  <footer>
    Исходник: <a href="{html.escape(md_rel)}">{html.escape(md_rel)}</a>
  </footer>
</body>
</html>
"""
    STORY_HTML.write_text(page, encoding="utf-8")


def publish_story(src: Path, args: argparse.Namespace, data: dict) -> dict:
    text = src.read_text(encoding="utf-8")
    title, version = extract_story_meta(text, src, args.title)
    STORIES.mkdir(parents=True, exist_ok=True)
    dest_name = src.name
    dest = STORIES / dest_name
    shutil.copy2(src, dest)
    md_rel = f"stories/{dest_name}"
    write_story_page(title, version, md_rel, md_to_html(text))
    iid = args.id or "story-gym-night-shift"
    data["items"] = [it for it in data.get("items") or [] if it.get("id") != iid]
    item = {
        "id": iid,
        "file": md_rel,
        "html": "story.html",
        "source": src.name,
        "title": title,
        "category": "story",
        "model": args.model if args.model != "Seedream 5 Pro" else "проза",
        "note": args.note or "Последняя версия рассказа",
        "version": version,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "latest": True,
    }
    data["items"].insert(0, item)
    return item


def apply_prompt_and_refs(item: dict, prompt: str, ref_specs: list[str]) -> None:
    iid = item["id"]
    if prompt:
        item["prompt"] = prompt
        PROMPTS.mkdir(parents=True, exist_ok=True)
        (PROMPTS / f"{iid}.txt").write_text(prompt, encoding="utf-8")
        item["prompt_file"] = f"prompts/{iid}.txt"
    if ref_specs:
        item["refs"] = ingest_refs(iid, ref_specs)


def parse_lora_spec(spec: str) -> dict:
    parts = [p.strip() for p in spec.split("|")]
    out = {"name": parts[0] if parts else "LoRA"}
    if len(parts) > 1 and parts[1]:
        out["url"] = parts[1]
    if len(parts) > 2 and parts[2]:
        try:
            out["strength"] = float(parts[2])
        except ValueError:
            out["strength"] = parts[2]
    return out


def apply_loras(item: dict, specs: list[str]) -> None:
    if not specs:
        return
    item["loras"] = [parse_lora_spec(s) for s in specs if s.strip()]


def apply_service(item: dict, args: argparse.Namespace) -> None:
    if args.service:
        item["service"] = args.service
    if args.service_url:
        item["service_url"] = args.service_url
    if args.service_model_url:
        item["service_model_url"] = args.service_model_url
    if args.api:
        item["api"] = args.api
    if args.api_key:
        item["api_key"] = args.api_key
    if args.key_name:
        item["key_name"] = args.key_name


def upsert_gallery_service(data: dict, args: argparse.Namespace) -> None:
    if not (args.service or args.service_url or args.api_key):
        return
    services = data.get("services")
    if not isinstance(services, dict):
        services = {}
        data["services"] = services
    sid = slugify(args.service or "service")
    entry = dict(services.get(sid) or {})
    if args.service:
        entry["name"] = args.service
    if args.service_url:
        entry["url"] = args.service_url
    if args.service_model_url:
        entry["model_url"] = args.service_model_url
    if args.api:
        entry["api"] = args.api
    if args.api_key:
        entry["api_key"] = args.api_key
    if args.key_name:
        entry["key_name"] = args.key_name
    services[sid] = entry


def infer_characters(it: dict) -> list[str]:
    blob = " ".join(
        [
            str(it.get("id") or ""),
            str(it.get("title") or ""),
            str(it.get("note") or ""),
            str(it.get("category") or ""),
            str(it.get("source") or ""),
        ]
    ).lower()
    chars: list[str] = []
    if "bunny" in blob or it.get("category") == "bunny":
        chars.append("Bunny")
    if "terry" in blob:
        chars.append("Terry Crews")
    if re.search(r"black[\s-]?man|\bbbc\b", blob):
        chars.append("Black man")
    iid = str(it.get("id") or "")
    if iid.startswith("male-character") or "male character sheet" in blob:
        chars.append("Male")
    partner_sheet = (
        iid.startswith("male-character")
        or iid.startswith("image3-")
        or "male character sheet" in blob
    )
    if not partner_sheet:
        chars.append("Tigra")
    seen: set[str] = set()
    out: list[str] = []
    for c in chars:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def apply_characters(item: dict, names: list[str], infer: bool = True) -> None:
    chars: list[str] = []
    seen: set[str] = set()
    for n in names or []:
        n = str(n).strip()
        if n and n not in seen:
            seen.add(n)
            chars.append(n)
    if not chars and infer:
        chars = infer_characters(item)
    if chars:
        item["characters"] = chars


def collect_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()
    return (args.prompt or "").strip()


def collect_ref_specs(args: argparse.Namespace) -> list[str]:
    specs = list(args.ref or [])
    if args.refs_json:
        raw = json.loads(Path(args.refs_json).read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            specs.extend(f"{k}|{v}" for k, v in raw.items() if v)
        elif isinstance(raw, list):
            for i, it in enumerate(raw, start=1):
                if isinstance(it, str):
                    specs.append(it)
                elif isinstance(it, dict):
                    src = it.get("source") or it.get("url") or it.get("file") or ""
                    label = it.get("label") or f"ref {i}"
                    if src:
                        specs.append(f"{label}|{src}")
    return specs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?", help="Source image/video path")
    ap.add_argument("--title", default="")
    ap.add_argument("--category", default="scene", choices=["sheet", "scene", "identity", "bunny", "video", "story"])
    ap.add_argument("--model", default="Seedream 5 Pro")
    ap.add_argument("--note", default="")
    ap.add_argument("--cdn", default="", help="optional CDN url")
    ap.add_argument("--pose", default="", help="original pose reference image path")
    ap.add_argument("--id", default="")
    ap.add_argument("--best", action="store_true")
    ap.add_argument("--push", action="store_true", help="git commit + push after add")
    ap.add_argument("--push-only", action="store_true")
    ap.add_argument("--rebuild-only", action="store_true")
    ap.add_argument("--extract-posters", action="store_true", help="extract JPEG posters for video items")
    ap.add_argument("--force-posters", action="store_true", help="rebuild posters even if files exist")
            ap.add_argument("--update-id", default="", help="update prompt/refs on an existing item")
    ap.add_argument("--prompt", default="", help="exact generation prompt")
    ap.add_argument("--prompt-file", default="", help="utf-8 file with exact prompt")
    ap.add_argument("--ref", action="append", default=[], help="repeatable: 'label|url_or_path'")
    ap.add_argument("--refs-json", default="", help="json object {label: url} or list")
    ap.add_argument("--lora", action="append", default=[], help="repeatable: 'name|url' or 'name|url|strength'")
    ap.add_argument("--service", default="", help="service name, e.g. WaveSpeed")
    ap.add_argument("--service-url", default="", help="public site URL for the service")
    ap.add_argument("--service-model-url", default="", help="model playground/docs URL")
    ap.add_argument("--api", default="", help="API base URL")
    ap.add_argument("--api-key", default="", help="API key used for this generation")
    ap.add_argument("--key-name", default="", help="key label in the provider dashboard")
    ap.add_argument("--set-gallery-service", action="store_true", help="also store service+key at gallery root")
    ap.add_argument("--character", action="append", default=[], help="repeatable character name, e.g. Tigra")
    args = ap.parse_args()

    if args.push_only:
        git_push("gallery: update")
        return 0

    if args.extract_posters:
        data = load_manifest()
        n = extract_all_posters(data, force=args.force_posters)
        save_manifest(data)
        print("posters updated", n)
        if args.push:
            git_push("gallery: video posters")
        return 0

    if args.rebuild_only:
        data = load_manifest()
        extract_all_posters(data, force=False)
        save_manifest(data)
        print("manifest touched")
        return 0

    prompt = collect_prompt(args)
    ref_specs = collect_ref_specs(args)

    if args.set_gallery_service and not args.update_id and not args.image:
        data = load_manifest()
        upsert_gallery_service(data, args)
        save_manifest(data)
        print("Gallery service updated")
        if args.push:
            git_push("gallery: service key")
        return 0

    if args.update_id:
        data = load_manifest()
        item = next((it for it in data["items"] if it.get("id") == args.update_id), None)
        if not item:
            print("Not found:", args.update_id, file=sys.stderr)
            return 1
        apply_prompt_and_refs(item, prompt, ref_specs)
        apply_loras(item, args.lora or [])
        apply_service(item, args)
        apply_characters(item, args.character or [])
        if args.set_gallery_service:
            upsert_gallery_service(data, args)
        if args.note:
            item["note"] = args.note
        save_manifest(data)
        print("Updated", args.update_id)
        if args.push:
            git_push(f"gallery: prompt+refs {args.update_id}")
        return 0

    if not args.image:
        ap.error("image path required (or --update-id / --push-only / --rebuild-only)")

    src = Path(args.image)
    if not src.is_file():
        print("Not found:", src, file=sys.stderr)
        return 1

    data = load_manifest()
    if args.category == "story" or src.suffix.lower() == ".md":
        item = publish_story(src, args, data)
        save_manifest(data)
        print("Story", item.get("version"), "->", item["file"])
        print("Reader ->", STORY_HTML)
        if args.push:
            git_push(f"gallery: story {item.get('version') or item['id']}")
        return 0

    iid = args.id or slugify(args.title or src.stem)
    existing = {it["id"] for it in data["items"]}
    base = iid
    n = 2
    while iid in existing:
        iid = f"{base}-{n}"
        n += 1

    if src.suffix.lower() == ".mp4":
        out_name = f"{iid}.mp4"
        out_path = IMG / out_name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Compressing video {src.name} to {out_name}...")
        process_video_file(src, out_path)
        size = (0, 0)
    else:
        out_name = f"{iid}.jpg"
        out_path = IMG / out_name
        size = to_web_jpeg(src, out_path)

    item = {
        "id": iid,
        "file": f"images/{out_name}",
        "source": src.name,
        "title": args.title or src.stem,
        "category": args.category,
        "model": args.model,
        "note": args.note,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "pixels": f"{size[0]}x{size[1]}",
    }
    if src.suffix.lower() == ".mp4":
        ensure_item_poster(item)
    if args.cdn:
        item["cdn"] = args.cdn
    if args.best:
        item["flag"] = "best"
    if args.pose:
        pose_src = Path(args.pose)
        if not pose_src.is_file():
            print("Pose not found:", pose_src, file=sys.stderr)
            return 1
        h = hashlib.sha1(pose_src.read_bytes()).hexdigest()[:12]
        pose_name = f"pose-{slugify(pose_src.stem)}-{h}.jpg"
        pose_path = POSE_DIR / pose_name
        to_web_jpeg(pose_src, pose_path)
        item["pose"] = f"images/poses/{pose_name}"
        print("Pose", pose_name, "->", pose_path)

    apply_prompt_and_refs(item, prompt, ref_specs)
    apply_loras(item, args.lora or [])
    apply_service(item, args)
    apply_characters(item, args.character or [])
    if args.set_gallery_service:
        upsert_gallery_service(data, args)

    data["items"].insert(0, item)
    save_manifest(data)
    print("Added", out_name, size, "->", out_path)
    print("Total items:", len(data["items"]))

    if args.push:
        git_push(f"gallery: add {iid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
