#!/usr/bin/env python3
"""Опрос Ozon: вопросы, отзывы, чат → черновик → автоответ.

Примеры:
  python3 scripts/ozon_comms_poll.py --all
  python3 scripts/ozon_comms_poll.py --chat --dry-run
  OZON_COMMS_DRY_RUN=1 python3 scripts/ozon_comms_poll.py --all --notify-telegram
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ozon_comms_lib import (
    env_bool,
    load_product_index,
    load_state,
    process_chats,
    process_questions,
    process_reviews,
    save_state,
)
from telegram_notify import format_comms_summary, send_message


def main() -> None:
    parser = argparse.ArgumentParser(description="Ozon buyer comms auto-reply")
    parser.add_argument("--all", action="store_true", help="Вопросы + отзывы + чат")
    parser.add_argument("--questions", action="store_true")
    parser.add_argument("--reviews", action="store_true")
    parser.add_argument("--chat", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Не отправлять ответы")
    parser.add_argument("--notify-telegram", action="store_true", help="Сводка в Telegram")
    args = parser.parse_args()

    if not any([args.all, args.questions, args.reviews, args.chat]):
        args.all = True

    dry_run = args.dry_run or env_bool("OZON_COMMS_DRY_RUN", False)
    notify = args.notify_telegram or env_bool("OZON_COMMS_NOTIFY_TELEGRAM", False)

    state = load_state()
    products = load_product_index()
    results: list[dict] = []

    if args.all or args.chat:
        if env_bool("OZON_COMMS_AUTO_CHAT", True):
            results.extend(
                process_chats(products=products, state=state, dry_run=dry_run)
            )
    if args.all or args.questions:
        if env_bool("OZON_COMMS_AUTO_QUESTIONS", True):
            results.extend(
                process_questions(products=products, state=state, dry_run=dry_run)
            )
    if args.all or args.reviews:
        if env_bool("OZON_COMMS_AUTO_REVIEWS", True):
            results.extend(
                process_reviews(products=products, state=state, dry_run=dry_run)
            )

    save_state(state)

    summary = {
        "dry_run": dry_run,
        "handled": len([r for r in results if r.get("action") in {"sent", "dry_run"}]),
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if notify:
        sent = send_message(format_comms_summary(results))
        if not sent:
            print("WARN: Telegram не настроен (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)", file=sys.stderr)


if __name__ == "__main__":
    main()
