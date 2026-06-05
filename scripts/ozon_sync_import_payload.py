#!/usr/bin/env python3
"""Обновить ozon-import-payload из row.json (фото, Rich, видео, цены)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ROW_TO_ATTR_ID = {
    "Аннотация": 4191,
    "#Хештеги": 23171,
    "Rich-контент JSON": 11254,
    "Озон.Видеообложка: ссылка": 21845,
    "Высота, см": 10174,
    "Ширина, см": 10175,
    "Глубина, см": 10176,
    "Минимальный возраст ребенка": 13214,
    "Максимальный возраст ребенка": 13215,
    "Состав комплекта": 23277,
}


def split_photos(row: dict) -> tuple[str, list[str]]:
    main = (row.get("Ссылка на главное фото*") or "").strip()
    extra_raw = row.get("Ссылки на дополнительные фото") or ""
    extra = [u.strip() for u in re.split(r"[\r\n]+", str(extra_raw)) if u.strip()]
    if row.get("images"):
        imgs = [str(u).strip() for u in row["images"] if str(u).strip()]
        if imgs:
            main = main or imgs[0]
            for u in imgs[1:]:
                if u not in extra and u != main:
                    extra.append(u)
    extra = [u for u in extra if u != main]
    return main, extra


def set_attr(
    attrs: list[dict],
    attr_id: int,
    value: str,
    *,
    dictionary_value_id: int | None = None,
) -> None:
    entry: dict = {"value": value}
    if dictionary_value_id:
        entry["dictionary_value_id"] = int(dictionary_value_id)
    for a in attrs:
        if int(a.get("id", 0)) == attr_id:
            a["values"] = [entry]
            return
    attrs.append({"complex_id": 0, "id": attr_id, "values": [entry]})


def sync_payload(row: dict, payload: dict) -> dict:
    meta = row.get("_meta") or {}
    item = payload["items"][0]
    item["name"] = (row.get("Название товара") or item.get("name") or "").strip()
    item["price"] = str(int(row.get("Цена, руб.*") or row.get("Цена, руб.") or item["price"]))
    old = row.get("Цена до скидки, руб.")
    if old not in ("", None):
        item["old_price"] = str(int(old))

    if meta.get("description_category_id"):
        item["description_category_id"] = int(meta["description_category_id"])
    if meta.get("type_id"):
        item["type_id"] = int(meta["type_id"])

    w_mm = int(row.get("Ширина упаковки, мм*") or 0)
    h_mm = int(row.get("Высота упаковки, мм*") or 0)
    d_mm = int(row.get("Длина упаковки, мм*") or 0)
    if w_mm:
        item["width"] = max(1, w_mm // 10)
        item["height"] = max(1, h_mm // 10)
        item["depth"] = max(1, d_mm // 10)
        item["dimension_unit"] = "cm"
    item["weight"] = int(row.get("Вес в упаковке, г*") or item.get("weight") or 0)

    main, extra = split_photos(row)
    if not main:
        raise SystemExit("Нет главного фото в row.json — запустите apply_hosting_urls.py")
    item["primary_image"] = main
    item["images"] = extra[:14]

    attrs = item.setdefault("attributes", [])
    dict_ids = (row.get("_meta") or {}).get("ozon_dictionary") or {}
    for field, attr_id in ROW_TO_ATTR_ID.items():
        val = row.get(field)
        if val:
            set_attr(
                attrs,
                attr_id,
                str(val).strip(),
                dictionary_value_id=dict_ids.get(field),
            )

    return payload


def main() -> None:
    article = sys.argv[1]
    card = ROOT / "cards" / article
    row_path = card / f"{article}.row.json"
    payload_path = card / f"ozon-import-payload_{article}.json"
    if not row_path.is_file():
        raise SystemExit(f"Нет {row_path}")
    if not payload_path.is_file():
        raise SystemExit(f"Нет {payload_path} — сначала создайте payload вручную или через API")

    row = json.loads(row_path.read_text(encoding="utf-8"))
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    payload = sync_payload(row, payload)
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -> {payload_path}")


if __name__ == "__main__":
    main()
