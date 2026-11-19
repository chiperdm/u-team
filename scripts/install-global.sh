#!/usr/bin/env bash
set -euo pipefail
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${ANTIGRAVITY_CONFIG_DIR:-$HOME/.gemini/antigravity}"
STAMP="$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DEST/skills" "$DEST/agents"
copy_items() {
  local src="$1" dst="$2"
  for item in "$src"/*; do
    [[ -e "$item" ]] || continue
    local name="$(basename "$item")"
    if [[ -e "$dst/$name" ]]; then
      cp -a "$dst/$name" "$dst/${name}.backup-${STAMP}"
      echo "Backup: $dst/${name}.backup-${STAMP}"
    fi
    cp -a "$item" "$dst/$name"
  done
}
copy_items "$BASE/.agents/skills" "$DEST/skills"
copy_items "$BASE/.agents/agents" "$DEST/agents"
echo "Global copy complete: $DEST"
echo "Verify the global customization path in your installed Antigravity version."
echo "Project rules/commands/hooks are intentionally not auto-registered."
