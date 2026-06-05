#!/usr/bin/env python3
"""Уведомления в Telegram (Bot API, stdlib)."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv() -> None:
    path = ROOT / ".env"
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def send_message(text: str, *, chat_id: str | None = None, parse_mode: str = "HTML") -> bool:
    load_dotenv()
    token = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    chat = (chat_id or os.environ.get("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = urllib.parse.urlencode(
        {
            "chat_id": chat,
            "text": text[:4000],
            "parse_mode": parse_mode,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return bool(data.get("ok"))


def format_comms_summary(results: list[dict]) -> str:
    if not results:
        return "Ozon comms: новых обращений нет."
    lines = ["<b>Ozon comms</b>"]
    for r in results:
        kind = r.get("kind", "?")
        action = r.get("action", "?")
        if action.startswith("skip"):
            continue
        lines.append(f"\n<b>{kind}</b> → {action}")
        if r.get("article"):
            lines.append(f"Артикул: {r['article']}")
        if r.get("incoming"):
            lines.append(f"Вход: {r['incoming'][:200]}")
        if r.get("reply"):
            lines.append(f"Ответ: {r['reply'][:300]}")
    return "\n".join(lines) if len(lines) > 1 else "Ozon comms: только системные чаты / пропуски."
