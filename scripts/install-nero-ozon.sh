#!/usr/bin/env bash
# Установить в ozon-mebel только агентов Nero Network, нужных для карточек Ozon.
# Источник: https://github.com/Horosheff/nero-network-office-page
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="https://github.com/Horosheff/nero-network-office-page.git"
TMP_DIR="$(mktemp -d)"

cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

echo "Installing Nero agents (Ozon subset) into ${ROOT}"

if [ -d "/tmp/nero-network-office-page/.git" ]; then
  SOURCE="/tmp/nero-network-office-page"
else
  git clone --depth 1 "$REPO" "$TMP_DIR/repo"
  SOURCE="$TMP_DIR/repo"
fi

mkdir -p "$ROOT/.cursor/agents" "$ROOT/.cursor/skills" "$ROOT/vendor/nero-network-office-page"

cp -r "$SOURCE/agents" "$ROOT/vendor/nero-network-office-page/"
cp -r "$SOURCE/skills/researcher-artyom" "$ROOT/.cursor/skills/researcher-artyom-ozon"
cp "$SOURCE/shared/agent-pipeline-pitfalls.md" "$ROOT/docs/nero-agent-pipeline-pitfalls.md"
cp "$SOURCE/agents/artyom.md" "$ROOT/.cursor/agents/artyom.md"

export ROOT
python3 << 'PY'
import os
import re
from pathlib import Path

root = Path(os.environ["ROOT"])
artyom = root / ".cursor/agents/artyom.md"
text = artyom.read_text(encoding="utf-8")
if "ozon-mebel" not in text:
    patch = """
## Проект ozon-mebel

Ты работаешь **не над WordPress-лонгридом**, а над **карточкой товара на Ozon**.

**Вход от Шурика:** ссылки поставщика, производителя, 1–3 карточки конкурентов на `ozon.ru`.

**Выход:** `cards/{АРТИКУЛ}/{АРТИКУЛ}.research.md`:

- факты ТТХ (приоритет **производитель**);
- что пишут конкуренты в title, буллетах;
- УТП и возражения;
- риски модерации.

Не делай hero, canvas, FTP, WordPress.

"""
    text = text.replace("## Твоя задача — deep research", patch + "\n## Твоя задача — deep research")
    text = re.sub(
        r"офиса Nero Network\. Следуй скиллу \*\*researcher-artyom\*\*",
        "проекта ozon-mebel. Следуй скиллу **researcher-artyom-ozon**",
        text,
        count=1,
    )
    artyom.write_text(text, encoding="utf-8")

skill = root / ".cursor/skills/researcher-artyom-ozon/SKILL.md"
st = skill.read_text(encoding="utf-8")
st = st.replace("researcher-artyom", "researcher-artyom-ozon")
st = st.replace("WordPress-тема **Configured WordPress Theme**", "**маркетплейс Ozon**, корпусная/кухонная мебель")
if "ozon.ru" not in st:
    st += """

## Ozon-mebel

- Анализируй карточки конкурентов на **ozon.ru**.
- Сверяй ТТХ с сайтом производителя и поставщика.
- Результат: `cards/{АРТИКУЛ}/{АРТИКУЛ}.research.md`.
"""
    skill.write_text(st, encoding="utf-8")
PY

chmod +x "$ROOT/scripts/install-nero-ozon.sh"
echo "OK. Agents: shurik, artyom, zhenya-ozon, core. Docs: docs/nero-ozon-agents.md"
