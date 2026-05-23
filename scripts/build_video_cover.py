#!/usr/bin/env python3
"""Слайд-шоу MP4 для Ozon «Видеообложка» (8–30 сек, до 20 МБ)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def load_frame(path: Path, width: int, height: int) -> np.ndarray:
    im = Image.open(path).convert("RGB")
    im.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), (255, 255, 255))
    canvas.paste(im, ((width - im.width) // 2, (height - im.height) // 2))
    return np.asarray(canvas)


def build(
    image_paths: list[Path],
    dest: Path,
    *,
    width: int = 1080,
    height: int = 1440,
    fps: int = 24,
    sec_per_slide: float = 3.0,
    quality: int = 7,
) -> None:
    if not image_paths:
        raise SystemExit("Нет входных изображений")
    duration = len(image_paths) * sec_per_slide
    if duration < 8 or duration > 30:
        raise SystemExit(f"Длительность {duration:.1f} сек — нужно 8–30")

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
    print(f"OK {dest} ({size_mb:.2f} MB, {duration:.0f}s, {width}x{height})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("article")
    ap.add_argument("--out", default="video/video-cover.mp4")
    ap.add_argument("--sec", type=float, default=3.0, help="секунд на кадр")
    args = ap.parse_args()

    card = ROOT / "cards" / args.article
    names = [
        "01-main.png",
        "05-angle.png",
        "03-lifestyle.png",
        "04-details.png",
        "09-dimensions.png",
    ]
    paths = [card / "images" / n for n in names]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise SystemExit(f"Нет файлов: {missing}")

    build(paths, card / args.out, sec_per_slide=args.sec)


if __name__ == "__main__":
    main()
