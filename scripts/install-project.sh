#!/usr/bin/env bash
# Install the pack into a project. Never overwrites: existing files are skipped (merge mode).
# Usage: install-project.sh /path/to/project [--dry-run] [--skills-only]
set -euo pipefail
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET=""; DRY=0; SKILLS_ONLY=0
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    --skills-only) SKILLS_ONLY=1 ;;
    -h|--help) sed -n '2,4p' "$0"; exit 0 ;;
    *) TARGET="$a" ;;
  esac
done
if [[ -z "$TARGET" || ! -d "$TARGET" ]]; then
  echo "Usage: $0 /path/to/project [--dry-run] [--skills-only]"; exit 2
fi
ITEMS=(.agents rules commands hooks workflows templates docs evals)
[[ $SKILLS_ONLY -eq 1 ]] && ITEMS=(.agents/skills)
copied=0; skipped=0
copy_tree() {
  local rel="$1"
  while IFS= read -r -d '' f; do
    local r="${f#"$BASE"/}"
    if [[ -e "$TARGET/$r" ]]; then
      skipped=$((skipped+1)); echo "skip (exists): $r"
    else
      copied=$((copied+1))
      if [[ $DRY -eq 1 ]]; then echo "would copy:   $r"; else mkdir -p "$TARGET/$(dirname "$r")"; cp -p "$f" "$TARGET/$r"; fi
    fi
  done < <(find "$BASE/$rel" -type f -print0)
}
for item in "${ITEMS[@]}"; do [[ -e "$BASE/$item" ]] && copy_tree "$item"; done
if [[ $SKILLS_ONLY -eq 0 ]]; then
  if [[ -e "$TARGET/AGENTS.md" ]]; then
    echo "AGENTS.md exists: writing AGENTS.u-org.md next to it; merge the routing table manually."
    [[ $DRY -eq 1 ]] || cp -p "$BASE/AGENTS.md" "$TARGET/AGENTS.u-org.md"
  else
    echo "copy: AGENTS.md"; [[ $DRY -eq 1 ]] || cp -p "$BASE/AGENTS.md" "$TARGET/AGENTS.md"
  fi
  mkdir -p "$TARGET/scripts" 2>/dev/null || true
  for s in validate-pack.py new-skill.py; do
    [[ -e "$TARGET/scripts/$s" ]] || { echo "copy: scripts/$s"; [[ $DRY -eq 1 ]] || cp -p "$BASE/scripts/$s" "$TARGET/scripts/$s"; }
  done
fi
echo "Done: $copied copied, $skipped skipped$([[ $DRY -eq 1 ]] && echo ' (dry run)')."
echo "Reload your IDE and confirm which of .agents/, rules/, commands/ it discovers; hooks need manual wiring."
