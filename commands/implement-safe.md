# /implement-safe
Implement the approved scope only, preserving architecture and user changes.

**Agents:** owner engineer for the area
**Skills:** `testing-strategy`

## Steps
1. Preflight (status, baseline checks).
2. Inspect affected code and callers.
3. Make small changes; add regression/failure-path tests.
4. Run narrowest checks then wider ones; inspect the full diff.

## Output
Summary, changed files, checks with results, limitations.

## Guardrail
No destructive or production actions. No unrelated cleanup.
