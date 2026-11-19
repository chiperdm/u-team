#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-.}"
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[U-ORG] Changed files:"
  git -C "$ROOT" status --short
  echo "[U-ORG] Diff summary:"
  git -C "$ROOT" diff --stat
fi
