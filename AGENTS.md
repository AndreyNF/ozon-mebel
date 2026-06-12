# Ozon-mebel — правила для агента

**Магазин:** торгуем **только мебелью** (корпусная, спальни, детская, гостиная, **кухонная** — гарнитуры, модули, столы, стулья). Категории Ozon — только ветка **Мебель → …**. См. `docs/ozon-categories-mebel.md`.

## Обязательно при каждой карточке

1. **Шаблон Ozon** — xlsx из ЛК для **типа мебели** (шкаф, кухня, стол…), не «Комплекты мебели» для одиночного SKU. Путь категории начинается с **Мебель**.
2. **`docs/ozon-seo.md`** — название без keyword-stuffing, аннотация ≤500 символов, SEO в Rich/хештегах.
3. **Rich-контент JSON v0.3** — только через `py scripts/build_rich_content.py {АРТ}`; формат: `.cursor/rules/ozon-rich-content-json.mdc`, `docs/ozon-rich-content.md`. Перед API — [песочница](https://rich-content.ozon.ru/sandbox). В billboard/chess: `title` и `text` — объекты с `size`/`align`/`color`/`content`, обязателен `imgLink`.
4. **`templates/ozon-card-template.md`** — полная карточка: УТП, FAQ, источники, риски модерации.
5. **Серия фото (обязательно)** — **10 кадров 3:4** в `cards/{АРТ}/images/` (`01-main` … `10-*`). **i2i от фото производителя** — не выдумывать мебель: можно фон, lifestyle, людей; **нельзя** лишние шкафы/модули и неверный цвет. Правило: `.cursor/rules/ozon-photo-fidelity.mdc`, слоты: `.cursor/rules/ozon-photo-series-10.mdc`, промпты `docs/prompts-by-category.md`. **Кухня:** один кадр зоны варки (`08-cooktop`), не три типа плит; `09-sink`, `10-assembly`. Без 10 фото **не загружать** в Ozon.
6. **`docs/ozon-photo-specs.md`** — технические требования Ozon (3:4, без растягивания ЛК).
7. **Wordstat (MCP KV)** — `wordstat_get_top_requests` по 3–5 фразам; обновить `#Хештеги` и `_meta.seo_keywords`.
8. **Сборка:** `py scripts/fill_template.py {АРТ}` → Excel; `--api` — выгрузка в Ozon. `docs/fill-template.md`, `docs/ozon-upload-strategy.md`.
9. **Контент-рейтинг ~100** — `.cursor/rules/ozon-content-rating.mdc`: главное фото i2i от дилера, характеристики категории, **`py scripts/build_video_cover.py {АРТ}`** + `Озон.Видеообложка: ссылка` в row.json.
10. **Артикул производителя** — первым из описания, **не менять**. EAN пустой, если генерирует Ozon.

## Новая карточка от ссылки на товар

Полный цикл без паузы: данные → **10 фото gpt-image-2** → push GitHub → Rich → API.  
Правило: `.cursor/rules/ozon-new-card-pipeline.mdc`.

## Производитель Браво (tdbravomebel.ru)

Ссылка на **tdbravomebel.ru** → автопайплайн без уточнений. Сначала проверка дублей:

`py scripts/bravo_card_registry.py check URL`

Реестр опубликованных: `data/manufacturers/bravo-mebel.json`. Правило: `.cursor/rules/ozon-bravo-mebel.mdc`.  
**1 URL коллекции = 1 карточка Ozon.** После import — дописать в реестр.

## Файлы карточки

```
cards/{АРТИКУЛ}/
  {АРТИКУЛ}.md
  {АРТИКУЛ}.row.json
  {АРТИКУЛ}.rich-content.json
  images/               ← 10 файлов 3:4 (обязательно)
  video/video-cover.mp4 ← видеообложка Ozon (8–30 сек)
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
