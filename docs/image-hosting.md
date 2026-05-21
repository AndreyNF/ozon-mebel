# Фото для Ozon — хранение в репозитории

## Где лежат файлы

```
cards/{АРТИКУЛ}/images/
├── 01-main.png              ← главное (белый фон)
├── 02-infographic.png
├── 03-lifestyle-woman.png   ← с людьми (продающее)
├── 04-lifestyle-interior-ref.jpg
├── 05-dimensions-ref.jpg
├── 05-interior-cutaway-ref.jpg
└── 06-angle-ref.jpg
```

**Правило Шурика:** сразу после `gpt-image-2` сохранять PNG в эту папку (`scripts/download_image.py`). Не оставлять только tempfile-ссылки.

## Публичные URL для Ozon

Ozon принимает **прямые HTTPS-ссылки** на jpeg/png.

1. Залейте репозиторий на GitHub (или Яндекс.Облако / свой CDN).
2. В `hosting.config.json` укажите `public_base_url`:
   ```json
   "public_base_url": "https://raw.githubusercontent.com/USER/ozon-mebel/main"
   ```
3. Запустите:
   ```bash
   py scripts/apply_hosting_urls.py Ц0081444
   ```
4. В `filled-template.xlsx` подставятся постоянные URL.

## Поля, которые не заполняем

| Поле | Правило |
|------|---------|
| Штрихкод EAN | пусто — генерирует Ozon |
| ТН ВЭД | пусто, если не требует модерация |
| Габариты упаковки | задаёт пользователь отдельно |

## Продающие фото с людьми

- **Слот 3+** — lifestyle **с людьми** (женщина/пара/семья в интерьере).
- **Слот 1** — только товар на белом/светлом фоне (требование Ozon для главного).
- Без лиц крупным планом на главном фото; на доп. — можно.
