#!/usr/bin/env python3
"""
Загрузить одну карточку в Ozon через Seller API.

Импорт ставит карточку в очередь проверки Ozon (модерация/валидация).
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

from ozon_build_import import build_payload, load_config
from ozon_client import poll_import_task, post

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload one Ozon card via Seller API")
    parser.add_argument("article", help="Артикул (cards/{АРТИКУЛ})")
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "ozon-api-komplekty-mebeli.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-wait", action="store_true")
    args = parser.parse_args()

    row_path = ROOT / "cards" / args.article / f"{args.article}.row.json"
    if not row_path.is_file():
        raise SystemExit(f"Нет {row_path}")

    row = json.loads(row_path.read_text(encoding="utf-8"))
    cfg = load_config(args.config)
    payload = build_payload(row, cfg)

    payload_path = row_path.parent / f"{args.article}.api-payload.json"
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.dry_run:
        print(f"DRY-RUN -> {payload_path}")
        return

    resp = post("/v3/product/import", payload)
    task_id = (resp.get("result") or {}).get("task_id")
    if not task_id:
        raise SystemExit(f"Нет task_id: {resp}")

    result = {
        "article": args.article,
        "task_id": task_id,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "import_response": resp,
    }
    if not args.no_wait:
        info = poll_import_task(int(task_id))
        result["import_info"] = info
        for it in (info.get("result") or {}).get("items") or []:
            print(f"offer_id={it.get('offer_id')} status={it.get('status')}")
            for err in it.get("errors") or []:
                print(f"  error: {err}")

    report = row_path.parent / f"{args.article}.api-upload.json"
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK task_id={task_id} -> {report}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
