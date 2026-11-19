# /review
Independent read-only review of the current diff.

**Agents:** code-reviewer
**Skills:** `code-review-practice`

## Steps
1. Scope the diff and read the task.
2. Run analyzers/tests for touched modules.
3. Walk passes: intent, correctness, security, errors, tests, performance, compatibility, readability.

## Output
Verdict + findings by severity with file:line + evidence + not reviewed (`templates/review-report.md`).

## Guardrail
Do not edit files.
