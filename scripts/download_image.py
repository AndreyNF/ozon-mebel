#!/usr/bin/env python3
"""Скачать URL изображения в папку cards/{article}/images/."""

from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def download(url: str, dest: Path, retries: int = 3) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as resp, dest.open("wb") as f:
                while True:
                    chunk = resp.read(1024 * 256)
                    if not chunk:
                        break
                    f.write(chunk)
            if dest.stat().st_size < 1000:
                raise OSError(f"file too small: {dest.stat().st_size}")
            return
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            if dest.exists():
                dest.unlink(missing_ok=True)
    raise RuntimeError(f"download failed after {retries} tries: {url}") from last_err


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("dest")
    args = p.parse_args()
    dest = Path(args.dest)
    download(args.url, dest)
    print(f"OK {dest} ({dest.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
