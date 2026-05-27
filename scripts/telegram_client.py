#!/usr/bin/env python3
"""Минимальный клиент Telegram Bot API (stdlib)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.telegram.org/bot{token}/{method}"


def load_dotenv(path: Path | None = None) -> None:
    path = path or ROOT / ".env"
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def credentials() -> tuple[str, str]:
    load_dotenv()
    token = (
        os.environ.get("TELEGRAM_BOT_TOKEN")
        or os.environ.get("telegram_bot_token")
        or os.environ.get("OZON_TELEGRAM_BOT_TOKEN")
        or ""
    ).strip()
    chat_id = (
        os.environ.get("TELEGRAM_CHAT_ID")
        or os.environ.get("telegram_chat_id")
        or os.environ.get("OZON_TELEGRAM_CHAT_ID")
        or ""
    ).strip()
    if not token:
        raise SystemExit(
            "Задайте TELEGRAM_BOT_TOKEN в Cloud Agents / .env для репозитория ozon-mebel."
        )
    if not chat_id:
        raise SystemExit(
            "Задайте TELEGRAM_CHAT_ID (личка / группа, куда бот может писать). "
            "Получить: напишите боту /start и откройте getUpdates."
        )
    return token, chat_id


def call(method: str, payload: dict[str, Any] | None = None, *, token: str | None = None) -> dict[str, Any]:
    tok = token or credentials()[0]
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(
        API.format(token=tok, method=method),
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60.0) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram {method} HTTP {e.code}: {detail}") from e
    body = json.loads(raw) if raw else {}
    if not body.get("ok"):
        raise RuntimeError(f"Telegram {method} error: {body}")
    return body.get("result") or {}


def send_message(
    text: str,
    *,
    chat_id: str | None = None,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
) -> dict[str, Any]:
    token, default_chat = credentials()
    cid = (chat_id or default_chat).strip()
    return call(
        "sendMessage",
        {
            "chat_id": cid,
            "text": text[:4096],
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        },
        token=token,
    )
