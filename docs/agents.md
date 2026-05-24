# Агенты проекта ozon-mebel

Главная задача: **продающие карточки товара на Ozon** (мебель).

## Карта агентов

| Агент | Команда / Task | Задача |
|-------|----------------|--------|
| **Шурик** | `/shurik` | Оркестратор: research → текст → фото → row.json → Excel/API |
| **ЯДрышко (Core)** | `/core` | Wordstat, кластеры, HTML/XLSX в `research/semantic-core-runs/` |
| **Артём** | Task `artyom` | Research: поставщик, производитель, конкуренты Ozon → `.research.md` |
| **Женя Ozon** | Task `zhenya-ozon` | Продающее название, аннотация, FAQ, хештеги (не лонгрид) |

Подробная схема Nero (что взяли / что нет): **`docs/nero-ozon-agents.md`**.

## Антидубли

`py scripts/card_registry.py check {АРТИКУЛ}` — `docs/card-deduplication.md`.

## Типовой пайплайн одной карточки

```text
/shurik
Артикул: Ц0081444
Поставщик: https://...
Производитель: https://...
Конкурент Ozon: https://www.ozon.ru/product/...
Комната: Детская
```

1. **Core** (если нет семантики) — `/core` + ниша товара.
2. **Артём** — `cards/Ц0081444/Ц0081444.research.md`.
3. **Шурик** — row.json, фото (`gpt-image-2`), Rich, Excel.
4. **Женя Ozon** — финальная вычитка продающих полей.

## Установка и обновление

| Пакет | Скрипт |
|-------|--------|
| ЯДрышко (Core) | `bash scripts/install-yadryshko.sh` |
| Nero (Артём + skill) | `bash scripts/install-nero-ozon.sh` |

После установки: **Reload Window** в Cursor.

## Wordstat

MCP **Kovcheg** (`wordstat_get_top_requests`) — для Core и при необходимости для Артёма.  
Альтернатива: [MCP-KV](https://mcp-kv.ru/docs/wordstat-mcp-setup) — `docs/mcp-kv-wordstat-setup.md`.

## Документы

- `docs/yadryshko-ozon-mebel.md` — Core + Шурик
- `docs/nero-ozon-agents.md` — роли Nero Office
- `docs/ozon-seo.md` — поля карточки
- `examples/yadryshko-ozon-prompt.md` — примеры `/core`

## Что не установлено

Полный [Nero Network Office](https://github.com/Horosheff/nero-network-office-page) (WordPress, hero, FTP, Директор, Коля, Юра…) — **отдельный продукт**, в ozon-mebel не нужен для карточек.
