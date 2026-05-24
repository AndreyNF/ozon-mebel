#!/usr/bin/env python3
"""
Реестр выпущенных карточек — проверка дублей перед генерацией.

Использование:
  py scripts/card_registry.py check Ц0081444
  py scripts/card_registry.py check Ц0081444 Ц0081445   # серия
  py scripts/card_registry.py sync                      # обновить из cards/
  py scripts/card_registry.py list
  py scripts/card_registry.py register Ц0081444 --status ready --note "обновление цены"
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "cards" / "registry.json"

STATUSES = ("draft", "ready", "uploaded", "published")


def load_registry() -> dict:
    if not REGISTRY_PATH.is_file():
        return {"version": 1, "articles": {}}
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def save_registry(data: dict) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_article(article: str) -> str:
    return article.strip()


def scan_card_dir(article: str) -> dict:
    """Факты с диска для артикула."""
    card = ROOT / "cards" / article
    if not card.is_dir():
        return {"exists": False}

    row = card / f"{article}.row.json"
    md = card / f"{article}.md"
    xlsx = sorted(card.glob("OZON_UPLOAD_*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
    api = sorted(card.glob(f"{article}.api-upload.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    images = list((card / "images").glob("*")) if (card / "images").is_dir() else []

    status = "draft"
    if xlsx or api:
        status = "uploaded"
    elif row.is_file() and md.is_file():
        status = "ready"

    return {
        "exists": True,
        "path": str(card.relative_to(ROOT)),
        "has_row_json": row.is_file(),
        "has_md": md.is_file(),
        "has_images": len(images) > 0,
        "image_count": len(images),
        "xlsx": [p.name for p in xlsx[:3]],
        "api_upload": api[0].name if api else None,
        "inferred_status": status,
    }


def merge_entry(article: str, reg: dict, scan: dict) -> dict:
    articles = reg.setdefault("articles", {})
    entry = articles.get(article, {})
    now = datetime.now(timezone.utc).isoformat()
    entry.setdefault("article", article)
    entry.setdefault("created_at", entry.get("created_at") or now[:10])
    entry["updated_at"] = now[:10]
    entry["path"] = scan.get("path", f"cards/{article}")
    if scan.get("exists"):
        entry["status"] = entry.get("status") or scan["inferred_status"]
        entry["artifacts"] = {
            "row_json": scan["has_row_json"],
            "md": scan["has_md"],
            "images": scan["image_count"],
            "xlsx": scan["xlsx"],
            "api_upload": scan["api_upload"],
        }
    articles[article] = entry
    return entry


def cmd_check(articles: list[str], *, strict: bool) -> int:
    reg = load_registry()
    blocked = []

    for raw in articles:
        article = normalize_article(raw)
        if not article:
            continue
        scan = scan_card_dir(article)
        reg_entry = reg.get("articles", {}).get(article)
        on_disk = scan.get("exists")
        in_reg = reg_entry is not None

        if not on_disk and not in_reg:
            print(f"OK {article}: карточки нет — можно создавать")
            continue

        lines = [f"DUPLICATE {article}: карточка уже есть — не запускай полную генерацию с нуля"]
        if reg_entry:
            lines.append(f"  реестр: status={reg_entry.get('status', '?')}, updated={reg_entry.get('updated_at', '?')}")
            if reg_entry.get("note"):
                lines.append(f"  note: {reg_entry['note']}")
        if on_disk:
            lines.append(f"  папка: {scan['path']}")
            lines.append(
                f"  файлы: row.json={scan['has_row_json']}, md={scan['has_md']}, "
                f"фото={scan['image_count']}, xlsx={len(scan['xlsx'])}"
            )
            if scan["xlsx"]:
                lines.append(f"  последний Excel: {scan['xlsx'][0]}")
        lines.append("  действия: обновить поля | пересобрать Excel | --force только по запросу пользователя")
        lines.append("  см. docs/card-deduplication.md")
        print("\n".join(lines))
        blocked.append(article)

    if blocked and strict:
        return 2
    return 0 if not blocked else 1


def cmd_sync() -> None:
    reg = load_registry()
    cards_root = ROOT / "cards"
    found = []
    for d in sorted(cards_root.iterdir()) if cards_root.is_dir() else []:
        if not d.is_dir() or d.name.startswith("."):
            continue
        art = d.name
        if (d / f"{art}.row.json").is_file() or (d / f"{art}.md").is_file():
            found.append(art)
            merge_entry(art, reg, scan_card_dir(art))

    save_registry(reg)
    print(f"OK registry -> {REGISTRY_PATH.relative_to(ROOT)} ({len(found)} артикулов)")


def cmd_register(article: str, status: str | None, note: str | None) -> None:
    article = normalize_article(article)
    reg = load_registry()
    scan = scan_card_dir(article)
    entry = merge_entry(article, reg, scan)
    if status:
        if status not in STATUSES:
            raise SystemExit(f"status must be one of: {', '.join(STATUSES)}")
        entry["status"] = status
    if note:
        entry["note"] = note
    entry["registered_at"] = date.today().isoformat()
    save_registry(reg)
    print(f"OK {article} -> status={entry.get('status')}")


def cmd_list() -> None:
    reg = load_registry()
    articles = reg.get("articles") or {}
    if not articles:
        print("(пусто — py scripts/card_registry.py sync)")
        return
    for art in sorted(articles):
        e = articles[art]
        print(f"{art}\t{e.get('status', '?')}\t{e.get('updated_at', '')}\t{e.get('path', '')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Реестр карточек Ozon — антидубли")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check", help="Проверить перед созданием")
    p_check.add_argument("articles", nargs="+", help="Артикулы")
    p_check.add_argument(
        "--strict",
        action="store_true",
        help="exit 2 при дубле (для CI/скриптов)",
    )

    sub.add_parser("sync", help="Синхронизировать реестр из cards/")

    p_reg = sub.add_parser("register", help="Записать/обновить статус")
    p_reg.add_argument("article")
    p_reg.add_argument("--status", choices=STATUSES)
    p_reg.add_argument("--note", default="")

    sub.add_parser("list", help="Список артикулов в реестре")

    args = parser.parse_args()
    if args.cmd == "check":
        sys.exit(cmd_check(args.articles, strict=args.strict))
    if args.cmd == "sync":
        cmd_sync()
    elif args.cmd == "register":
        cmd_register(args.article, args.status, args.note or None)
    elif args.cmd == "list":
        cmd_list()


if __name__ == "__main__":
    main()
