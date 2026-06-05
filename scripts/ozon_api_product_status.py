#!/usr/bin/env python3
"""Сохранить live-статус товара: /v3/product/info/list + описание."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ozon_client import post

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: ozon_api_product_status.py ARTICLE")

    article = sys.argv[1]
    card = ROOT / "cards" / article

    info = post("/v3/product/info/list", {"offer_id": [article]})
    items = info.get("items") or []
    if not items:
        raise SystemExit(f"Товар {article} не найден в Ozon")

    item = items[0]
    product_id = item.get("id")
    desc_block: dict = {}
    if product_id:
        try:
            desc_block = post(
                "/v1/product/info/description",
                {"offer_id": article, "product_id": int(product_id)},
            )
        except RuntimeError:
            pass

    out = {
        "item": item,
        "description": desc_block,
    }
    path = card / f"ozon-live-status_{article}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    st = (item.get("statuses") or {})
    print(f"offer_id={article} product_id={product_id}")
    print(f"  status_name={st.get('status_name')} validation={st.get('validation_status')}")
    print(f"  has_stock={(item.get('stocks') or {}).get('has_stock')}")
    print(f"OK -> {path}")


if __name__ == "__main__":
    main()
