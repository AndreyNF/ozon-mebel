#!/usr/bin/env python3
"""Собрать тело POST /v3/product/import из {АРТИКУЛ}.row.json."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "config" / "ozon-api-komplekty-mebeli.json"


def load_config(path: Path | None = None) -> dict[str, Any]:
    path = path or DEFAULT_CONFIG
    return json.loads(path.read_text(encoding="utf-8"))


def _split_photos(row: dict[str, Any]) -> tuple[str, list[str]]:
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


def _attr_value(spec: dict[str, Any], raw: Any, cfg: dict[str, Any]) -> list[dict[str, Any]]:
    text = str(raw).strip()
    if not text:
        return []
    entry: dict[str, Any] = {"value": text}
    if spec.get("dictionary"):
        key = f"{spec['id']}:{text}"
        dmap = cfg.get("dictionary_value_hints") or {}
        if key in dmap:
            entry["dictionary_value_id"] = int(dmap[key])
        else:
            entry["dictionary_value_id"] = 0
    return [entry]


def resolve_type_id(row: dict[str, Any], cfg: dict[str, Any]) -> int:
    meta = row.get("_meta") or {}
    api = meta.get("api") or {}
    if api.get("type_id"):
        return int(api["type_id"])
    type_name = (row.get("Тип*") or row.get("Тип") or "").strip()
    tmap = cfg.get("type_name_to_type_id") or {}
    if type_name and type_name in tmap and int(tmap[type_name]) > 0:
        return int(tmap[type_name])
    raise ValueError(
        f"Не задан type_id для типа «{type_name}». "
        "Запустите: py scripts/ozon_sync_config.py "
        "или добавьте _meta.api.type_id в row.json"
    )


def build_import_item(row: dict[str, Any], cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    cfg = cfg or load_config()
    article = (row.get("Артикул*") or row.get("Артикул") or "").strip()
    if not article:
        raise ValueError("В row.json нет Артикул*")

    name = (row.get("Название товара") or "").strip()
    if not name:
        raise ValueError(f"{article}: пустое «Название товара»")

    type_id = resolve_type_id(row, cfg)
    main_img, images = _split_photos(row)
    if not main_img:
        raise ValueError(f"{article}: нужно главное фото")

    vat_key = (row.get("НДС, %*") or row.get("НДС, %") or "Не облагается").strip()
    vat = (cfg.get("vat_map") or {}).get(vat_key, "0")

    price = row.get("Цена, руб.*") or row.get("Цена, руб.")
    old_price = row.get("Цена до скидки, руб.") or ""
    if price in ("", None, "[УТОЧНИТЬ]"):
        raise ValueError(f"{article}: укажите цену перед отправкой в Ozon")

    attributes: list[dict[str, Any]] = []
    for field_name, spec in (cfg.get("fields") or {}).items():
        if field_name.startswith("_"):
            continue
        raw = row.get(field_name)
        if raw is None or raw == "" or raw == "[УТОЧНИТЬ]":
            continue
        values = _attr_value(spec, raw, cfg)
        if values:
            attributes.append({"complex_id": 0, "id": int(spec["id"]), "values": values})

    item: dict[str, Any] = {
        "offer_id": article,
        "name": name,
        "description_category_id": int(cfg["description_category_id"]),
        "type_id": type_id,
        "attributes": attributes,
        "complex_attributes": [],
        "currency_code": cfg.get("currency_code", "RUB"),
        "price": str(int(price) if isinstance(price, float) else price),
        "vat": vat,
        "weight": int(row.get("Вес в упаковке, г*") or row.get("Вес в упаковке, г") or 0),
        "weight_unit": cfg.get("weight_unit", "g"),
        "width": int(row.get("Ширина упаковки, мм*") or 0),
        "height": int(row.get("Высота упаковки, мм*") or 0),
        "depth": int(row.get("Длина упаковки, мм*") or 0),
        "dimension_unit": cfg.get("dimension_unit", "mm"),
        "primary_image": main_img,
        "images": images[:14],
        "images360": [],
        "color_image": "",
        "pdf_list": [],
    }
    if old_price not in ("", None, "[УТОЧНИТЬ]"):
        item["old_price"] = str(int(old_price) if isinstance(old_price, float) else old_price)

    barcode = (row.get("Штрихкод (Серийный номер / EAN)") or "").strip()
    if barcode:
        item["barcode"] = barcode

    return item


def build_payload(row: dict[str, Any], cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"items": [build_import_item(row, cfg)]}
