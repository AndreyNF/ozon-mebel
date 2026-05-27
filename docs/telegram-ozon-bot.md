# Telegram-бот для Ozon-mebel

Отдельный бот **не использует** MCP Kovcheg (тот привязан к другому проекту). Уведомления идут через `scripts/telegram_*.py` и Bot API.

## Секреты в Cloud Agents (репозиторий `AndreyNF/ozon-mebel`)

| Переменная | Обязательно | Описание |
|------------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | да | Токен от [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | да | Куда слать сообщения (личка или группа) |

После добавления секретов **перезапустите Cloud Agent** — в списке должно быть не только `ozon_client_id, ozon_api_key`, но и telegram-переменные.

Локально: `cp .env.example .env` и те же ключи.

## Получить `TELEGRAM_CHAT_ID`

1. Напишите боту `/start`.
2. Откройте в браузере:  
   `https://api.telegram.org/bot<ВАШ_ТОКЕН>/getUpdates`
3. Скопируйте `"chat":{"id": ...}`.

Для группы: добавьте бота в группу, напишите сообщение, снова `getUpdates` (id обычно отрицательный).

## Проверка

```bash
python3 scripts/telegram_notify.py
```

Ожидается: `OK message_id=...` и сообщение в Telegram.

## Чаты и вопросы Ozon

```bash
# Непрочитанные сообщения покупателей → Telegram
python3 scripts/ozon_chat_notify.py

# Без отправки
python3 scripts/ozon_chat_notify.py --dry-run
```

**Вопросы в карточке** (`/v1/question/list`) на вашем кабинете требуют **Premium Plus** — через API пока 403. Их можно пересылать боту вручную или подключить Premium.

## Что будет слать агент

- тест подключения;
- непрочитанные чаты с покупателем;
- (позже) черновики ответов, ошибки импорта карточек.

Токен **не коммитить** в git.
