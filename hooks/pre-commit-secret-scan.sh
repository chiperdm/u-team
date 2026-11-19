#!/usr/bin/env bash
# Lightweight secret-pattern check. Scans ONLY lines added in the staged diff
# (default) or the whole working tree with --all. Not a replacement for gitleaks/trufflehog.
set -euo pipefail
PATTERN="(BEGIN (RSA|OPENSSH|EC|PGP) PRIVATE KEY|(api[_-]?key|secret|token|password|passwd)[[:space:]]*[:=][[:space:]]*[\"'][A-Za-z0-9_./+=-]{12,}[\"']|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,})"
echo "[U-ORG] Secret-pattern check (review findings manually)."
if [[ "${1:-}" == "--all" ]]; then
  ROOT="${2:-.}"
  if grep -RInE --exclude-dir=.git --exclude-dir=node_modules --exclude='*.lock' -e "$PATTERN" "$ROOT"; then
    echo "[U-ORG] Potential secrets found."; exit 1
  fi
else
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then echo "[U-ORG] Not a Git repo; use --all <dir>."; exit 0; fi
  if git diff --cached -U0 --no-color | grep -E '^\+' | grep -vE '^\+\+\+' | grep -nE -e "$PATTERN"; then
    echo "[U-ORG] Potential secrets in staged changes. Do not commit until reviewed."; exit 1
  fi
fi
echo "[U-ORG] No obvious secret patterns found."
