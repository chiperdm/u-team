# /refactor-safe
Restructure code without changing behavior.

**Agents:** technical-architect, test-engineer, owner engineer
**Skills:** `refactoring-characterization`

## Steps
1. Define goal, boundary and protected contracts.
2. Add characterization tests for current behavior.
3. Plan steps (Mikado); one small move per commit.
4. Run regression checks after each step; keep a revertable diff.

## Output
Step list, commits, checks per step, preserved contracts.

## Guardrail
No behavior change, no mass formatting, no feature mixing.
