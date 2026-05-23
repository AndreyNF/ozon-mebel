#!/usr/bin/env python3
"""Extract product image URLs from 33komoda product page."""

from __future__ import annotations

import re
import sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"


def fetch_urls(page_url: str) -> list[str]:
    req = urllib.request.Request(page_url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        html = resp.read().decode("utf-8", "replace")
    rel = re.findall(r"/upload/[^\"'\s>]+\.(?:jpg|jpeg|png|webp)", html, re.I)
    absu = re.findall(r"https?://[^\"'\s>]+\.(?:jpg|jpeg|png|webp)", html, re.I)
    out: list[str] = []
    seen: set[str] = set()
    for u in absu + [f"https://33komoda.ru{x}" for x in rel]:
        if "upload" not in u.lower():
            continue
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else (
        "https://33komoda.ru/catalog/krovati_i_osnovaniya/"
        "krovat_lori_1400_2000_mm_s_ortopedicheskim_osnovaniem_i_yashchikami_dub_seryy_belyy/"
    )
    for u in fetch_urls(url):
        print(u)


if __name__ == "__main__":
    main()
