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

COOKTOP_LABELS = {
    "08-cooktop-gas.png": "Модуль 450 мм: газовая панель + духовка\n(не входят в комплект)",
    "09-cooktop-electric.png": "Модуль 450 мм: электрическая панель\n(не входит в комплект)",
    "10-cooktop-induction.png": "Модуль 450 мм: индукционная панель\n(не входит в комплект)",
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


def make_cooktop_slide(main_path: Path, dest: Path, label: str) -> None:
    """Кроп модуля под духовку с оригинала — без AI, тот же цвет фасадов."""
    img = Image.open(main_path).convert("RGB")
    w, h = img.size
    # Нижний правый сектор: зона готовки 450 мм на угловой кухне
    crop = img.crop((int(w * 0.42), int(h * 0.38), int(w * 0.98), int(h * 0.98)))
    tw, th = 1536, 2048
    scale = min(tw / crop.width, (th - 280) / crop.height)
    nw, nh = max(1, int(crop.width * scale)), max(1, int(crop.height * scale))
    resized = crop.resize((nw, nh), Image.Resampling.LANCZOS)
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

    for slot, label in COOKTOP_LABELS.items():
        dest = out_dir / slot
        make_cooktop_slide(main_raw, dest, label)
        manifest_refs[slot] = SANVUT_URLS["main"] + " (crop cooktop)"
        print(f"OK {slot} <- crop + label")

    manifest_path = card / "images-manifest.json"
    manifest = {}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["dealer_slots"] = manifest_refs
    manifest["photo_policy"] = "dealer_only_no_ai_color"
    manifest["dealer_ref"] = SANVUT_URLS["main"]
    manifest["required_count"] = 10
    manifest["image_files"] = sorted(SLOT_URLS.keys()) + sorted(COOKTOP_LABELS.keys())
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    import shutil

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Done: {out_dir}")


if __name__ == "__main__":
    import sys

    apply(sys.argv[1] if len(sys.argv) > 1 else "Кухня Шампань 1000х1800")
