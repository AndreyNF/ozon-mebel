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

ROOT = Path(__file__).resolve().parent.parent


def is_configured() -> bool:
    """Telegram задан и chat_id не совпадает с id бота."""
    load_dotenv()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return False
    try:
        import urllib.request as _ur

        with _ur.urlopen(f"https://api.telegram.org/bot{token}/getMe", timeout=15) as resp:
            me = json.loads(resp.read()).get("result") or {}
        if str(me.get("id")) == chat_id:
            return False
    except Exception:
        pass
    return True


def notify_safe(text: str, *, disable_notification: bool = False) -> bool:
    """Отправить сообщение; при отсутствии секретов или ошибке — не падать."""
    if not is_configured():
        return False
    try:
        send_message(text, disable_notification=disable_notification)
        return True
    except Exception as exc:
        print(f"Telegram: {exc}", file=sys.stderr)
        return False


def _live_status_lines(article: str) -> list[str]:
    live = ROOT / "cards" / article / f"ozon-live-status_{article}.json"
    if not live.is_file():
        return []
    try:
        data = json.loads(live.read_text(encoding="utf-8"))
        st = (data.get("item") or {}).get("statuses") or {}
        v = st.get("validation_status")
        n = st.get("status_name")
        if v or n:
            return [f"• ЛК: {n or '—'}, validation={v or '—'}"]
    except (json.JSONDecodeError, OSError):
        pass
    return []


def format_import_notify(article: str, items: list[dict], *, pictures: bool = False) -> str:
    lines = [f"Ozon import: {article}"]
    for it in items:
        status = str(it.get("status", "?"))
        lines.append(f"• статус: {status}")
        for err in it.get("errors") or []:
            code = err.get("code") or err.get("message") or err
            lines.append(f"  ⚠ {code}")
    if pictures:
        lines.append("• фото: pictures/import (обход skipped)")
    lines.extend(_live_status_lines(article))
    return "\n".join(lines)


def format_pipeline_notify(article: str, *, stock: int | None = None) -> str:
    """Сводка после import + status + stocks (для вызова в конце цикла)."""
    lines = [f"Ozon: {article}"]
    imp = ROOT / "cards" / article / f"ozon-import-result_{article}.json"
    if imp.is_file():
        try:
            data = json.loads(imp.read_text(encoding="utf-8"))
            for it in (data.get("result") or {}).get("items") or []:
                lines.append(f"• импорт: {it.get('status', '?')}")
        except (json.JSONDecodeError, OSError):
            pass
    lines.extend(_live_status_lines(article))
    if stock is not None:
        lines.append(f"• FBS остаток: {stock}")
    return "\n".join(lines)


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
