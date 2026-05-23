# Rich-контент Ozon (JSON v0.3)

Правило для агента: `.cursor/rules/ozon-rich-content-json.mdc`.

Источники: [seller-edu — загрузка Rich](https://seller-edu.ozon.ru/libra/work-with-goods/zagruzka-tovarov/zagruzka-media/rich-content), [песочница](https://rich-content.ozon.ru/sandbox).

## Ошибка «JSON не соответствует шаблону»

Чаще всего:

| Проблема | Как должно быть |
|----------|-----------------|
| `billboard.text` без полей | `"text": {"size":"size2","align":"left","color":"color1","content":[...]}` |
| `billboard.title` строка | объект `"title": {"content":["..."], "size":"size4", ...}` |
| Нет `imgLink` в billboard/chess | `"imgLink": ""` |
| Символы `•`, `×` в тексте | убрать или заменить на `-` / `x` |
| chess блоков < 2 | минимум 2, максимум 6 |

## Сборка в проекте

```powershell
py scripts/build_rich_content.py Ц0111571
py scripts/build_rich_content.py Ц0081444
```

Скрипт пишет `{АРТ}.rich-content.json` и поле **Rich-контент JSON** в `row.json`.

## Виджеты

- **raTextBlock** — заголовок + текст
- **raShowcase billboard** — 1 большой блок: фото + заголовок + текст
- **raShowcase chess** — 2–6 пар фото/текст
- **raShowcase roll** — галерея (только `img`, без title)
- **raVideo** — YouTube ID (опционально)

## URL картинок

Прямые HTTPS (GitHub raw после push). Размеры `width`/`height` — пропорции исходника; для 3:4 типично 768×1024, mobile 750×1000.

## Проверка

1. Скопировать JSON из `{АРТ}.rich-content.json`
2. Вставить в https://rich-content.ozon.ru/sandbox
3. Если OK — `py scripts/ozon_api_import.py {АРТ}`
