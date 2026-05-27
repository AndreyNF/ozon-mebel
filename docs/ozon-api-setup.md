# Ozon Seller API

## Ключи

1. [seller.ozon.ru](https://seller.ozon.ru) → Настройки → API-ключи (Seller API, товары + цены).
2. В корне репозитория: `cp .env.example .env` и заполнить `OZON_CLIENT_ID`, `OZON_API_KEY`.

## Карточка Киви (после push фото в GitHub)

```bash
pip install -r requirements.txt
py scripts/build_rich_content.py Ц0011713
py scripts/apply_hosting_urls.py Ц0011713
py scripts/ozon_sync_import_payload.py Ц0011713
py scripts/validate_ozon_card.py Ц0011713
py scripts/ozon_api_import.py Ц0011713 --sync-payload
py scripts/ozon_api_product_status.py Ц0011713
py scripts/ozon_api_stocks.py Ц0011713 --stock 1
```

Повторить для `Ц0023320`.

При `imported` со статусом `skipped` скрипт импорта сам вызовет `/v1/product/pictures/import`.
