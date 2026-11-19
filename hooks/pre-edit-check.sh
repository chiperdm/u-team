#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-.}"
if ! git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[U-ORG] Not a Git repository; inspect files carefully before editing."
  exit 0
fi
echo "[U-ORG] Current repository status:"
git -C "$ROOT" status --short
echo "[U-ORG] Preserve all existing uncommitted changes. Do not overwrite user work."
