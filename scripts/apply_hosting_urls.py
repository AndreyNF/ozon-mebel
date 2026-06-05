#!/usr/bin/env python3
"""Подставить публичные URL картинок из hosting.config.json в row.json и Excel."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent


def public_url(base: str, rel: str) -> str:
    base = base.rstrip("/")
    rel = rel.replace("\\", "/").lstrip("/")
    return f"{base}/{'/'.join(quote(part, safe='') for part in rel.split('/'))}"


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: apply_hosting_urls.py ARTICLE")

    article = sys.argv[1]
    cfg = json.loads((ROOT / "hosting.config.json").read_text(encoding="utf-8"))
    card = ROOT / "cards" / article
    row_path = card / f"{article}.row.json"
    row = json.loads(row_path.read_text(encoding="utf-8"))
    meta = row.get("_meta") or {}
    base = (meta.get("images_base_url") or cfg.get("public_base_url") or "").strip()
    video_base = (meta.get("video_base_url") or cfg.get("public_base_url") or "").strip()
    if not base:
        raise SystemExit("Укажите public_base_url в hosting.config.json")

    images_dir = card / "images"
    manifest_path = card / "images-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = list(manifest.get("image_files") or [])
    else:
        files = []
    if not files:
        files = sorted(p.name for p in images_dir.glob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})
    if not files:
        raise SystemExit(f"Нет файлов в {images_dir}")

    urls = [public_url(base, f"cards/{article}/images/{name}") for name in files]
    row["Ссылка на главное фото*"] = urls[0]
    row["Ссылки на дополнительные фото"] = "\r\n".join(urls[1:]) if len(urls) > 1 else ""
    row["images"] = urls
    row["image_files"] = files

    video_path = card / "video" / "video-cover.mp4"
    if video_path.exists():
        row["Озон.Видеообложка: ссылка"] = public_url(
            video_base, f"cards/{article}/video/video-cover.mp4"
        )

    row_path.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")

    build = ROOT / "scripts" / "build_upload_excel.py"
    subprocess.check_call([sys.executable, str(build), article])
    print(f"OK {len(urls)} URLs -> {row_path.name}, OZON_UPLOAD_{article}_*.xlsx")
    for u in urls:
        print(u)


if __name__ == "__main__":
    main()
