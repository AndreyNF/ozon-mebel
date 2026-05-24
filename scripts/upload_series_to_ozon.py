#!/usr/bin/env python3
"""Пакетная загрузка серии товаров в Ozon через API."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ozon_build_import import build_import_item, load_config
from ozon_client import poll_import_task, post

ROOT = Path(__file__).resolve().parent.parent


def articles_from_args(args: argparse.Namespace) -> list[str]:
    if args.manifest:
        data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        return [str(a).strip() for a in data["articles"] if str(a).strip()]
    if args.list_file:
        return [
            ln.strip()
            for ln in Path(args.list_file).read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")
        ]
    if args.articles:
        return list(args.articles)
    if args.glob:
        return sorted({p.parent.name for p in ROOT.glob(args.glob) if p.is_file()})
    raise SystemExit("Укажите --manifest, --list-file, --articles или --glob")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", help="series/mori.json")
    parser.add_argument("--list-file", help="Файл: артикул на строку")
    parser.add_argument("--articles", nargs="+")
    parser.add_argument("--glob", help='cards/*/Ц*.row.json')
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "ozon-api-komplekty-mebeli.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--stop-on-error", action="store_true")
    parser.add_argument("--batch-size", type=int, default=1)
    args = parser.parse_args()

    cfg = load_config(args.config)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8")) if args.manifest else {}
    articles = articles_from_args(args)
    defaults = manifest.get("defaults") or {}

    report = {"series": manifest.get("series", ""), "results": []}
    batch_size = max(1, min(100, args.batch_size))

    for start in range(0, len(articles), batch_size):
        chunk = articles[start : start + batch_size]
        items, meta = [], []
        for art in chunk:
            row_path = ROOT / "cards" / art / f"{art}.row.json"
            if not row_path.is_file():
                report["results"].append({"article": art, "error": "нет row.json"})
                continue
            row = json.loads(row_path.read_text(encoding="utf-8"))
            for k, v in defaults.items():
                if not row.get(k):
                    row[k] = v
            try:
                items.append(build_import_item(row, cfg))
                meta.append(art)
            except ValueError as e:
                report["results"].append({"article": art, "error": str(e)})
                if args.stop_on_error:
                    sys.exit(1)

        if not items:
            continue

        if args.dry_run:
            for art, item in zip(meta, items):
                p = ROOT / "cards" / art / f"{art}.api-payload.json"
                p.write_text(json.dumps({"items": [item]}, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"DRY-RUN {art}")
            continue

        resp = post("/v3/product/import", {"items": items})
        task_id = (resp.get("result") or {}).get("task_id")
        info = poll_import_task(int(task_id)) if task_id else {}
        by_offer = {str(x.get("offer_id")): x for x in (info.get("result") or {}).get("items") or []}

        for art in meta:
            st = by_offer.get(art, {})
            entry = {
                "article": art,
                "task_id": task_id,
                "status": st.get("status"),
                "product_id": st.get("product_id"),
                "errors": st.get("errors"),
            }
            report["results"].append(entry)
            (ROOT / "cards" / art / f"{art}.api-upload.json").write_text(
                json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"{art}: {entry.get('status')}")
            if entry.get("errors") and args.stop_on_error:
                sys.exit(1)

        if start + batch_size < len(articles) and args.delay:
            time.sleep(args.delay)

    out = ROOT / "series" / f"upload-report-{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Report -> {out}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
