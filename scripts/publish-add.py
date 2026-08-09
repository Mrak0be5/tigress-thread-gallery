#!/usr/bin/env python3
"""Add a new generation to the tigress thread gallery and optionally push to GitHub Pages.

Usage:
  python publish-add.py path/to/image.png --title "Pool v6" --category scene --model "Seedream 5 Pro" --note "fix notes" --cdn "https://..."
  python publish-add.py path/to/image.png --title "..." --push
  python publish-add.py --rebuild-only   # just regenerate index from manifest (noop)
  python publish-add.py --push-only      # git add/commit/push existing tree

Defaults:
  GAL = C:\\Users\\hebp\\galleries\\tigress-thread-gallery
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

GAL = Path(r"C:\Users\hebp\galleries\tigress-thread-gallery")
IMG = GAL / "images"
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


def save_manifest(data: dict) -> None:
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?", help="Source image path")
    ap.add_argument("--title", default="")
    ap.add_argument("--category", default="scene", choices=["sheet", "scene", "identity", "bunny"])
    ap.add_argument("--model", default="Seedream 5 Pro")
    ap.add_argument("--note", default="")
    ap.add_argument("--cdn", default="")
    ap.add_argument("--id", default="")
    ap.add_argument("--best", action="store_true")
    ap.add_argument("--push", action="store_true", help="git commit + push after add")
    ap.add_argument("--push-only", action="store_true")
    ap.add_argument("--rebuild-only", action="store_true")
    args = ap.parse_args()

    if args.push_only:
        git_push("gallery: update")
        return 0

    if args.rebuild_only:
        data = load_manifest()
        save_manifest(data)
        print("manifest touched")
        return 0

    if not args.image:
        ap.error("image path required (or --push-only / --rebuild-only)")

    src = Path(args.image)
    if not src.is_file():
        print("Not found:", src, file=sys.stderr)
        return 1

    data = load_manifest()
    iid = args.id or slugify(args.title or src.stem)
    # uniqueness
    existing = {it["id"] for it in data["items"]}
    base = iid
    n = 2
    while iid in existing:
        iid = f"{base}-{n}"
        n += 1

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

    data["items"].append(item)
    save_manifest(data)
    print("Added", out_name, size, "->", out_path)
    print("Total items:", len(data["items"]))

    if args.push:
        git_push(f"gallery: add {iid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
