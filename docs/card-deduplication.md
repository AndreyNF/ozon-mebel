# Антидубли карточек

Один **артикул производителя** = одна карточка в репозитории и один `offer_id` на Ozon.  
Перед полной генерацией (фото, Wordstat, лонгрид) — **обязательная проверка**.

## Команда (Шурик и агент)

```bash
py scripts/card_registry.py check Ц0081444
```

Несколько артикулов (серия):

```bash
py scripts/card_registry.py check Ц0081444 Ц0081445 Ц0081446
```

| Код выхода | Значение |
|------------|----------|
| 0 | Дублей нет — можно создавать новую карточку |
| 1 | Есть дубль — **остановиться**, предложить обновление |
| 2 | Дубль (`--strict`) — для скриптов/CI |

## Что считается «уже выпущено»

Проверяются:

1. Запись в `cards/registry.json`
2. Папка `cards/{АРТИКУЛ}/` с любым из:
   - `{АРТИКУЛ}.row.json`
   - `{АРТИКУЛ}.md`
   - `OZON_UPLOAD_*.xlsx`
   - `{АРТИКУЛ}.api-upload.json`
   - `images/*`

## Статусы в реестре

| Статус | Смысл |
|--------|--------|
| `draft` | Черновик, не все артефакты |
| `ready` | row.json + md (+ фото), Excel можно собрать |
| `uploaded` | Был вызов API или есть upload xlsx |
| `published` | Карточка на Ozon (вручную отметить) |

Обновить реестр с диска:

```bash
py scripts/card_registry.py sync
py scripts/card_registry.py list
```

Отметить вручную:

```bash
py scripts/card_registry.py register Ц0081444 --status published --note "на модерации Ozon"
```

## Поведение Шурика

### Если `check` показал DUPLICATE

**Запрещено без явной просьбы пользователя:**

- заново генерировать все фото (`gpt-image-2`);
- заново вызывать `/core` на ту же нишу;
- перезаписывать `row.json` «с нуля».

**Разрешено:**

- точечное обновление (цена, габариты, одно фото);
- `build_upload_excel.py` / `upload_to_ozon.py` после правок;
- дополнение `.research.md` или SEO-полей.

### Если пользователь просит «пересобери полностью»

Только тогда — режим `--force` (зафиксировать в запросе и в `note` реестра).

## Серии

Перед циклом по серии:

```bash
py scripts/card_registry.py check $(cat series/articles.txt)
```

Создавать папки **только** для артикулов с `OK` в выводе check.

## После успешной сборки

```bash
py scripts/card_registry.py register {АРТИКУЛ} --status ready
```

После API-загрузки:

```bash
py scripts/card_registry.py register {АРТИКУЛ} --status uploaded
```
