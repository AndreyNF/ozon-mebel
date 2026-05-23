#!/usr/bin/env python3
"""Слайд-шоу MP4 для Ozon «Видеообложка» (8–30 сек, до 20 МБ)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote

import imageio.v2 as imageio
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

# Приоритет кадров для видео (5 шт. × 3 сек = 15 сек)
SLIDE_PRIORITY = [
    re.compile(r"^01-main"),
    re.compile(r"^(05-angle|10-angle|06-angle)"),
    re.compile(r"^03-lifestyle"),
    re.compile(r"^(02-infographic|06-layout|05-interior)"),
    re.compile(r"^(09-dimensions|05-dimensions|07-utp)"),
]

PER_ARTICLE: dict[str, list[str]] = {
    "Ц0050573": [
        "01-main.png",
        "05-angle.png",
        "03-lifestyle.png",
        "04-details.png",
        "09-dimensions.png",
    ],
    "Ц0081444": [
        "01-main.png",
        "02-infographic.png",
        "05-interior-layout.png",
        "10-angle-ai.png",
        "05-dimensions-ref.jpg",
    ],
    "Ц0111571": [
        "01-main.png",
        "05-angle.png",
        "03-lifestyle.png",
        "06-layout.png",
        "02-infographic.png",
    ],
}


def load_frame(path: Path, width: int, height: int) -> np.ndarray:
    im = Image.open(path).convert("RGB")
    im.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), (255, 255, 255))
    canvas.paste(im, ((width - im.width) // 2, (height - im.height) // 2))
    return np.asarray(canvas)


def pick_slides(article: str, images_dir: Path) -> list[Path]:
    if article in PER_ARTICLE:
        names = PER_ARTICLE[article]
        paths = [images_dir / n for n in names]
        missing = [p.name for p in paths if not p.exists()]
        if not missing:
            return paths

    files = sorted(
        p
        for p in images_dir.iterdir()
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        and "ref" not in p.name.lower()
        and "rejected" not in p.name.lower()
    )
    chosen: list[Path] = []
    used: set[str] = set()
    for pat in SLIDE_PRIORITY:
        for f in files:
            if f.name in used:
                continue
            if pat.search(f.name):
                chosen.append(f)
                used.add(f.name)
                break
        if len(chosen) >= 5:
            break
    if len(chosen) < 3:
        for f in files:
            if f.name not in used:
                chosen.append(f)
                used.add(f.name)
            if len(chosen) >= 5:
                break
    return chosen[:5]


def ensure_local_images(card: Path, article: str) -> None:
    """Скачать с GitHub недостающие файлы из row.json."""
    row_path = card / f"{article}.row.json"
    if not row_path.exists():
        return
    row = json.loads(row_path.read_text(encoding="utf-8"))
    urls = list(row.get("images") or [])
    primary = row.get("Ссылка на главное фото*")
    if primary and primary not in urls:
        urls.insert(0, primary)
    extra = row.get("Ссылки на дополнительные фото") or ""
    for u in str(extra).replace("\r", "").split("\n"):
        u = u.strip()
        if u and u not in urls:
            urls.append(u)

    images_dir = card / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    from download_image import download  # noqa: PLC0415

    for url in urls:
        if not url:
            continue
        base = unquote(url.split("?")[0].rstrip("/").split("/")[-1])
        dest = images_dir / base
        if dest.exists() and dest.stat().st_size > 1000:
            continue
        try:
            download(url.split("?")[0], dest)
            print(f"  downloaded {dest.name}")
        except Exception as exc:  # noqa: BLE001
            print(f"  skip {base}: {exc}")


def build(
    image_paths: list[Path],
    dest: Path,
    *,
    width: int = 1080,
    height: int = 1440,
    fps: int = 24,
    sec_per_slide: float | None = None,
    quality: int = 7,
) -> None:
    if not image_paths:
        raise SystemExit("Нет входных изображений")
    n = len(image_paths)
    if sec_per_slide is None:
        sec_per_slide = max(8 / n, min(3.0, 30 / n))
    duration = n * sec_per_slide
    if duration < 8 or duration > 30:
        raise SystemExit(f"Длительность {duration:.1f} сек — нужно 8–30 ({n} кадров)")

    dest.parent.mkdir(parents=True, exist_ok=True)
    frames_per_slide = max(1, int(round(sec_per_slide * fps)))
    writer = imageio.get_writer(
        dest,
        fps=fps,
        codec="libx264",
        quality=quality,
        macro_block_size=1,
        ffmpeg_params=["-pix_fmt", "yuv420p"],
    )
    try:
        for path in image_paths:
            frame = load_frame(path, width, height)
            for _ in range(frames_per_slide):
                writer.append_data(frame)
    finally:
        writer.close()

    size_mb = dest.stat().st_size / (1024 * 1024)
    if size_mb > 20:
        raise SystemExit(f"Файл {size_mb:.1f} МБ — лимит Ozon 20 МБ")
    print(f"OK {dest} ({size_mb:.2f} MB, {duration:.0f}s, {width}x{height}, {n} slides)")


def video_public_url(article: str, base: str) -> str:
    from apply_hosting_urls import public_url  # noqa: PLC0415

    return public_url(base, f"cards/{article}/video/video-cover.mp4")


def patch_row_video_url(article: str, url: str) -> None:
    row_path = ROOT / "cards" / article / f"{article}.row.json"
    row = json.loads(row_path.read_text(encoding="utf-8"))
    row["Озон.Видеообложка: ссылка"] = url
    meta = row.setdefault("_meta", {})
    meta["video_cover"] = "video/video-cover.mp4"
    row_path.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"row.json: Озон.Видеообложка: ссылка")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("article")
    ap.add_argument("--out", default="video/video-cover.mp4")
    ap.add_argument("--sec", type=float, default=None, help="секунд на кадр (auto если не задано)")
    ap.add_argument("--download", action="store_true", help="скачать фото с GitHub из row.json")
    ap.add_argument("--patch-row", action="store_true", help="прописать URL видео в row.json")
    args = ap.parse_args()

    card = ROOT / "cards" / args.article
    if args.download or not (card / "images").exists():
        print("Проверка локальных фото…")
        ensure_local_images(card, args.article)

    paths = pick_slides(args.article, card / "images")
    missing = [p.name for p in paths if not p.exists()]
    if missing:
        raise SystemExit(f"Нет файлов: {missing}. Запустите с --download")

    build(paths, card / args.out, sec_per_slide=args.sec)

    if args.patch_row:
        cfg = json.loads((ROOT / "hosting.config.json").read_text(encoding="utf-8"))
        base = (cfg.get("public_base_url") or "").strip()
        if not base:
            raise SystemExit("public_base_url в hosting.config.json")
        patch_row_video_url(args.article, video_public_url(args.article, base))


if __name__ == "__main__":
    main()
