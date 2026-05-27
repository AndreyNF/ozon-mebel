#!/usr/bin/env python3
"""Проверка карточки перед загрузкой в Ozon."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLOT_PATTERN = re.compile(r"^\d{2}-.+\.(png|jpg|jpeg|webp)$", re.I)


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: validate_ozon_card.py ARTICLE")

    article = sys.argv[1]
    card = ROOT / "cards" / article
    row_path = card / f"{article}.row.json"
    if not row_path.is_file():
        raise SystemExit(f"Нет {row_path}")

    errors: list[str] = []
    row = json.loads(row_path.read_text(encoding="utf-8"))

    manifest_path = card / "images-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        required = int(manifest.get("required_count") or 10)
        files = list(manifest.get("image_files") or [])
    else:
        required = 10
        files = sorted(
            p.name
            for p in (card / "images").glob("*")
            if SLOT_PATTERN.match(p.name)
        )

    if len(files) < required:
        errors.append(f"Фото: {len(files)}/{required} (нужны 01-main … 10-*)")

    main_url = (row.get("Ссылка на главное фото*") or "").strip()
    if not main_url or "jsdelivr" not in main_url and "ozone.ru" not in main_url:
        errors.append("Нет CDN URL главного фото — apply_hosting_urls.py")

    rich = (row.get("Rich-контент JSON") or "").strip()
    if not rich:
        errors.append("Пустой Rich-контент JSON")
    else:
        try:
            data = json.loads(rich)
            if data.get("version") != 0.3:
                errors.append(f"Rich version={data.get('version')} (нужен 0.3)")
        except json.JSONDecodeError as e:
            errors.append(f"Rich JSON: {e}")

    video = (row.get("Озон.Видеообложка: ссылка") or "").strip()
    video_path = card / "video" / "video-cover.mp4"
    if not video and not video_path.is_file():
        errors.append("Нет видеообложки")
    elif video and "?" in video:
        errors.append("В URL видеообложки не должно быть ?v= (Ozon не скачивает)")

    ann = (row.get("Аннотация") or "")
    if len(ann) > 500:
        errors.append(f"Аннотация {len(ann)} симв. (макс. 500)")

    meta = row.get("_meta") or {}
    if not meta.get("description_category_id"):
        errors.append("_meta.description_category_id не задан")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        raise SystemExit(1)

    print(f"OK {article}: {len(files)} фото, Rich, видео, аннотация {len(ann)} симв.")


if __name__ == "__main__":
    main()
