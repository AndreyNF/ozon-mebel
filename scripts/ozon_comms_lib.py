#!/usr/bin/env python3
"""Ozon: вопросы, отзывы, чат с покупателями — опрос, черновики, автоответ."""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ozon_client import post

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
STATE_PATH = DATA_DIR / "ozon-comms-state.json"
LOG_DIR = ROOT / "data" / "ozon-comms-logs"

BUYER_USER_TYPES = {"customer", "buyer"}
SKIP_USER_TYPES = {"notificationuser", "chatbot", "crm", "courier", "support"}

REVIEW_POSITIVE_MIN = 4


@dataclass
class FaqEntry:
    question: str
    answer: str
    source: str


@dataclass
class ProductInfo:
    article: str
    name: str
    sku: int | None
    product_id: int | None
    faq: list[FaqEntry]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def env_bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name, "").strip().lower()
    if not val:
        return default
    return val in {"1", "true", "yes", "on"}


def load_state() -> dict[str, Any]:
    if STATE_PATH.is_file():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {
        "processed": {"questions": {}, "reviews": {}, "chat_messages": {}},
        "premium_plus": None,
        "last_run": None,
    }


def save_state(state: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    state["last_run"] = utc_now_iso()
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def append_log(record: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = LOG_DIR / f"ozon-comms-{day}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def normalize_text(text: str) -> str:
    text = text.lower().replace("ё", "е")
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def token_set(text: str) -> set[str]:
    stop = {
        "и", "в", "на", "с", "по", "для", "как", "что", "ли", "это", "у", "из",
        "а", "или", "не", "да", "нет", "у", "же", "бы", "то", "вы", "мы",
    }
    return {t for t in normalize_text(text).split() if len(t) > 2 and t not in stop}


def parse_faq_from_md(text: str, source: str) -> list[FaqEntry]:
    entries: list[FaqEntry] = []
    q = a = ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("**В:**"):
            q = line.replace("**В:**", "").strip()
        elif line.startswith("**О:**") and q:
            a = line.replace("**О:**", "").strip()
            if a:
                entries.append(FaqEntry(q, a, source))
            q = a = ""
    return entries


def faq_from_row(article: str, row: dict[str, Any]) -> list[FaqEntry]:
    entries: list[FaqEntry] = []
    name = (row.get("Название товара") or article).strip()
    guarantee = (row.get("Гарантийный срок") or row.get("Гарантия") or "").strip()
    packing = (row.get("Форма поставки") or "").strip()
    kit = (row.get("Комплектация") or "").strip()
    ann = (row.get("Аннотация") or "").strip()

    if kit:
        entries.append(FaqEntry("Что входит в комплект?", kit, f"{article}.row.json"))
    if packing:
        entries.append(FaqEntry("Нужна ли сборка?", packing, f"{article}.row.json"))
    if guarantee:
        entries.append(FaqEntry("Какая гарантия?", guarantee, f"{article}.row.json"))
    if ann:
        entries.append(FaqEntry("Расскажите о товаре", ann[:400], f"{article}.row.json"))
    entries.append(
        FaqEntry(
            "Как называется товар?",
            f"Это {name}. Будем рады помочь с подбором и уточнением характеристик.",
            f"{article}.row.json",
        )
    )
    return entries


def load_product_index() -> dict[str, ProductInfo]:
    by_article: dict[str, ProductInfo] = {}
    by_sku: dict[int, str] = {}
    by_product_id: dict[int, str] = {}

    cards = ROOT / "cards"
    if not cards.is_dir():
        return by_article

    for card_dir in cards.iterdir():
        if not card_dir.is_dir():
            continue
        article = card_dir.name
        row_path = card_dir / f"{article}.row.json"
        md_path = card_dir / f"{article}.md"
        faq: list[FaqEntry] = []

        row: dict[str, Any] = {}
        if row_path.is_file():
            row = json.loads(row_path.read_text(encoding="utf-8"))
            faq.extend(faq_from_row(article, row))
        if md_path.is_file():
            faq.extend(parse_faq_from_md(md_path.read_text(encoding="utf-8"), f"{article}.md"))

        name = (row.get("Название товара") or article).strip()
        sku = None
        product_id = None

        live = card_dir / f"ozon-live-status_{article}.json"
        if live.is_file():
            item = json.loads(live.read_text(encoding="utf-8")).get("item") or {}
            product_id = item.get("id")
            for src in item.get("sources") or []:
                if src.get("sku"):
                    sku = int(src["sku"])
                    by_sku[sku] = article
            if product_id:
                by_product_id[int(product_id)] = article

        by_article[article] = ProductInfo(article, name, sku, product_id, faq)

    # attach sku lookup on products
    for sku, article in by_sku.items():
        if article in by_article and by_article[article].sku is None:
            by_article[article].sku = sku
    return by_article


def resolve_article(
    products: dict[str, ProductInfo],
  *,
    sku: str | int | None = None,
    product_id: int | None = None,
    offer_id: str | None = None,
) -> ProductInfo | None:
    if offer_id and offer_id in products:
        return products[offer_id]
    if sku not in (None, ""):
        sku_i = int(sku)
        for p in products.values():
            if p.sku == sku_i:
                return p
    if product_id:
        for p in products.values():
            if p.product_id == int(product_id):
                return p
    return None


def match_faq(question: str, faq: list[FaqEntry]) -> FaqEntry | None:
    if not faq:
        return None
    q_tokens = token_set(question)
    if not q_tokens:
        return None
    best: FaqEntry | None = None
    best_score = 0.0
    for entry in faq:
        e_tokens = token_set(entry.question)
        if not e_tokens:
            continue
        overlap = len(q_tokens & e_tokens)
        score = overlap / max(len(q_tokens), 1)
        if score > best_score:
            best_score = score
            best = entry
    if best and best_score >= 0.25:
        return best
    return None


def greeting() -> str:
    return "Здравствуйте!"


def draft_answer(question: str, product: ProductInfo | None) -> str:
    faq = product.faq if product else []
    hit = match_faq(question, faq)
    if hit:
        body = hit.answer
    else:
        body = (
            "Спасибо за вопрос. Мебель поставляется в разобранном виде с фурнитурой и инструкцией. "
            "По габаритам и комплектации смотрите карточку товара; если нужно — уточним детали по вашему заказу."
        )
    if product:
        return f"{greeting()} {body}"
    return f"{greeting()} {body}"


def draft_review_reply(rating: int, text: str, product: ProductInfo | None) -> str:
    name = product.name if product else "наш товар"
    if rating >= REVIEW_POSITIVE_MIN:
        return (
            f"{greeting()} Благодарим за отзыв и высокую оценку {name}! "
            "Рады, что покупка вам понравилась. Хорошего дня!"
        )
    apology = (
        f"{greeting()} Сожалеем, что впечатление от {name} оказалось неидеальным."
    )
    if text.strip():
        apology += " Мы внимательно изучим ваш комментарий."
    apology += (
        " Напишите, пожалуйста, в чат с продавцом номер заказа — поможем решить вопрос."
    )
    return apology


def draft_chat_reply(message: str, product: ProductInfo | None) -> str:
    low = message.lower()
    if any(x in low for x in ("спасибо", "благодар", "получил", "всё отлично")):
        return f"{greeting()} Рады были помочь! Если появятся вопросы — пишите."
    return draft_answer(message, product)


def check_premium_plus(state: dict[str, Any]) -> bool:
    cached = state.get("premium_plus")
    if isinstance(cached, dict) and cached.get("checked_at"):
        return bool(cached.get("available"))
    available = False
    try:
        post("/v1/question/count", {})
        available = True
    except RuntimeError as e:
        available = "Premium Plus" not in str(e) and "403" not in str(e)
    state["premium_plus"] = {"available": available, "checked_at": utc_now_iso()}
    return available


def already_processed(state: dict[str, Any], kind: str, item_id: str) -> bool:
    return item_id in (state.get("processed") or {}).get(kind, {})


def mark_processed(state: dict[str, Any], kind: str, item_id: str, meta: dict[str, Any]) -> None:
    proc = state.setdefault("processed", {})
    bucket = proc.setdefault(kind, {})
    bucket[item_id] = {"at": utc_now_iso(), **meta}


def message_text(msg: dict[str, Any]) -> str:
    parts = msg.get("data") or []
    if not parts:
        return ""
    if isinstance(parts, list):
        return "\n".join(str(p) for p in parts).strip()
    return str(parts).strip()


def is_buyer_message(msg: dict[str, Any]) -> bool:
    user_type = str((msg.get("user") or {}).get("type") or "").lower()
    if user_type in SKIP_USER_TYPES:
        return False
    if user_type in BUYER_USER_TYPES:
        return True
    # legacy / неизвестные типы: не отвечаем на системные
    return False


def is_system_chat(messages: list[dict[str, Any]]) -> bool:
    """Пропускаем чаты Ozon (уведомления, боты) без сообщений покупателя."""
    for msg in messages:
        if is_buyer_message(msg):
            return False
    return True


def list_unread_chats(limit: int = 50) -> list[dict[str, Any]]:
    resp = post("/v3/chat/list", {"filter": {"unread_only": True}, "limit": limit})
    return resp.get("chats") or []


def chat_history(chat_id: str, limit: int = 50) -> list[dict[str, Any]]:
    resp = post("/v3/chat/history", {"chat_id": chat_id, "limit": limit})
    return resp.get("messages") or []


def send_chat_message(chat_id: str, text: str) -> dict[str, Any]:
    return post("/v1/chat/send/message", {"chat_id": chat_id, "text": text})


def mark_chat_read(chat_id: str, from_message_id: int) -> dict[str, Any]:
    return post("/v2/chat/read", {"chat_id": chat_id, "from_message_id": from_message_id})


def list_unprocessed_questions(limit: int = 50) -> list[dict[str, Any]]:
    resp = post(
        "/v1/question/list",
        {"filter": {"status": "UNPROCESSED"}, "limit": limit},
    )
    return resp.get("questions") or resp.get("result", {}).get("questions") or []


def create_question_answer(question_id: str, sku: int, text: str) -> dict[str, Any]:
    return post(
        "/v1/question/answer/create",
        {"question_id": question_id, "sku": sku, "text": text},
    )


def mark_question_processed(question_ids: list[str]) -> dict[str, Any]:
    return post(
        "/v1/question/change-status",
        {"question_ids": question_ids, "status": "PROCESSED"},
    )


def list_unprocessed_reviews(limit: int = 50) -> list[dict[str, Any]]:
    resp = post(
        "/v1/review/list",
        {"last_id": "", "limit": limit, "sort_dir": "DESC", "status": "UNPROCESSED"},
    )
    return resp.get("reviews") or resp.get("result", {}).get("reviews") or []


def create_review_comment(review_id: str, text: str, mark_processed: bool = True) -> dict[str, Any]:
    return post(
        "/v1/review/comment/create",
        {
            "review_id": review_id,
            "text": text,
            "mark_review_as_processed": mark_processed,
        },
    )


def process_chats(
    *,
    products: dict[str, ProductInfo],
    state: dict[str, Any],
    dry_run: bool,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in list_unread_chats():
        chat = item.get("chat") or {}
        chat_id = chat.get("chat_id")
        if not chat_id:
            continue
        messages = chat_history(chat_id)
        if is_system_chat(messages):
            results.append(
                {"kind": "chat", "chat_id": chat_id, "action": "skip_system_chat"}
            )
            continue

        pending = [
            m
            for m in messages
            if not m.get("is_read") and is_buyer_message(m)
        ]
        if not pending:
            continue

        # Отвечаем только на последнее непрочитанное сообщение покупателя
        msg = pending[-1]
        msg_id = str(msg.get("message_id") or "")
        if not msg_id or already_processed(state, "chat_messages", msg_id):
            continue

        text_in = message_text(msg)
        if not text_in or msg.get("is_image"):
            mark_processed(state, "chat_messages", msg_id, {"action": "skip_image"})
            continue

        ctx = msg.get("context") or {}
        product = resolve_article(
            products,
            sku=ctx.get("sku"),
            offer_id=None,
        )
        reply = draft_chat_reply(text_in, product)
        record = {
            "kind": "chat",
            "chat_id": chat_id,
            "message_id": msg_id,
            "incoming": text_in[:500],
            "reply": reply,
            "article": product.article if product else None,
            "dry_run": dry_run,
        }

        if dry_run:
            record["action"] = "dry_run"
        else:
            send_chat_message(chat_id, reply)
            mark_chat_read(chat_id, int(msg_id))
            record["action"] = "sent"
            mark_processed(state, "chat_messages", msg_id, {"action": "sent"})

        append_log(record)
        results.append(record)
    return results


def process_questions(
    *,
    products: dict[str, ProductInfo],
    state: dict[str, Any],
    dry_run: bool,
) -> list[dict[str, Any]]:
    if not check_premium_plus(state):
        return [{"kind": "question", "action": "skip_no_premium_plus"}]

    results: list[dict[str, Any]] = []
    for q in list_unprocessed_questions():
        qid = str(q.get("id") or q.get("question_id") or "")
        if not qid or already_processed(state, "questions", qid):
            continue

        text_in = (q.get("text") or q.get("question_text") or "").strip()
        sku = q.get("sku")
        product = resolve_article(products, sku=sku, product_id=q.get("product_id"))
        reply = draft_answer(text_in, product)

        record = {
            "kind": "question",
            "question_id": qid,
            "incoming": text_in[:500],
            "reply": reply,
            "article": product.article if product else None,
            "dry_run": dry_run,
        }

        if dry_run:
            record["action"] = "dry_run"
        else:
            if not product or not product.sku:
                record["action"] = "skip_no_sku"
            else:
                create_question_answer(qid, int(product.sku), reply)
                mark_question_processed([qid])
                record["action"] = "sent"
                mark_processed(state, "questions", qid, {"action": "sent"})

        append_log(record)
        results.append(record)
    return results


def process_reviews(
    *,
    products: dict[str, ProductInfo],
    state: dict[str, Any],
    dry_run: bool,
) -> list[dict[str, Any]]:
    if not check_premium_plus(state):
        return [{"kind": "review", "action": "skip_no_premium_plus"}]

    results: list[dict[str, Any]] = []
    for r in list_unprocessed_reviews():
        rid = str(r.get("id") or r.get("review_id") or "")
        if not rid or already_processed(state, "reviews", rid):
            continue

        text_in = (r.get("text") or r.get("review_text") or "").strip()
        rating = int(r.get("rating") or r.get("score") or 5)
        product = resolve_article(products, sku=r.get("sku"), product_id=r.get("product_id"))
        reply = draft_review_reply(rating, text_in, product)

        record = {
            "kind": "review",
            "review_id": rid,
            "rating": rating,
            "incoming": text_in[:500],
            "reply": reply,
            "article": product.article if product else None,
            "dry_run": dry_run,
        }

        if dry_run:
            record["action"] = "dry_run"
        else:
            create_review_comment(rid, reply, mark_processed=True)
            record["action"] = "sent"
            mark_processed(state, "reviews", rid, {"action": "sent"})

        append_log(record)
        results.append(record)
    return results
