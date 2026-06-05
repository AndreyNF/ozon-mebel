#!/usr/bin/env python3
"""
Импорт карточки в Ozon: POST /v3/product/import.

При status=skipped после импорта — обновление фото через /v1/product/pictures/import.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ozon_client import poll_import_task, post

ROOT = Path(__file__).resolve().parent.parent


def load_product_id(card: Path, article: str) -> int | None:
    live = card / f"ozon-live-status_{article}.json"
    if not live.is_file():
        return None
    data = json.loads(live.read_text(encoding="utf-8"))
    item = data.get("item") or {}
    pid = item.get("id")
    return int(pid) if pid else None


def pictures_urls(item: dict) -> list[str]:
    """Все фото для /v1/product/pictures/import: первое — главное."""
    primary = (item.get("primary_image") or "").strip()
    extra = [str(u).strip() for u in (item.get("images") or []) if str(u).strip()]
    if primary:
        urls = [primary] + [u for u in extra if u != primary]
    else:
        urls = extra
    return urls


def import_pictures(product_id: int, item: dict) -> dict:
    body = {"product_id": product_id, "images": pictures_urls(item)}
    return post("/v1/product/pictures/import", body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Ozon card via Seller API")
    parser.add_argument("article", help="Артикул cards/{АРТ}")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-wait", action="store_true")
    parser.add_argument("--no-pictures-fallback", action="store_true")
    parser.add_argument("--sync-payload", action="store_true", help="Сначала ozon_sync_import_payload.py")
    args = parser.parse_args()

    article = args.article
    card = ROOT / "cards" / article
    payload_path = card / f"ozon-import-payload_{article}.json"
    if not payload_path.is_file():
        raise SystemExit(f"Нет {payload_path}")

    if args.sync_payload:
        import subprocess

        subprocess.check_call(
            [sys.executable, str(_SCRIPTS / "ozon_sync_import_payload.py"), article]
        )

    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    item = payload["items"][0]

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2)[:2000], "...")
        return

    resp = post("/v3/product/import", payload)
    task_id = (resp.get("result") or {}).get("task_id")
    if not task_id:
        raise SystemExit(f"Нет task_id: {resp}")

    result: dict = {
        "result": {
            "items": [],
            "total": 0,
        }
    }
    info: dict = {}
    if not args.no_wait:
        info = poll_import_task(int(task_id))
        result = info

    items = (info.get("result") or {}).get("items") or []
    if not items:
        items = [{"offer_id": article, "status": "pending", "task_id": task_id}]

    pictures_resp = None
    for it in items:
        status = str(it.get("status", "")).lower()
        print(f"offer_id={it.get('offer_id')} status={status}")
        for err in it.get("errors") or []:
            print(f"  error: {err}")
        if status == "skipped" and not args.no_pictures_fallback:
            pid = it.get("product_id") or load_product_id(card, article)
            if pid:
                print(f"pictures/import product_id={pid} (обход skipped)")
                pictures_resp = import_pictures(int(pid), item)
                print(json.dumps(pictures_resp, ensure_ascii=False)[:500])

    out = card / f"ozon-import-result_{article}.json"
    save = {"result": info.get("result") or {"items": items, "total": len(items)}}
    if pictures_resp:
        save["pictures_import"] = pictures_resp
    save["task_id"] = task_id
    save["submitted_at"] = datetime.now(timezone.utc).isoformat()
    out.write_text(json.dumps(save, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -> {out}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, SystemExit) as e:
        if isinstance(e, SystemExit):
            raise
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
