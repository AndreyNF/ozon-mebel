#!/usr/bin/env python3
"""Отправить тестовое или произвольное сообщение в Telegram (Ozon-бот)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from telegram_client import send_message


def main() -> None:
    parser = argparse.ArgumentParser(description="Telegram notify via OZON bot")
    parser.add_argument("text", nargs="?", default="✅ Ozon-mebel: тест бота. Уведомления подключены.")
    parser.add_argument("--chat-id", help="Переопределить TELEGRAM_CHAT_ID")
    args = parser.parse_args()
    result = send_message(args.text, chat_id=args.chat_id)
    print(f"OK message_id={result.get('message_id')}")


if __name__ == "__main__":
    main()
