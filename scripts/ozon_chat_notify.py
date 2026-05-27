#!/usr/bin/env python3
"""
Проверить чаты Ozon и отправить в Telegram непрочитанное от покупателей.

Использование:
  python3 scripts/ozon_chat_notify.py
  python3 scripts/ozon_chat_notify.py --dry-run
"""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ozon_client import post
from telegram_client import send_message

CUSTOMER_TYPES = {"Customer", "customer"}


def message_text(msg: dict) -> str:
    parts = msg.get("data") or []
    if isinstance(parts, list):
        return "\n".join(str(p) for p in parts if p).strip()
    return str(parts).strip()


def check_chats(*, dry_run: bool = False) -> int:
    listing = post("/v3/chat/list", {"filter": {}, "limit": 50})
    alerts: list[str] = []

    for entry in listing.get("chats") or []:
        chat = entry.get("chat") or {}
        chat_id = chat.get("chat_id")
        unread = int(entry.get("unread_count") or 0)
        if not chat_id or unread <= 0:
            continue

        history = post("/v3/chat/history", {"chat_id": chat_id, "limit": min(unread + 5, 30)})
        customer_msgs = [
            m
            for m in history.get("messages") or []
            if (m.get("user") or {}).get("type") in CUSTOMER_TYPES
        ]
        if not customer_msgs:
            continue

        last = customer_msgs[-1]
        text = message_text(last) or "(без текста)"
        ctype = chat.get("chat_type") or "UNSPECIFIED"
        block = (
            f"<b>Чат Ozon</b> ({html.escape(ctype)})\n"
            f"<code>{html.escape(str(chat_id)[:36])}</code>\n"
            f"Непрочитано: {unread}\n\n"
            f"{html.escape(text[:1500])}"
        )
        alerts.append(block)

    if not alerts:
        print("Нет непрочитанных сообщений от покупателей (Customer).")
        return 0

    body = "\n\n—\n\n".join(alerts)
    if dry_run:
        print(body)
        return len(alerts)

    send_message(body)
    print(f"OK отправлено в Telegram: {len(alerts)} чат(ов)")
    return len(alerts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Только показать, не слать в Telegram")
    args = parser.parse_args()
    check_chats(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
