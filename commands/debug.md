# /debug
Reproduce, isolate and fix a bug at its root cause.

**Agents:** debugger, then the owner engineer
**Skills:** `debugging-root-cause`, `debugging-android-crash-anr`

## Steps
1. Reproduce before editing; capture the smallest useful logs/stack trace.
2. Form 2-3 hypotheses; test each with an observation.
3. Bisect regressions; instrument boundaries.
4. Write a failing regression test; implement the smallest fix; re-run.

## Output
Symptom, root cause (file:line), fix, test, same-pattern search results, residual risk.

## Guardrail
Do not guess-fix or clean up unrelated code.
