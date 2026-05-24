#!/usr/bin/env bash
# Обновить ЯДрышко (Core) из upstream GitHub в текущий проект.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="Horosheff/yadryshko-semantic-core-subagent"
BRANCH="main"
ZIP_URL="https://github.com/${REPO}/archive/refs/heads/${BRANCH}.zip"
TMP_DIR="$(mktemp -d)"

cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

echo "Installing YADryshko Core into ${ROOT}"

if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$ZIP_URL" -o "$TMP_DIR/repo.zip"
elif command -v wget >/dev/null 2>&1; then
  wget -q "$ZIP_URL" -O "$TMP_DIR/repo.zip"
else
  echo "Error: need curl or wget"; exit 1
fi

unzip -q "$TMP_DIR/repo.zip" -d "$TMP_DIR/src"
SOURCE="$(find "$TMP_DIR/src" -maxdepth 1 -type d | tail -n 1)"

mkdir -p "$ROOT/.cursor/agents" "$ROOT/docs" "$ROOT/scripts" "$ROOT/templates"
cp "$SOURCE/.cursor/agents/core.md" "$ROOT/.cursor/agents/core.md"
cp "$SOURCE"/docs/*.md "$ROOT/docs/"
cp "$SOURCE/scripts/build_core_html_report.py" "$ROOT/scripts/"
cp "$SOURCE/scripts/build_semantic_core_xlsx.py" "$ROOT/scripts/"
cp "$SOURCE"/templates/*.md "$ROOT/templates/"

export ROOT
python3 << 'PY'
import os
from pathlib import Path

root = Path(os.environ["ROOT"])
p = root / ".cursor/agents/core.md"
text = p.read_text(encoding="utf-8")
insert = """
## Проект ozon-mebel (интеграция)

Этот репозиторий — карточки мебели на **Ozon** (агент **Шурик**). Для семантики карточек, а не сайта:

- запросы вида: `/core шкаф белый 90 см распашной для спальни` или ниша + конкурент Ozon;
- папка прогона: `research/semantic-core-runs/ozon-{товар}-{date}/`;
- результат передай **Шурику**: ключи из `04-keywords-clean.csv` / `05-clusters.csv` → `#Хештеги`, название, аннотация (`docs/ozon-seo.md`).

**Wordstat в этом проекте:** MCP-сервер **Kovcheg** (`wordstat_get_top_requests`, `wordstat_get_user_info`). Если недоступен — см. `docs/mcp-kv-wordstat-setup.md` (MCP-KV).

Подробно: `docs/yadryshko-ozon-mebel.md`.

"""
marker = "Перед работой прочитай методологию пакета:"
if "Проект ozon-mebel" not in text:
    text = text.replace(marker, insert + "\n" + marker)
text = text.replace(
    "Используй MCP Wordstat через сервер `user-mcp-kv`, если он подключён:",
    "Используй MCP Wordstat через сервер **Kovcheg** (приоритет в этом репозитории) или `user-mcp-kv`, если подключён:",
)
p.write_text(text, encoding="utf-8")
PY

chmod +x "$ROOT/scripts/install-yadryshko.sh"
echo "OK. Reload Cursor. Docs: docs/agents.md"
