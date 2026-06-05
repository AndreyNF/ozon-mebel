#!/usr/bin/env python3
"""Выставить остатки FBS: POST /v2/products/stocks."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ozon_client import post

ROOT = Path(__file__).resolve().parent.parent


def warehouse_id() -> int:
    wh = os.environ.get("OZON_WAREHOUSE_ID", "").strip()
    if wh:
        return int(wh)
    resp = post("/v2/warehouse/list", {"limit": 100})
    whs = resp.get("warehouses") or resp.get("result") or []
    fbs = [w for w in whs if "fbs" in str(w.get("name", "")).lower() or w.get("is_rfbs")]
    if not fbs and whs:
        fbs = whs
    if not fbs:
        raise SystemExit(
            "Склады FBS не найдены (POST /v2/warehouse/list пуст). "
            "Создайте склад в ЛК Ozon или задайте OZON_WAREHOUSE_ID в .env"
        )
    wid = fbs[0].get("warehouse_id") or fbs[0].get("id")
    return int(wid)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("articles", nargs="+", help="Артикулы")
    parser.add_argument("--stock", type=int, default=None)
    args = parser.parse_args()

    stock = args.stock
    if stock is None:
        stock = int(os.environ.get("OZON_DEFAULT_STOCK", "1"))

    wid = warehouse_id()
    stocks = [
        {"offer_id": art, "stock": stock, "warehouse_id": wid} for art in args.articles
    ]
    resp = post("/v2/products/stocks", {"stocks": stocks})
    print(json.dumps(resp, ensure_ascii=False, indent=2))
    print(f"OK warehouse_id={wid} stock={stock} x {len(args.articles)}")


if __name__ == "__main__":
    main()
