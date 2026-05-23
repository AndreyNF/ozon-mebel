# Ozon-mebel — правила для агента

**Магазин:** торгуем **только мебелью** (корпусная, спальни, детская, гостиная, **кухонная** — гарнитуры, модули, столы, стулья). Категории Ozon — только ветка **Мебель → …**. См. `docs/ozon-categories-mebel.md`.

## Обязательно при каждой карточке

1. **Шаблон Ozon** — xlsx из ЛК для **типа мебели** (шкаф, кухня, стол…), не «Комплекты мебели» для одиночного SKU. Путь категории начинается с **Мебель**.
2. **`docs/ozon-seo.md`** — название без keyword-stuffing, аннотация ≤500 символов, SEO в Rich/хештегах.
3. **Rich-контент JSON v0.3** — только через `py scripts/build_rich_content.py {АРТ}`; формат: `.cursor/rules/ozon-rich-content-json.mdc`, `docs/ozon-rich-content.md`. Перед API — [песочница](https://rich-content.ozon.ru/sandbox). В billboard/chess: `title` и `text` — объекты с `size`/`align`/`color`/`content`, обязателен `imgLink`.
4. **`templates/ozon-card-template.md`** — полная карточка: УТП, FAQ, источники, риски модерации.
5. **Серия фото (обязательно)** — **7 кадров 3:4** в `cards/{АРТ}/images/` (`01-main` … `07-utp`), промпты в `docs/prompts-by-category.md`, правило: `docs/ozon-photo-series.md`. Без 7 фото **не загружать** в Ozon. После генерации: push на GitHub → `apply_hosting_urls.py` → Rich с теми же URL.
6. **`docs/ozon-photo-specs.md`** — технические требования Ozon (3:4, без растягивания ЛК).
7. **Wordstat (MCP KV)** — `wordstat_get_top_requests` по 3–5 фразам; обновить `#Хештеги` и `_meta.seo_keywords`.
8. **Сборка:** `py scripts/fill_template.py {АРТ}` → Excel; `--api` — выгрузка в Ozon. `docs/fill-template.md`, `docs/ozon-upload-strategy.md`.
9. **Артикул производителя** — первым из описания, **не менять**. EAN пустой, если генерирует Ozon.

## Новая карточка от ссылки на товар

Полный цикл без паузы: данные → **7 фото gpt-image-2** → push GitHub → Rich → API.  
Правило: `.cursor/rules/ozon-new-card-pipeline.mdc`.

## Файлы карточки

```
cards/{АРТИКУЛ}/
  {АРТИКУЛ}.md
  {АРТИКУЛ}.row.json
  {АРТИКУЛ}.rich-content.json
  images/               ← 7 файлов 3:4 (обязательно)
  images-manifest.json
  OZON_UPLOAD_*.xlsx    — не в git
```

## Шаблон в row.json

```json
"_meta": {
  "ozon_template": "Шкафы_21.05.2026.xlsx",
  "description_category_id": "17027919"
}
```

Переопределение: `$env:OZON_TEMPLATE = "полный путь.xlsx"`.
