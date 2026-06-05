#!/usr/bin/env python3
"""Скачать фото дилера Браво и привести к 3:4 PNG без AI (точный цвет)."""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import colorsys

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def _color_stats(path: Path) -> dict[str, float]:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    crop = im.crop((int(w * 0.15), int(h * 0.15), int(w * 0.85), int(h * 0.85)))
    pixels = list(crop.resize((80, 80)).getdata())
    blues = greens = 0
    for r, g, b in pixels:
        hue, sat, _ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        hue *= 360
        if 90 < hue < 170 and sat > 0.12:
            greens += 1
        elif 180 < hue < 260 and sat > 0.12:
            blues += 1
    n = len(pixels) or 1
    return {"blue_pct": blues / n * 100, "green_pct": greens / n * 100}


def assert_sapphire_color(path: Path, slot: str) -> None:
    """Отсечь зелёный самшит / чужие расцветки с галереи tdbravomebel."""
    s = _color_stats(path)
    if s["green_pct"] > 8 and s["green_pct"] > s["blue_pct"]:
        raise SystemExit(f"COLOR FAIL {slot}: похоже на зелёный ({s}), не Сапфировый")
    if s["blue_pct"] < 3 and "main" in slot or slot.startswith("01"):
        raise SystemExit(f"COLOR FAIL {slot}: мало синего ({s}), проверьте референс")
UA = "Mozilla/5.0 (compatible; ozon-mebel/1.0)"


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp, dest.open("wb") as f:
        f.write(resp.read())


def fit_3x4(src: Path, dest: Path, width: int = 1536, height: int = 2048) -> None:
    img = Image.open(src).convert("RGB")
    tw, th = width, height
    scale = min(tw / img.width, th / img.height)
    nw, nh = max(1, int(img.width * scale)), max(1, int(img.height * scale))
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (tw, th), (255, 255, 255))
    canvas.paste(resized, ((tw - nw) // 2, (th - nh) // 2))
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, "PNG", optimize=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Браво: dealer JPEG → cards/.../images/NN-slot.png")
    ap.add_argument("article", help="Папка cards/{article}")
    ap.add_argument(
        "mapping_json",
        help='JSON: {"01-main.png": "https://...", ...}',
    )
    args = ap.parse_args()

    card = ROOT / "cards" / args.article
    mapping: dict[str, str] = json.loads(args.mapping_json)
    tmp = card / ".dealer-tmp"
    tmp.mkdir(exist_ok=True)

    out_dir = card / "images"
    manifest_refs: dict[str, str] = {}
    for slot, url in mapping.items():
        raw = tmp / Path(url).name
        if not raw.suffix:
            raw = raw.with_suffix(".jpg")
        download(url, raw)
        dest = out_dir / slot
        fit_3x4(raw, dest)
        assert_sapphire_color(dest, slot)
        manifest_refs[slot] = url
        print(f"OK {slot} <- {url} color={_color_stats(dest)}")

    manifest_path = card / "images-manifest.json"
    manifest = {}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["dealer_slots"] = manifest_refs
    manifest["photo_policy"] = "dealer_only_no_ai_color"
    manifest["required_count"] = manifest.get("required_count", 10)
    manifest["image_files"] = sorted(mapping.keys())
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    import shutil

    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
