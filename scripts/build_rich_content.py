#!/usr/bin/env python3
"""Собрать Rich-контент JSON (Ozon v0.3) для карточки."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://raw.githubusercontent.com/AndreyNF/ozon-mebel/main"


def img_url(name: str, article: str) -> str:
    rel = f"cards/{article}/images/{name}"
    return f"{BASE}/{'/'.join(quote(p, safe='') for p in rel.split('/'))}"


def img_block(url: str, width: int, height: int, alt: str = "") -> dict:
    return {
        "src": url,
        "srcMobile": url,
        "alt": alt,
        "width": width,
        "height": height,
        "widthMobile": min(width, 750),
        "heightMobile": max(int(height * min(width, 750) / width), 400),
    }


def text_block(*paragraphs: str, size: str = "size2", align: str = "left") -> dict:
    return {
        "widgetName": "raTextBlock",
        "text": {
            "size": size,
            "align": align,
            "color": "color1",
            "content": list(paragraphs),
        },
    }


def title_text_block(title: str, *paragraphs: str) -> dict:
    return {
        "widgetName": "raTextBlock",
        "title": {
            "content": [title],
            "size": "size4",
            "align": "left",
            "color": "color1",
        },
        "text": {
            "size": "size2",
            "align": "left",
            "color": "color1",
            "content": list(paragraphs),
        },
    }


def chess_block(
    url: str,
    w: int,
    h: int,
    title: str,
    body: str,
    reverse: bool = False,
    alt: str = "",
) -> dict:
    return {
        "img": img_block(url, w, h, alt),
        "imgLink": "",
        "title": {
            "content": [title],
            "size": "size4",
            "align": "left",
            "color": "color1",
        },
        "text": {
            "size": "size2",
            "align": "left",
            "color": "color1",
            "content": [body],
        },
        "reverse": reverse,
    }


def build(article: str = "Ц0081444") -> dict:
    u = lambda name: img_url(name, article)

    return {
        "version": 0.3,
        "content": [
            title_text_block(
                "Шкаф Мори МШ900.1 — белый минимализм для спальни",
                "Распашной шкаф ДСВ 90×180 см: 2 двери, 2 ящика, ЛДСП. "
                "Компактное хранение одежды в спальне, детской или комнате подростка. "
                "Серия «Мори» — единый стиль всей комнаты.",
            ),
            {
                "widgetName": "raShowcase",
                "type": "billboard",
                "blocks": [
                    {
                        "img": img_block(u("02-infographic.png"), 1240, 1656, "Шкаф Мори МШ900.1 — преимущества"),
                        "title": "Почему выбирают Мори МШ900.1",
                        "text": {
                            "content": [
                                "• 90 см ширина — встраивается даже в небольшую комнату",
                                "• 2 двери + 2 ящика — одежда и мелочи отдельно",
                                "• Белый минимализм без ручек — визуально облегчает интерьер",
                                "• ЛДСП корпус и фасады — практично в ежедневном использовании",
                                "• Серия «Мори» — соберите комнату в одном стиле",
                            ]
                        },
                    }
                ],
            },
            {
                "widgetName": "raShowcase",
                "type": "chess",
                "blocks": [
                    chess_block(
                        u("03-lifestyle-woman.png"),
                        768,
                        1024,
                        "В интерьере спальни",
                        "Белый фасад не перегружает комнату — шкаф смотрится легко "
                        "и подходит для современной спальни или детской.",
                        False,
                        "Lifestyle шкаф в спальне",
                    ),
                    chess_block(
                        u("05-interior-cutaway-ref.jpg"),
                        1000,
                        667,
                        "Планировка внутри",
                        "Слева — полки для вещей, справа — штанга для вешалок. "
                        "Внизу — 2 выдвижных ящика на роликовых направляющих.",
                        True,
                        "Схема наполнения шкафа",
                    ),
                    chess_block(
                        u("05-dimensions-ref.jpg"),
                        1000,
                        667,
                        "Размеры 180×90×50 см",
                        "Высота 1800 мм, ширина 904 мм, глубина 504 мм. "
                        "Вес 79,9 кг. Напольная установка.",
                        False,
                        "Габариты шкафа МШ900.1",
                    ),
                    chess_block(
                        u("04-lifestyle-interior-ref.jpg"),
                        1000,
                        667,
                        "Модульная серия «Мори»",
                        "Шкаф сочетается с кроватью, комодом и тумбой серии Мори — "
                        "можно собрать комнату в едином минималистичном стиле.",
                        True,
                        "Шкаф в интерьере комнаты",
                    ),
                ],
            },
            {
                "widgetName": "raShowcase",
                "type": "roll",
                "blocks": [
                    {
                        "imgLink": "",
                        "img": {
                            **img_block(u("01-main.png"), 768, 1024, "Шкаф Мори белый — главное фото"),
                            "position": "width_full",
                            "positionMobile": "width_full",
                        },
                    },
                    {
                        "imgLink": "",
                        "img": {
                            **img_block(u("06-angle-ref.jpg"), 1000, 667, "Ракурс шкафа"),
                            "position": "width_full",
                            "positionMobile": "width_full",
                        },
                    },
                ],
            },
            {
                "widgetName": "raVideo",
                "type": "youtube",
                "youtubeVideoId": "WpW8Ssc7C4U",
            },
            text_block(
                "Комплектация и гарантия",
                "В комплекте: корпус, фасады, полки, штанга, направляющие, "
                "крепёж, подпятники, инструкция по сборке. "
                "Поставка в разборе. Производитель: ДСВ Мебель, Пенза, Россия. "
                "Гарантия 18 месяцев.",
                size="size2",
            ),
        ],
    }


def main() -> None:
    article = sys.argv[1] if len(sys.argv) > 1 else "Ц0081444"
    card = ROOT / "cards" / article
    rich = build(article)

    out_pretty = card / f"{article}.rich-content.json"
    out_pretty.write_text(json.dumps(rich, ensure_ascii=False, indent=2), encoding="utf-8")

    row_path = card / f"{article}.row.json"
    row = json.loads(row_path.read_text(encoding="utf-8"))
    row["Rich-контент JSON"] = json.dumps(rich, ensure_ascii=False, separators=(",", ":"))
    row_path.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")

    print(out_pretty)
    print(f"Rich widgets: {len(rich['content'])}")


if __name__ == "__main__":
    main()
