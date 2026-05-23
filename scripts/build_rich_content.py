#!/usr/bin/env python3
"""Собрать Rich-контент JSON (Ozon v0.3) для карточки.

Схема по seller-edu / rich-content.ozon.ru/sandbox:
- billboard: title (object), text (size, align, color, content), imgLink
- chess: 2–6 blocks, те же поля title/text
- roll: только img + imgLink
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://cdn.jsdelivr.net/gh/AndreyNF/ozon-mebel@main"

BUILDERS = {}


def register(article: str):
    def deco(fn):
        BUILDERS[article] = fn
        return fn

    return deco


def img_url(name: str, article: str) -> str:
    rel = f"cards/{article}/images/{name}"
    return f"{BASE}/{'/'.join(quote(p, safe='') for p in rel.split('/'))}"


def img_block(url: str, width: int, height: int, alt: str = "") -> dict:
    wm = min(width, 750)
    hm = max(int(height * wm / width), 400)
    return {
        "src": url,
        "srcMobile": url,
        "alt": alt,
        "width": width,
        "height": height,
        "widthMobile": wm,
        "heightMobile": hm,
    }


def rich_title(text: str) -> dict:
    return {
        "content": [text],
        "size": "size4",
        "align": "left",
        "color": "color1",
    }


def rich_text(*lines: str) -> dict:
    return {
        "size": "size2",
        "align": "left",
        "color": "color1",
        "content": [sanitize_rich_text(l) for l in lines if l],
    }


def sanitize_rich_text(text: str) -> str:
    text = text.replace("\u00d7", "x").replace("×", "x")
    text = re.sub(r"^\s*•\s*", "", text)
    return text.strip()


def billboard_block(
    url: str,
    w: int,
    h: int,
    title: str,
    *text_lines: str,
    alt: str = "",
) -> dict:
    return {
        "imgLink": "",
        "img": img_block(url, w, h, alt),
        "title": rich_title(title),
        "text": rich_text(*text_lines),
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
        "title": rich_title(title),
        "text": rich_text(body),
        "reverse": reverse,
    }


def text_block(*paragraphs: str) -> dict:
    return {
        "widgetName": "raTextBlock",
        "text": rich_text(*paragraphs),
    }


def title_text_block(title: str, *paragraphs: str) -> dict:
    return {
        "widgetName": "raTextBlock",
        "title": rich_title(title),
        "text": rich_text(*paragraphs),
    }


def roll_block(url: str, w: int, h: int, alt: str = "") -> dict:
    return {
        "imgLink": "",
        "img": {
            **img_block(url, w, h, alt),
            "position": "width_full",
            "positionMobile": "width_full",
        },
    }


@register("Ц0081444")
def build_wardrobe(article: str) -> dict:
    u = lambda name: img_url(name, article)
    return {
        "version": 0.3,
        "content": [
            title_text_block(
                "Шкаф белый 90 см Мори МШ900.1 — распашной, 2 двери, 2 ящика",
                "Распашной шкаф для одежды ДСВ 90x180 см: белый ЛДСП, штанга, полки, выдвижные ящики. "
                "Подходит для спальни, детской и комнаты подростка. Серия Мори — единый стиль комнаты.",
            ),
            {
                "widgetName": "raShowcase",
                "type": "billboard",
                "blocks": [
                    billboard_block(
                        u("02-infographic.png"),
                        1240,
                        1656,
                        "Белый шкаф 90 см: преимущества Мори МШ900.1",
                        "90 см ширина — встраивается в небольшую комнату.",
                        "2 двери и 2 ящика — одежда и мелочи отдельно.",
                        "Белый минимализм без ручек облегчает интерьер.",
                        "ЛДСП корпус и фасады — практично каждый день.",
                        "Серия Мори — соберите комнату в одном стиле.",
                        alt="Шкаф белый 90 см ДСВ Мори — инфографика",
                    )
                ],
            },
            {
                "widgetName": "raShowcase",
                "type": "chess",
                "blocks": [
                    chess_block(
                        u("04-lifestyle-couple.png"),
                        768,
                        1024,
                        "Шкаф для спальни в интерьере",
                        "Белый распашной шкаф 90 см смотрится легко в современной спальне.",
                        False,
                        "Белый шкаф Мори 90 см в спальне",
                    ),
                    chess_block(
                        u("05-interior-layout.png"),
                        768,
                        1024,
                        "Планировка шкафа для одежды",
                        "Слева полки, справа штанга. Внизу 2 выдвижных ящика на направляющих.",
                        True,
                        "Шкаф распашной 2 двери — наполнение",
                    ),
                    chess_block(
                        u("05-dimensions-ref.jpg"),
                        1000,
                        667,
                        "Размеры 180x90x50 см",
                        "Высота 1800 мм, ширина 904 мм, глубина 504 мм. Вес 79,9 кг.",
                        False,
                        "Габариты шкафа МШ900.1",
                    ),
                    chess_block(
                        u("04-lifestyle-interior-ref.jpg"),
                        1000,
                        667,
                        "Модульная серия Мори",
                        "Шкаф сочетается с кроватью, комодом и тумбой серии Мори.",
                        True,
                        "Шкаф в интерьере комнаты",
                    ),
                ],
            },
            {
                "widgetName": "raShowcase",
                "type": "roll",
                "blocks": [
                    roll_block(u("01-main.png"), 768, 1024, "Шкаф Мори белый — главное фото"),
                    roll_block(u("10-angle-ai.png"), 768, 1024, "Шкаф белый 90 см — ракурс"),
                ],
            },
            text_block(
                "Комплектация и гарантия",
                "В комплекте: корпус, фасады, полки, штанга, направляющие, крепёж, подпятники, инструкция. "
                "Поставка в разборе. Производитель ДСВ, Пенза, Россия. Гарантия 18 месяцев.",
            ),
        ],
    }


@register("Ц0111571")
def build_kitchen(article: str) -> dict:
    u = lambda name: img_url(name, article)
    return {
        "version": 0.3,
        "content": [
            title_text_block(
                "Кухня Фортуна 2,0 м серый/графит — готовый комплект ДСВ",
                "Модульный кухонный гарнитур 200 см: корпус ЛДСП серый, фасады МДФ с матовой пленкой графит. "
                "Напольные модули 600 мм, навесные 300 мм. Столешница и ручки продаются отдельно.",
            ),
            {
                "widgetName": "raShowcase",
                "type": "billboard",
                "blocks": [
                    billboard_block(
                        u("02-infographic.png"),
                        1240,
                        1656,
                        "Кухня 2 метра: размеры и материалы",
                        "Ширина комплекта 2000 мм.",
                        "Глубина: напольные 600 мм, навесные 300 мм.",
                        "Корпус ЛДСП, фасады МДФ.",
                        "Модули: П800 x2, П400, С800, СМ800, СЯШ400.",
                        "Артикул производителя Ц0111571.",
                        alt="Кухня Фортуна 2 м — инфографика",
                    )
                ],
            },
            {
                "widgetName": "raShowcase",
                "type": "chess",
                "blocks": [
                    chess_block(
                        u("03-lifestyle.png"),
                        768,
                        1024,
                        "Кухня в повседневном интерьере",
                        "Компактная кухня 2 м для квартиры — серый графит без ручек.",
                        False,
                        "Серая кухня Фортуна в интерьере",
                    ),
                    chess_block(
                        u("06-layout.png"),
                        768,
                        1024,
                        "Состав комплекта 2,0 м",
                        "Верх: 2 модуля П800 и П400. Низ: С800, СМ800, СЯШ400. Ящики на шариковых направляющих.",
                        True,
                        "Планировка модулей кухни",
                    ),
                    chess_block(
                        u("04-details.png"),
                        768,
                        1024,
                        "Качество фасадов и фурнитуры",
                        "Матовая пленка на МДФ, аккуратная кромка, петли и направляющие для ежедневной работы.",
                        False,
                        "Фасад МДФ графит — детали",
                    ),
                    chess_block(
                        u("07-utp.png"),
                        768,
                        1024,
                        "2 метра — для небольшой кухни",
                        "Готовое решение Фортуна экономит место и дает полный набор модулей.",
                        True,
                        "Компактная кухня 2 метра",
                    ),
                ],
            },
            {
                "widgetName": "raShowcase",
                "type": "roll",
                "blocks": [
                    roll_block(u("01-main.png"), 768, 1024, "Кухня Фортуна — главное фото"),
                    roll_block(u("05-angle.png"), 768, 1024, "Кухня Фортуна — ракурс"),
                ],
            },
            text_block(
                "Комплектация и доставка",
                "В комплекте: модули верхние и напольные, фурнитура, инструкция. Поставка в разборе. "
                "Столешница и ручки не входят. Производитель ДСВ, Пенза, Россия. Гарантия 24 месяца.",
            ),
        ],
    }


@register("Ц0011713")
def build_bed_kivi(article: str) -> dict:
    u = lambda name: img_url(name, article)
    return {
        "version": 0.3,
        "content": [
            title_text_block(
                "Кровать Террикон Киви 80x160 — 2 ящика, молочный дуб/лайм",
                "Односпальная детская кровать 80x160 см: корпус ЛДСП, акценты лайм. "
                "Два выдвижных ящика под спальным местом. Матрас продается отдельно.",
            ),
            {
                "widgetName": "raShowcase",
                "type": "billboard",
                "blocks": [
                    billboard_block(
                        u("02-infographic.png"),
                        1240,
                        1656,
                        "Кровать 80x160: размеры и комплектация",
                        "Спальное место 800 x 1600 мм.",
                        "Габариты 1630 x 850 x 700 мм.",
                        "2 выдвижных ящика для белья.",
                        "Шариковые направляющие.",
                        "Артикул производителя Ц0011713.",
                        alt="Кровать Киви 80x160 — инфографика",
                    )
                ],
            },
            {
                "widgetName": "raShowcase",
                "type": "chess",
                "blocks": [
                    chess_block(
                        u("03-lifestyle.png"),
                        768,
                        1024,
                        "Кровать в детской комнате",
                        "Молочный дуб и лайм — свежий интерьер для ребенка и подростка.",
                        False,
                        "Кровать Киви в детской",
                    ),
                    chess_block(
                        u("06-layout.png"),
                        768,
                        1024,
                        "Комплектация",
                        "Каркас, основание, 2 ящика, фурнитура, инструкция. Матрас не входит.",
                        True,
                        "Комплектация кровати Киви",
                    ),
                    chess_block(
                        u("04-details.png"),
                        768,
                        1024,
                        "Материалы и направляющие",
                        "ЛДСП корпус, кромка ПВХ, шариковые направляющие ящиков.",
                        False,
                        "Детали кровати Киви",
                    ),
                    chess_block(
                        u("07-utp.png"),
                        768,
                        1024,
                        "Хранение под кроватью",
                        "Два ящика экономят место в небольшой детской комнате.",
                        True,
                        "Ящики под кроватью Киви",
                    ),
                ],
            },
            {
                "widgetName": "raShowcase",
                "type": "roll",
                "blocks": [
                    roll_block(u("01-main.png"), 768, 1024, "Кровать Киви — главное фото"),
                    roll_block(u("05-angle.png"), 768, 1024, "Кровать Киви — ракурс"),
                ],
            },
            text_block(
                "Комплектация и доставка",
                "В комплекте: каркас, основание, ящики, фурнитура, инструкция. Разборная поставка. "
                "Матрас не входит. Производитель Террикон, Пенза, Россия. Гарантия 18 месяцев.",
            ),
        ],
    }


@register("Ц0023320")
def build_kivi_set(article: str) -> dict:
    u = lambda name: img_url(name, article)
    return {
        "version": 0.3,
        "content": [
            title_text_block(
                "Комплект детской мебели Террикон Киви набор №1",
                "Модульная детская комната в цвете молочный дуб/лайм: кровать 80x200, шкаф, пенал, "
                "тумба для игрушек и навесная секция. Корпус ЛДСП, разборная поставка.",
            ),
            {
                "widgetName": "raShowcase",
                "type": "billboard",
                "blocks": [
                    billboard_block(
                        u("02-infographic.png"),
                        1240,
                        1656,
                        "Состав набора Киви №1",
                        "Кровать 80x200 см.",
                        "Шкаф 800 мм, 2 двери.",
                        "Пенал 2 ящика.",
                        "Тумба для игрушек.",
                        "Навесная секция.",
                        alt="Комплект Киви — состав модулей",
                    )
                ],
            },
            {
                "widgetName": "raShowcase",
                "type": "chess",
                "blocks": [
                    chess_block(
                        u("03-lifestyle.png"),
                        768,
                        1024,
                        "Готовая детская комната",
                        "Полный комплект мебели в одном стиле — экономия времени на подбор модулей.",
                        False,
                        "Детская комната Киви",
                    ),
                    chess_block(
                        u("06-layout.png"),
                        768,
                        1024,
                        "5 модулей в комплекте",
                        "Кровать, шкаф, пенал, тумба и полка — все в цвете молочный дуб/лайм.",
                        True,
                        "Модули набора Киви",
                    ),
                    chess_block(
                        u("04-details.png"),
                        768,
                        1024,
                        "Фасады и фурнитура",
                        "ЛДСП, аккуратная кромка, шариковые направляющие ящиков.",
                        False,
                        "Детали мебели Киви",
                    ),
                    chess_block(
                        u("07-utp.png"),
                        768,
                        1024,
                        "Модульная система",
                        "Дополняйте комнату другими элементами серии Киви по мере роста ребенка.",
                        True,
                        "Модульность Киви",
                    ),
                ],
            },
            {
                "widgetName": "raShowcase",
                "type": "roll",
                "blocks": [
                    roll_block(u("01-main.png"), 768, 1024, "Комплект Киви — главное фото"),
                    roll_block(u("05-angle.png"), 768, 1024, "Комплект Киви — ракурс"),
                ],
            },
            text_block(
                "Комплектация и доставка",
                "5 модулей, фурнитура, инструкции. Поставка в разборе, 5 упаковок. "
                "Производитель Террикон, Пенза, Россия. Гарантия 18 месяцев.",
            ),
        ],
    }


@register("Ц0050573")
def build_bed_lori(article: str) -> dict:
    u = lambda name: img_url(name, article)
    return {
        "version": 0.3,
        "content": [
            title_text_block(
                "Кровать MLK Лори 140x200 — ящики и ортопедическое основание",
                "Двуспальная кровать 140x200 см: корпус ЛДСП, отделка дуб серый/белый. "
                "Два выдвижных ящика, ортопедическое основание в комплекте. Матрас продается отдельно.",
            ),
            {
                "widgetName": "raShowcase",
                "type": "billboard",
                "blocks": [
                    billboard_block(
                        u("02-infographic.png"),
                        1240,
                        1656,
                        "Кровать 140x200: размеры и комплектация",
                        "Спальное место 1400 x 2000 мм.",
                        "Габариты 1450 x 850 x 2052 мм.",
                        "2 выдвижных ящика для хранения.",
                        "Ортопедическое основание в комплекте.",
                        "Артикул производителя Ц0050573.",
                        alt="Кровать Лори 140x200 — инфографика",
                    )
                ],
            },
            {
                "widgetName": "raShowcase",
                "type": "chess",
                "blocks": [
                    chess_block(
                        u("03-lifestyle.png"),
                        768,
                        1024,
                        "Кровать в современной спальне",
                        "Серый дуб и белый корпус — спокойный интерьер для взрослой и подростковой комнаты.",
                        False,
                        "Кровать Лори в интерьере спальни",
                    ),
                    chess_block(
                        u("06-layout.png"),
                        768,
                        1024,
                        "Ящики и основание",
                        "Два ящика на шариковых направляющих. Ортопедическое основание без подъемного механизма.",
                        True,
                        "Комплектация кровати с ящиками",
                    ),
                    chess_block(
                        u("04-details.png"),
                        768,
                        1024,
                        "Материалы и фурнитура",
                        "Корпус ЛДСП 16 мм, кромка ПВХ. Открывание push-to-open без ручек.",
                        False,
                        "Детали корпуса ЛДСП",
                    ),
                    chess_block(
                        u("07-utp.png"),
                        768,
                        1024,
                        "Серия Лори MLK",
                        "Сочетается с комодом, шкафом и тумбой серии Лори в одном стиле.",
                        True,
                        "Модульная спальня Лори",
                    ),
                ],
            },
            {
                "widgetName": "raShowcase",
                "type": "roll",
                "blocks": [
                    roll_block(u("01-main.png"), 768, 1024, "Кровать Лори — главное фото"),
                    roll_block(u("05-angle.png"), 768, 1024, "Кровать Лори — ракурс"),
                ],
            },
            text_block(
                "Комплектация и доставка",
                "В комплекте: каркас, основание, ящики, фурнитура, инструкция. 4 упаковки, разбор. "
                "Матрас не входит. Производитель MLK, Можга, Россия. Гарантия 18 месяцев.",
            ),
        ],
    }


def build(article: str) -> dict:
    if article in BUILDERS:
        return BUILDERS[article](article)
    raise SystemExit(
        f"Нет Rich-сборщика для {article}. Добавьте @register в build_rich_content.py"
    )


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
