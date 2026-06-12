#!/usr/bin/env python3
"""Sanvut кухня: оригиналы sanvut.ru → 10 PNG 3:4 без AI (точная цветовая гамма)."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (compatible; ozon-mebel/1.0)"

# Кухня Шампань 1000х1800 — фото с карточки производителя
SANVUT_URLS = {
    "main": "https://sanvut.ru/upload/dev2fun.imagecompress/webp/iblock/da8/jhzu9912ai37ncj41gfgf2r36453y98p.webp",
    "schematic": "https://sanvut.ru/upload/dev2fun.imagecompress/webp/iblock/096/voc4efgsfe9ffce0juiz3fyhzds9vxpv.webp",
    "alt": "https://sanvut.ru/upload/dev2fun.imagecompress/webp/iblock/5c5/im8kwe22dvxqafqjpyn4ml3rqkkv28kw.webp",
    "marble": "https://sanvut.ru/upload/dev2fun.imagecompress/webp/iblock/5d4/mnqeo7gevkmggqagmugzh1t7gc2siweu.webp",
}

SLOT_URLS: dict[str, str] = {
    "01-main.png": SANVUT_URLS["main"],
    "02-infographic.png": SANVUT_URLS["schematic"],
    "03-lifestyle.png": SANVUT_URLS["alt"],
    "04-details.png": SANVUT_URLS["marble"],
    "05-angle.png": SANVUT_URLS["alt"],
    "06-layout.png": SANVUT_URLS["schematic"],
    "07-utp.png": SANVUT_URLS["main"],
}

EXTRA_SLOTS = {
    "08-cooktop.png": "Модуль под варку: плита и духовка\n(не входят в комплект)",
    "09-sink.png": "Модуль под мойку\n(мойка не входит в комплект)",
    "10-assembly.png": "Поставка в разборе: модули, фурнитура, инструкция",
}


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp, dest.open("wb") as f:
        f.write(resp.read())


def fit_3x4(
    src: Path,
    dest: Path,
    *,
    crop_frac: tuple[float, float, float, float] | None = None,
    width: int = 1536,
    height: int = 2048,
) -> None:
    img = Image.open(src).convert("RGB")
    if crop_frac:
        l, t, r, b = crop_frac
        w, h = img.size
        img = img.crop((int(w * l), int(h * t), int(w * r), int(h * b)))
    tw, th = width, height
    scale = min(tw / img.width, th / img.height)
    nw, nh = max(1, int(img.width * scale)), max(1, int(img.height * scale))
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (tw, th), (255, 255, 255))
    canvas.paste(resized, ((tw - nw) // 2, (th - nh) // 2))
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, "PNG", optimize=True)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_labeled_slide(
    main_path: Path,
    dest: Path,
    label: str,
    *,
    crop: tuple[float, float, float, float] = (0.42, 0.38, 0.98, 0.98),
) -> None:
    """Кроп сектора кухни с оригинала — без AI, тот же цвет фасадов."""
    img = Image.open(main_path).convert("RGB")
    w, h = img.size
    l, t, r, b = crop
    crop_img = img.crop((int(w * l), int(h * t), int(w * r), int(h * b)))
    tw, th = 1536, 2048
    scale = min(tw / crop_img.width, (th - 280) / crop_img.height)
    nw, nh = max(1, int(crop_img.width * scale)), max(1, int(crop_img.height * scale))
    resized = crop_img.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (tw, th), (255, 255, 255))
    canvas.paste(resized, ((tw - nw) // 2, max(40, (th - 280 - nh) // 2)))

    draw = ImageDraw.Draw(canvas)
    font = _font(44)
    lines = label.split("\n")
    line_h = 56
    banner_h = 24 + line_h * len(lines)
    y0 = th - banner_h - 24
    draw.rectangle((48, y0, tw - 48, th - 24), fill=(40, 40, 40, 230))
    for i, line in enumerate(lines):
        draw.text((72, y0 + 16 + i * line_h), line, fill=(255, 255, 255), font=font)

    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, "PNG", optimize=True)


def apply(article: str = "Кухня Шампань 1000х1800") -> None:
    card = ROOT / "cards" / article
    out_dir = card / "images"
    tmp = card / ".dealer-tmp"
    tmp.mkdir(exist_ok=True)

    cache: dict[str, Path] = {}
    manifest_refs: dict[str, str] = {}

    for slot, url in SLOT_URLS.items():
        key = url.rsplit("/", 1)[-1]
        if key not in cache:
            raw = tmp / key
            download(url, raw)
            cache[key] = raw
        dest = out_dir / slot
        crop = (0.08, 0.05, 0.92, 0.95) if slot == "07-utp.png" else None
        fit_3x4(cache[key], dest, crop_frac=crop)
        manifest_refs[slot] = url
        print(f"OK {slot} <- {url}")

    main_raw = tmp / SANVUT_URLS["main"].rsplit("/", 1)[-1]
    if not main_raw.is_file():
        download(SANVUT_URLS["main"], main_raw)

    crop_by_slot: dict[str, tuple[float, float, float, float]] = {
        "08-cooktop.png": (0.42, 0.38, 0.98, 0.98),
        "09-sink.png": (0.05, 0.38, 0.55, 0.98),
        "10-assembly.png": (0.08, 0.05, 0.92, 0.95),
    }

    for slot, label in EXTRA_SLOTS.items():
        dest = out_dir / slot
        if slot == "10-assembly.png":
            fit_3x4(main_raw, dest, crop_frac=crop_by_slot[slot])
            manifest_refs[slot] = SANVUT_URLS["schematic"]
        else:
            make_labeled_slide(main_raw, dest, label, crop=crop_by_slot[slot])
            manifest_refs[slot] = SANVUT_URLS["main"] + f" (crop {slot})"
        print(f"OK {slot}")

    manifest_path = card / "images-manifest.json"
    manifest = {}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["dealer_slots"] = manifest_refs
    manifest["photo_policy"] = "dealer_only_no_ai_color"
    manifest["dealer_ref"] = SANVUT_URLS["main"]
    manifest["required_count"] = 10
    manifest["image_files"] = sorted(SLOT_URLS.keys()) + sorted(EXTRA_SLOTS.keys())
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    import shutil

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Done: {out_dir}")


if __name__ == "__main__":
    import sys

    apply(sys.argv[1] if len(sys.argv) > 1 else "Кухня Шампань 1000х1800")
