#!/usr/bin/env python3
"""Промпты i2i Sanvut кухня: обработка фото производителя, без выдуманных модулей.

Политика: .cursor/rules/ozon-photo-fidelity.mdc
Карточка: Кухня Шампань 1000х1800 — угловой гарнитир 1800×1000 мм.
"""

from __future__ import annotations

MAIN_REF = "https://sanvut.ru/upload/dev2fun.imagecompress/webp/iblock/da8/jhzu9912ai37ncj41gfgf2r36453y98p.webp"
SCHEMATIC_REF = "https://sanvut.ru/upload/dev2fun.imagecompress/webp/iblock/096/voc4efgsfe9ffce0juiz3fyhzds9vxpv.webp"
ALT_REF = "https://sanvut.ru/upload/dev2fun.imagecompress/webp/iblock/5c5/im8kwe22dvxqafqjpyn4ml3rqkkv28kw.webp"
MARBLE_REF = "https://sanvut.ru/upload/dev2fun.imagecompress/webp/iblock/5d4/mnqeo7gevkmggqagmugzh1t7gc2siweu.webp"

FIDELITY_RU = (
    "КРИТИЧНО i2i: сохранить ТОЧНО ту же угловую кухню L-формы 1800×1000 мм — "
    "4 напольных модуля, 3 навесных, ящики, один модуль 450 мм под духовку/варку. "
    "НЕ добавлять лишние шкафы, второй ряд, остров, полуостров, дублировать зону готовки. "
    "Цвета как на референсе: фасады белый сатин ЛДСП, столешница мрамор Марквина белый, ручки чёрные 160 мм. "
    "Не уходить в кремовый/greige, не усиливать насыщенность. "
    "Вертикальное фото 3:4 для Ozon, фотореализм, без водяных знаков."
)

FIDELITY_EN = (
    "CRITICAL i2i: keep IDENTICAL compact L-shaped corner kitchen 1800x1000mm — "
    "4 base cabinets, 3 wall cabinets, drawers, ONE 450mm oven module. "
    "Do NOT add extra cabinets, second kitchen run, island, peninsula, duplicate cooktop zone. "
    "Exact colors: white satin LDSP facades, white marble Markvina countertop, black 160mm handles. "
    "No cream/greige color shift, no saturation boost. Vertical 3:4 Ozon product photo, photorealistic."
)

SLOTS: dict[str, dict] = {
    "01-main.png": {
        "refs": [MAIN_REF],
        "prompt": f"{FIDELITY_RU} Та же кухня на чистом белом студийном фоне, полный вид, мягкий свет, без людей и текста — главное фото Ozon.",
    },
    "02-infographic.png": {
        "refs": [MAIN_REF, SCHEMATIC_REF],
        "prompt": f"{FIDELITY_RU} Инфографика на светлом фоне: та же кухня, размеры 180×100 см, подписи модулей по-русски, минимум текста.",
    },
    "03-lifestyle.png": {
        "refs": [MAIN_REF],
        "prompt": f"{FIDELITY_RU} Та же кухня в светлой квартире, женщина 30 лет готовит у плиты — товар тот же, без лишних модулей.",
    },
    "04-details.png": {
        "refs": [MARBLE_REF, MAIN_REF],
        "prompt": f"{FIDELITY_RU} Крупный план столешницы мрамор Марквина и фасада сатин белый, чёрная ручка — цвета с референса.",
    },
    "05-angle.png": {
        "refs": [ALT_REF, MAIN_REF],
        "prompt": f"{FIDELITY_EN} Three-quarter angle of the same L-kitchen in light empty room, show depth, no extra modules.",
    },
    "06-layout.png": {
        "refs": [SCHEMATIC_REF, MAIN_REF],
        "prompt": f"{FIDELITY_RU} Схема планировки угловой кухни 1,8 м: та же раскладка модулей, цвета с референса, белый фон.",
    },
    "07-utp.png": {
        "refs": [MAIN_REF],
        "prompt": f"{FIDELITY_RU} Продающий кадр: компактная угловая кухня для маленькой кухни — тот же гарнитир, столешницы в комплекте.",
    },
    "08-cooktop.png": {
        "refs": [MAIN_REF],
        "prompt": (
            f"{FIDELITY_RU} Модуль под варку: один нейтральный кадр зоны готовки "
            "(плита/духовка не в комплекте). Та же кухня, без второй плиты."
        ),
    },
    "09-sink.png": {
        "refs": [MAIN_REF],
        "prompt": (
            f"{FIDELITY_RU} Модуль под мойку: смеситель, столешница, фасады — "
            "мойка не в комплекте. Другой ракурс, не дубль зоны варки."
        ),
    },
    "10-assembly.png": {
        "refs": [MAIN_REF],
        "prompt": (
            f"{FIDELITY_RU} Сборка flat-pack: модули в упаковке, фурнитура, инструкция — "
            "тот же гарнитир, без лишних модулей."
        ),
    },
}
