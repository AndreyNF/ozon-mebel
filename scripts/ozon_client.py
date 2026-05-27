#!/usr/bin/env python3
"""Минимальный клиент Ozon Seller API (stdlib)."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

BASE_URL = "https://api-seller.ozon.ru"
ROOT = Path(__file__).resolve().parent.parent


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
    client_id = (
        os.environ.get("OZON_CLIENT_ID")
        or os.environ.get("Api_client_id")
        or os.environ.get("API_CLIENT_ID")
        or ""
    ).strip()
    api_key = (
        os.environ.get("OZON_API_KEY")
        or os.environ.get("Api_secret_key")
        or os.environ.get("API_SECRET_KEY")
        or ""
    ).strip()
    if not client_id or not api_key:
        raise SystemExit(
            "Задайте ключи Ozon: OZON_CLIENT_ID + OZON_API_KEY "
            "(или Api_client_id + Api_secret_key в Cloud Agents / .env). "
            "Секреты должны быть привязаны к репозиторию AndreyNF/ozon-mebel."
        )
    return client_id, api_key


def post(path: str, body: dict[str, Any] | None = None, *, timeout: float = 120.0) -> dict[str, Any]:
    client_id, api_key = credentials()
    data = json.dumps(body or {}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        method="POST",
        headers={
            "Client-Id": client_id,
            "Api-Key": api_key,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ozon API {path} HTTP {e.code}: {detail}") from e
    return json.loads(raw) if raw else {}


def poll_import_task(
    task_id: int,
    *,
    interval_sec: float = 3.0,
    max_wait_sec: float = 300.0,
) -> dict[str, Any]:
    """Ждать завершения задачи импорта /v1/product/import/info."""
    deadline = time.time() + max_wait_sec
    last: dict[str, Any] = {}
    while time.time() < deadline:
        last = post("/v1/product/import/info", {"task_id": task_id})
        items = (last.get("result") or {}).get("items") or []
        if items:
            statuses = {str(i.get("status", "")).lower() for i in items}
            if "pending" not in statuses and "processing" not in statuses:
                return last
        time.sleep(interval_sec)
    return last
