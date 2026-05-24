# Ozon Seller API — ключи и загрузка карточек

## 1. Ключи

1. [seller.ozon.ru](https://seller.ozon.ru) → **Настройки → API-ключи**
2. Тип: **Seller API** (не Performance)
3. Права: **товары** — чтение и запись; при необходимости **цены**
4. Скопировать **Client-Id** и **API key** (ключ показывается один раз)
5. В корне репозитория:

```bash
cp .env.example .env
# заполнить OZON_CLIENT_ID и OZON_API_KEY
```

`.env` в git не попадает.

## 2. Первичная настройка (один раз)

Подтянуть `type_id` и id атрибутов для категории «Комплекты мебели»:

```bash
py scripts/ozon_sync_config.py --type-name "Шкаф"
```

Обновится `config/ozon-api-komplekty-mebeli.json`.

Если бренд в справочнике Ozon не принимается как текст, добавьте в `dictionary_value_hints`:

```json
"85:ДСВ": 123456789
```

(`dictionary_value_id` можно найти через API или в ЛК при выборе бренда.)

## 3. Одна карточка → Ozon (модерация)

После того как Шурик собрал `cards/{АРТИКУЛ}/{АРТИКУЛ}.row.json`:

```bash
# Проверить payload без отправки
py scripts/upload_to_ozon.py Ц0081444 --dry-run

# Отправить в Ozon (карточка уходит в проверку/модерацию)
py scripts/upload_to_ozon.py Ц0081444
```

Результат: `cards/{АРТИКУЛ}/{АРТИКУЛ}.api-upload.json` — `task_id`, `status`, ошибки.

**Важно:** отдельной кнопки «на модерацию» в API нет. Вызов `POST /v3/product/import` создаёт/обновляет карточку; Ozon сам запускает валидацию и модерацию. Статусы смотрите в ЛК или через `import/info` (`imported`, `failed`, ошибки в `errors`).

## 4. Серия товаров

### Вариант A — манифест JSON (удобно для линейки «Мори»)

`series/mori.example.json`:

```json
{
  "series": "Mori",
  "defaults": {
    "Бренд*": "ДСВ",
    "Название модели (для объединения в одну карточку)*": "Mori",
    "Объединить в похожие товары": "Мори"
  },
  "articles": [
    "Ц0081444",
    "Ц0081445"
  ]
}
```

Загрузка:

```bash
py scripts/upload_series_to_ozon.py --manifest series/mori.json
```

### Вариант B — список артикулов

`series/mori-articles.txt` — по одному артикулу на строку:

```text
Ц0081444
Ц0081445
# комментарии через #
```

```bash
py scripts/upload_series_to_ozon.py --list-file series/mori-articles.txt
```

### Вариант C — несколько артикулов в команде

```bash
py scripts/upload_series_to_ozon.py --articles Ц0081444 Ц0081445 Ц0081446 --delay 3
```

### Вариант D — все готовые row.json по маске

```bash
py scripts/upload_series_to_ozon.py --glob "cards/Ц008*/Ц008*.row.json"
```

Отчёт: `series/upload-report-*.json`.

## 5. Как передать серию Шурику

Один запрос на всю серию:

```text
/shurik серия Mori
Артикулы:
- Ц0081444 | Поставщик: https://... | Производитель: https://...
- Ц0081445 | Поставщик: https://... | Производитель: https://...
Общее: бренд ДСВ, серия Mori, комната Детская
После сборки: py scripts/upload_series_to_ozon.py --manifest series/mori.json
```

Шурик для **каждого** артикула создаёт папку `cards/{АРТИКУЛ}/`, затем вы (или агент с ключами) запускаете пакетную загрузку.

## 6. Шурик + автоотправка

Если в `.env` заданы ключи, агент после `build_upload_excel.py` может вызвать:

```bash
py scripts/upload_to_ozon.py {АРТИКУЛ}
```

Рекомендуется сначала `--dry-run`, пока не отлажен `type_id` и бренды.

## 7. Excel vs API

| Способ | Когда |
|--------|--------|
| `OZON_UPLOAD_*.xlsx` | ручная проверка в ЛК, массовая правка |
| `upload_to_ozon.py` | сразу в Ozon без Excel |

Оба варианта используют одни и те же данные в `row.json`.

## 8. Ошибки

| Ошибка | Решение |
|--------|---------|
| `Не задан type_id` | `ozon_sync_config.py` или `_meta.api.type_id` в row.json |
| HTTP 403 | расширить права ключа |
| `invalid TypeId` | неверный тип для категории |
| Бренд не из справочника | `dictionary_value_hints` для id 85 |
