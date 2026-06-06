#!/usr/bin/env python3
"""Промпты i2i для Браво: обработка фото дилера, без выдуманных модулей.

Политика: .cursor/rules/ozon-photo-fidelity.mdc
"""

from __future__ import annotations

# Референс полного комплекта 8 модулей (tdbravomebel)
MAIN_REF = "https://tdbravomebel.ru/upload/iblock/f01/f014863f700a87d9f3aa4bcfa00dff07.jpg"
LAYOUT_REF = "https://tdbravomebel.ru/upload/iblock/1d8/1d8ac136a305052cfef3aa354a4e3fbb.jpg"
DIM_REF = "https://tdbravomebel.ru/upload/iblock/d54/d54bbfce5960976e0000ec42866d468d.jpg"
DETAIL_REF = "https://tdbravomebel.ru/upload/iblock/388/388aa9dae62c044c97c6c70e5925e10c.jpg"
ANGLE_REF = "https://tdbravomebel.ru/upload/iblock/823/82355357f3aedc6568280edd82123770.jpg"

FIDELITY = (
    "CRITICAL image-to-image rules: Keep the IDENTICAL wall unit layout as the reference — "
    "exactly these 8 modules in the same positions and proportions: TV stand, chest 2-door 6 drawers, "
    "display cabinet ШР-1, display cabinet ШР-2, chest 5 drawers, tall wardrobe ШР-2, chest 6 drawers, wall mirror. "
    "Do NOT add any extra cabinets, shelves, sideboards, bookcases, or duplicate modules. "
    "Preserve EXACT product colors: muted matte sapphire blue polyurethane MDF facades, "
    "dark brown wood veneer sides (Taksus corpus), silver metal bar handles. "
    "Do NOT increase saturation, do NOT shift to bright royal blue or green, do NOT use gold handles. "
    "Professional Ozon marketplace photo, vertical 3:4, photorealistic, sharp, no watermark, no price tags."
)

SLOTS: dict[str, dict] = {
    "01-main.png": {
        "refs": [MAIN_REF],
        "prompt": (
            f"{FIDELITY} "
            "Place the same wall unit on pure white studio background, full product visible, "
            "soft even lighting, no people, no room decor, no text — Ozon main photo."
        ),
    },
    "02-infographic.png": {
        "refs": [MAIN_REF, LAYOUT_REF],
        "prompt": (
            f"{FIDELITY} "
            "Clean infographic on light neutral background: same wall unit front view with subtle "
            "dimension lines 401×218×52 cm and icons for 8 modules, minimal Russian labels, "
            "professional catalog style."
        ),
    },
    "03-lifestyle.png": {
        "refs": [MAIN_REF],
        "prompt": (
            f"{FIDELITY} "
            "Same wall unit in a modern living room, warm natural daylight, light gray walls, "
            "minimal decor (one plant, floor lamp), no people, furniture arrangement unchanged."
        ),
    },
    "04-details.png": {
        "refs": [DETAIL_REF, MAIN_REF],
        "prompt": (
            f"{FIDELITY} "
            "Close-up macro of sapphire matte MDF facade, milled edge, silver handle and hinge — "
            "exact colors from reference, shallow depth of field."
        ),
    },
    "05-angle.png": {
        "refs": [ANGLE_REF, MAIN_REF],
        "prompt": (
            f"{FIDELITY} "
            "Three-quarter angle view of the same 8-module wall unit in empty light room, "
            "shows depth, no extra furniture pieces."
        ),
    },
    "06-layout.png": {
        "refs": [LAYOUT_REF, MAIN_REF],
        "prompt": (
            f"{FIDELITY} "
            "Composition layout diagram: all 8 modules of Goritsiya NCM Sapphire set shown as in dealer layout, "
            "same colors, catalog explainer style on white background."
        ),
    },
    "07-utp.png": {
        "refs": [MAIN_REF],
        "prompt": (
            f"{FIDELITY} "
            "Selling photo: modular living room wall system, same exact configuration, "
            "subtle visual emphasis on storage and display cabinets, bright clean interior."
        ),
    },
    "08-interior.png": {
        "refs": [MAIN_REF],
        "prompt": (
            f"{FIDELITY} "
            "Wide living room shot: same wall unit with TV on TV stand module, sofa in foreground blur, "
            "do not add or remove any wall modules."
        ),
    },
    "09-dimensions.png": {
        "refs": [DIM_REF, MAIN_REF],
        "prompt": (
            f"{FIDELITY} "
            "Technical dimensions image: wall unit with height 218 cm width 401 cm depth 52 cm markers, "
            "same module layout as reference schematic."
        ),
    },
    "10-series.png": {
        "refs": [MAIN_REF],
        "prompt": (
            f"{FIDELITY} "
            "Studio catalog photo of the complete 8-piece Goritsiya NCM Sapphire wall set, "
            "slight perspective, white-to-light-gray gradient background."
        ),
    },
}
