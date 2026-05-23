# Ozon — карточки мебели (Шурик)

## Агенты

| Агент | Команда | Назначение |
|-------|---------|------------|
| **Шурик** | `/shurik` | Оркестратор: research → текст → фото → Excel/API |
| **ЯДрышко (Core)** | `/core` | Семантика Wordstat, кластеры |
| **Артём** | Task `artyom` | Research: поставщик, производитель, Ozon |
| **Женя Ozon** | Task `zhenya-ozon` | Продающий копирайт карточки |

`docs/agents.md` · `docs/nero-ozon-agents.md` · `docs/yadryshko-ozon-mebel.md`

## Шаблон Ozon

**Excel:** `templates/Комплекты мебели_21.05.2026.xlsx`  
**Категория:** Комплекты мебели  
**Поля:** `docs/ozon-template-komplekty-mebeli.md`

## Минимальный вход

**Артикул производителя** — обязателен, не меняется.

Плюс: **поставщик**, **производитель**, конкурент Ozon, комната.

**Перед новой карточкой** — проверка дубля (не тратить генерацию зря):

```bash
py scripts/card_registry.py check {АРТИКУЛ}
```

`docs/card-deduplication.md` · реестр `cards/registry.json`


## Пример

```text
/shurik
Артикул: Ц0081444
Поставщик: https://33komoda.ru/...
Производитель: https://dsv-mebel.ru/...
Конкурент: https://www.ozon.ru/product/...
Комната: Детская
```

## Структура

```
ozon-mebel/
├── .cursor/agents/           ← shurik, core, artyom, zhenya-ozon
├── templates/
├── docs/
├── research/semantic-core-runs/
├── scripts/
│   ├── install-yadryshko.sh
│   └── install-nero-ozon.sh
└── cards/{АРТИКУЛ}/
    ├── {АРТИКУЛ}.md
    ├── {АРТИКУЛ}.research.md   ← Артём
    ├── {АРТИКУЛ}.row.json
    └── images/
```

## Фото

3–7 шт., MCP `gpt-image-2`, **3:4**, 2K.  
**Главное** — белый/светлый фон (col 15).  
Промпты: `docs/prompts-by-category.md`.

## Установка агентов

```bash
bash scripts/install-yadryshko.sh   # /core
bash scripts/install-nero-ozon.sh   # artyom + skill
```

Reload Window в Cursor после установки.
