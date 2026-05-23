# Агенты проекта ozon-mebel

| Агент | Команда | Задача |
|-------|---------|--------|
| **Шурик** | `/shurik` (см. README) | Продающие карточки Ozon: текст, фото, Excel/API |
| **ЯДрышко (Core)** | `/core` | Семантическое ядро: Wordstat, кластеры, отчёт HTML/XLSX |

## ЯДрышко — установка и обновление

Субагент из репозитория [Horosheff/yadryshko-semantic-core-subagent](https://github.com/Horosheff/yadryshko-semantic-core-subagent).

**Уже в проекте:**

- `.cursor/agents/core.md` — определение sub-agent
- `docs/core-agent-playbook.md`, `docs/semantic-core-methodology.md`, …
- `scripts/build_core_html_report.py`, `scripts/build_semantic_core_xlsx.py`

**Обновить до последней версии с GitHub:**

```bash
bash scripts/install-yadryshko.sh
```

После установки: перезагрузить окно Cursor (`Reload Window`), если `/core` не появился.

## Wordstat

- В Cursor Cloud: MCP **Kovcheg** (`wordstat_get_top_requests`, …).
- Альтернатива: [MCP-KV Wordstat](https://mcp-kv.ru/docs/wordstat-mcp-setup) — `docs/mcp-kv-wordstat-setup.md`.

## Связка Core → Шурик

1. `/core` — собрать семантику по нише/товару (см. `docs/yadryshko-ozon-mebel.md`).
2. `/shurik` — карточка с ключами из отчёта Core.

Примеры запросов: `examples/yadryshko-ozon-prompt.md`.
