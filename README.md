# Ozon — карточки мебели (Шурик)

## Шаблон Ozon

**Excel:** `templates/Комплекты мебели_21.05.2026.xlsx`  
**Категория:** Комплекты мебели  
**Поля:** `docs/ozon-template-komplekty-mebeli.md`

## Минимальный вход

**Артикул производителя** — обязателен, не меняется.

Плюс: референс-фото / ссылка конкурента / описание производителя.

## Пример

```text
/shurik
Артикул: Севилья
Комната: Детская
Конкурент: https://www.ozon.ru/product/...
```

## Структура

```
ozon-mebel/
├── templates/Комплекты мебели_21.05.2026.xlsx
├── docs/
│   ├── shurik-instructions.md   ← промпт агента
│   └── ozon-category-routing.md
├── scripts/fill_ozon_template.py
└── cards/{АРТИКУЛ}/
    ├── {АРТИКУЛ}.md
    ├── {АРТИКУЛ}.row.json
    ├── images-manifest.json
    └── filled-template.xlsx
```

## Фото

3–7 шт., MCP `gpt-image-2`, **3:4**, 2K.  
**Главное** — белый/светлый фон (col 15). **Доп.** — lifestyle, инфографика (col 16).  
Промпты: `docs/prompts-by-category.md` по полю **Комната**.
