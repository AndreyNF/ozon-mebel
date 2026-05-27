#!/usr/bin/env python3
"""Уведомления через бот проекта ozon-mebel (TELEGRAM_* в .env / Cloud Agents).

Не использовать MCP Kovcheg — там другой бот.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ozon_client import load_dotenv


def telegram_credentials() -> tuple[str, str]:
    load_dotenv()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise SystemExit(
            "Задайте TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID "
            "(Cloud Agents → Environment Variables или .env)."
        )
    return token, chat_id


def send_message(
    text: str,
    *,
    chat_id: str | None = None,
    parse_mode: str | None = None,
    disable_notification: bool = False,
) -> dict[str, Any]:
    token, default_chat = telegram_credentials()
    cid = (chat_id or default_chat).strip()
    body: dict[str, Any] = {
        "chat_id": cid,
        "text": text,
        "disable_notification": disable_notification,
    }
    if parse_mode:
        body["parse_mode"] = parse_mode
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram sendMessage HTTP {e.code}: {detail}") from e
    out = json.loads(raw) if raw else {}
    if not out.get("ok"):
        raise RuntimeError(f"Telegram API error: {out}")
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Отправить сообщение в Telegram (бот ozon-mebel)")
    p.add_argument("text", nargs="?", default="", help="Текст (или --test)")
    p.add_argument("--test", action="store_true", help="Тестовое сообщение от скрипта проекта")
    p.add_argument("--chat-id", help="Переопределить TELEGRAM_CHAT_ID")
    p.add_argument("--parse-mode", choices=("HTML", "Markdown", "MarkdownV2"))
    args = p.parse_args()
    text = args.text.strip()
    if args.test:
        text = (
            "Тест ozon-mebel: сообщение через scripts/telegram_notify.py "
            "(бот из TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, не MCP Kovcheg)."
        )
    if not text:
        p.error("Укажите текст или --test")
    result = send_message(text, chat_id=args.chat_id, parse_mode=args.parse_mode)
    msg = (result.get("result") or {})
    print(f"OK message_id={msg.get('message_id')} chat_id={msg.get('chat', {}).get('id')}")


if __name__ == "__main__":
    main()
