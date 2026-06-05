# Ozon: автоответы на вопросы, отзывы и чат

Скрипт `scripts/ozon_comms_poll.py` опрашивает Ozon Seller API и отвечает покупателям по шаблонам и FAQ из `cards/{АРТ}/`.

## Что нужно

| Компонент | Обязательно | Примечание |
|-----------|-------------|------------|
| `OZON_CLIENT_ID` + `OZON_API_KEY` | да | как для импорта карточек |
| **Premium Plus** | для вопросов и отзывов | без подписки API вернёт 403; **чат работает** |
| `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | нет | сводка после каждого опроса |
| GitHub Actions secrets | для cron | те же переменные |

## Запуск локально

```bash
# Просмотр черновиков без отправки
python3 scripts/ozon_comms_poll.py --all --dry-run

# Автоответ в чат (и вопросы/отзывы, если Premium Plus)
python3 scripts/ozon_comms_poll.py --all

# Только чат
python3 scripts/ozon_comms_poll.py --chat

# С уведомлением в Telegram
python3 scripts/ozon_comms_poll.py --all --notify-telegram
```

## Переменные окружения

```bash
OZON_COMMS_DRY_RUN=0          # 1 — не отправлять ответы
OZON_COMMS_AUTO_CHAT=1
OZON_COMMS_AUTO_QUESTIONS=1
OZON_COMMS_AUTO_REVIEWS=1
OZON_COMMS_NOTIFY_TELEGRAM=0  # 1 — сводка в Telegram после опроса
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## Как формируется ответ

1. **FAQ из карточки** — блоки `**В:**` / `**О:**` в `{АРТ}.md`
2. **Данные row.json** — комплектация, сборка, гарантия, аннотация
3. **Сопоставление SKU** — из `ozon-live-status_{АРТ}.json` → артикул
4. **Шаблоны** — вежливые ответы на отзывы (4–5★ — благодарность, 1–3★ — извинение + просьба написать в чат)

Системные чаты Ozon (уведомления, курсы, Premium) **пропускаются** — отвечаем только на сообщения покупателя (`user.type = customer`).

## Автоматизация (GitHub Actions)

Workflow `.github/workflows/ozon-comms-poll.yml` — **каждые 15 минут**:

- опрос чата / вопросов / отзывов;
- автоответ;
- артефакт логов `data/ozon-comms-logs/`.

Ручной запуск: Actions → **Ozon buyer comms auto-reply** → Run workflow.

## Файлы состояния

| Путь | Назначение |
|------|------------|
| `data/ozon-comms-state.json` | уже обработанные id (не дублировать ответы) |
| `data/ozon-comms-logs/ozon-comms-YYYY-MM-DD.jsonl` | журнал входящих и ответов |

## Ограничения

- Без **Premium Plus** доступен только **чат** (`/v3/chat/list`, `/v1/chat/send/message`).
- Ответы rule-based (FAQ + шаблоны), не LLM — для сложных кейсов проверяйте логи.
- Остатки FBS и модерация карточек — отдельно.
