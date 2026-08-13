#!/usr/bin/env python3
"""Add a new generation to the tigress thread gallery and optionally push to GitHub Pages.

Usage:
  python publish-add.py path/to/image.png --title "Pool v6" --category scene --model "Seedream 5 Pro" --note "fix notes"
  python publish-add.py path/to/video.mp4 --title "..." --category video --prompt-file prompt.txt --ref "Image 1|https://..." --push
  python publish-add.py --update-id existing-id --prompt-file prompt.txt --ref "Image 1|url" --push
  python publish-add.py --rebuild-only
  python publish-add.py --push-only

Defaults:
  GAL = C:\\Users\\hebp\\galleries\\tigress-thread-gallery
"""
from __future__ import annotations

import argparse
import hashlib
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
PROMPTS = GAL / "prompts"
MANIFEST = GAL / "manifest.json"
MAX_SIDE = 1800
QUALITY = 86


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


def save_manifest(data: dict) -> None:
    sort_items_newest_first(data)
    data["updated"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="minutes")
    data["local_path"] = str(GAL)
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


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


def apply_prompt_and_refs(item: dict, prompt: str, ref_specs: list[str]) -> None:
    iid = item["id"]
    if prompt:
        item["prompt"] = prompt
        PROMPTS.mkdir(parents=True, exist_ok=True)
        (PROMPTS / f"{iid}.txt").write_text(prompt, encoding="utf-8")
        item["prompt_file"] = f"prompts/{iid}.txt"
    if ref_specs:
        item["refs"] = ingest_refs(iid, ref_specs)


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
    ap.add_argument("--category", default="scene", choices=["sheet", "scene", "identity", "bunny", "video"])
    ap.add_argument("--model", default="Seedream 5 Pro")
    ap.add_argument("--note", default="")
    ap.add_argument("--cdn", default="", help="optional CDN url")
    ap.add_argument("--pose", default="", help="original pose reference image path")
    ap.add_argument("--id", default="")
    ap.add_argument("--best", action="store_true")
    ap.add_argument("--push", action="store_true", help="git commit + push after add")
    ap.add_argument("--push-only", action="store_true")
    ap.add_argument("--rebuild-only", action="store_true")
    ap.add_argument("--update-id", default="", help="update prompt/refs on an existing item")
    ap.add_argument("--prompt", default="", help="exact generation prompt")
    ap.add_argument("--prompt-file", default="", help="utf-8 file with exact prompt")
    ap.add_argument("--ref", action="append", default=[], help="repeatable: 'label|url_or_path'")
    ap.add_argument("--refs-json", default="", help="json object {label: url} or list")
    args = ap.parse_args()

    if args.push_only:
        git_push("gallery: update")
        return 0

    if args.rebuild_only:
        data = load_manifest()
        save_manifest(data)
        print("manifest touched")
        return 0

    prompt = collect_prompt(args)
    ref_specs = collect_ref_specs(args)

    if args.update_id:
        data = load_manifest()
        item = next((it for it in data["items"] if it.get("id") == args.update_id), None)
        if not item:
            print("Not found:", args.update_id, file=sys.stderr)
            return 1
        apply_prompt_and_refs(item, prompt, ref_specs)
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
        shutil.copy2(src, out_path)
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

    data["items"].insert(0, item)
    save_manifest(data)
    print("Added", out_name, size, "->", out_path)
    print("Total items:", len(data["items"]))

    if args.push:
        git_push(f"gallery: add {iid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
