#!/usr/bin/env python3
"""Подтянуть type_id и id атрибутов из Ozon API в config."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ozon_client import post

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "ozon-api-komplekty-mebeli.json"


def fetch_type_map(description_category_id: int) -> dict[str, int]:
    tree = post("/v1/description-category/tree", {"language": "RU"})
    result = tree.get("result") or []
    found: dict[str, int] = {}

    def dig(nodes: list) -> None:
        for n in nodes:
            dcid = n.get("description_category_id") or n.get("category_id")
            if int(dcid or 0) == description_category_id:
                for ch in n.get("children") or []:
                    tname = (ch.get("type_name") or ch.get("category_name") or "").strip()
                    tid = ch.get("type_id") or ch.get("description_category_id")
                    if tname and tid:
                        found[tname] = int(tid)
                    dig(ch.get("children") or [])
            else:
                dig(n.get("children") or [])

    dig(result if isinstance(result, list) else [result])
    return found


def fetch_attributes(description_category_id: int, type_id: int) -> dict[str, dict[str, Any]]:
    resp = post(
        "/v1/description-category/attribute",
        {
            "description_category_id": description_category_id,
            "type_id": type_id,
            "language": "RU",
        },
    )
    fields: dict[str, dict[str, Any]] = {}
    for attr in resp.get("result") or []:
        name = (attr.get("name") or "").strip()
        aid = attr.get("id")
        if name and aid:
            entry: dict[str, Any] = {"id": int(aid)}
            if attr.get("dictionary_id"):
                entry["dictionary"] = True
            fields[name] = entry
    return fields


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--type-name", default="Шкаф")
    args = parser.parse_args()

    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    dcid = int(cfg["description_category_id"])

    types = fetch_type_map(dcid)
    if types:
        cfg["type_name_to_type_id"] = types
        print(f"types: {len(types)}")

    type_id = types.get(args.type_name)
    if type_id:
        fields = fetch_attributes(dcid, type_id)
        if fields:
            cfg["fields"] = fields
            print(f"attributes: {len(fields)}")
    else:
        print(f"WARN: тип «{args.type_name}» не найден")

    args.config.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -> {args.config}")


if __name__ == "__main__":
    main()
