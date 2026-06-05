#!/usr/bin/env python3
"""Реестр карточек Браво Мебель — проверка дублей перед новым пайплайном."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "manufacturers" / "bravo-mebel.json"


def _load() -> dict:
    if not REGISTRY.is_file():
        return {"published": [], "sites": []}
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def normalize_url(url: str) -> str:
    u = unquote(url.strip().rstrip("/"))
    p = urlparse(u)
    path = p.path.rstrip("/").lower()
    return path


def is_bravo_url(url: str) -> bool:
    data = _load()
    host = urlparse(url).netloc.lower().replace("www.", "")
    for site in data.get("sites", []):
        sh = urlparse(site).netloc.lower().replace("www.", "")
        if host == sh:
            return True
    return "tdbravomebel" in host


def find_by_url(url: str) -> dict | None:
    path = normalize_url(url)
    for item in _load().get("published", []):
        for key in ("source_url", "source_url_normalized"):
            val = item.get(key)
            if not val:
                continue
            if normalize_url(val) == path or path.endswith(normalize_url(val)):
                return item
    return None


def find_by_article(article: str) -> dict | None:
    a = article.strip()
    for item in _load().get("published", []):
        if item.get("article") == a or item.get("ozon_offer_id") == a:
            return item
    return None


def list_published() -> list[dict]:
    return _load().get("published", [])


def cmd_check(target: str) -> int:
    if target.startswith("http"):
        if not is_bravo_url(target):
            print(f"WARN: URL не tdbravomebel — реестр Браво может не покрывать: {target}")
        hit = find_by_url(target)
        if hit:
            print("DUPLICATE: карточка уже есть")
            print(f"  article: {hit.get('article')}")
            print(f"  product_id: {hit.get('ozon_product_id')}")
            print(f"  folder: {hit.get('cards_folder')}")
            return 1
        print("OK: новая карточка, можно запускать пайплайн")
        return 0
    hit = find_by_article(target)
    if hit:
        print(f"FOUND: {hit.get('article')} → product_id {hit.get('ozon_product_id')}")
        return 0
    print(f"NOT FOUND: артикул «{target}» не в реестре Браво")
    return 2


def cmd_list() -> int:
    items = list_published()
    if not items:
        print("(пусто)")
        return 0
    for it in items:
        print(f"- {it.get('article')} | id={it.get('ozon_product_id')} | {it.get('source_url', '')}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: py scripts/bravo_card_registry.py list|check URL|АРТИКУЛ")
        return 2
    cmd = sys.argv[1].lower()
    if cmd == "list":
        return cmd_list()
    if cmd == "check" and len(sys.argv) >= 3:
        return cmd_check(sys.argv[2])
    return cmd_check(sys.argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
