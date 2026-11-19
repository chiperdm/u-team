---
name: code-review-practice
description: "Review a diff or pull request like a senior engineer: intent and design first, then correctness, security, error handling, tests, performance, readability; severity labels, evidence from actually running code, stack-specific checklists (Flutter/Dart, Kotlin/Compose, Node/TS, SQL), and a concise report. Use for any code review, PR review, 'check my changes', pre-merge or pre-release review."
domain: quality
---

# Code review practice

The reviewer is **not** the author and does not edit code (`code-reviewer`, read-only). Output: `templates/review-report.md`. Command: `/review`.

## Procedure
1. **Scope:** `git status`, `git diff --stat <base>...HEAD`, read the task/PR description and acceptance criteria. If intent is unclear, say what you assumed.
2. **Understand before judging:** read changed files in full context, callers and tests. Find the contracts touched (API, schema, storage, routes, channels).
3. **Run things:** analyzer, tests, build for the touched module (narrowest first). Reproduce the bug/feature if possible. "Looks right" is not evidence: record commands and results or say "not run".
4. **Review passes (in order, stop to report blockers early):**
   1. Intent and design: right problem, smallest sufficient change, fits existing architecture, no needless dependency/abstraction.
   2. Correctness: edge cases (empty, null, max, unicode, concurrency, offline, time zones), off-by-one, async ordering, resource cleanup, idempotency (`api-idempotency`), state consistency.
   3. Security and privacy: authz on every object access, input validation, injection/XSS, secrets, logging of sensitive data, permissions, crypto misuse (`security-*`, `e2ee-messaging-review`).
   4. Errors and failure paths: handled, surfaced to user appropriately, not swallowed, retried safely, timeouts.
   5. Tests: cover acceptance criteria and failure paths, deterministic, fail before/pass after for bug fixes.
   6. Performance: obvious N+1, unbounded lists/loops, main-thread work, rebuild storms, large images, missing indexes (`database-indexing-query-plans`).
   7. Compatibility: old clients, migrations backward compatible, minSdk/OS support, API versioning.
   8. Readability/maintainability: naming, function size, duplication, dead code, comments for why, consistent style.
5. **Report** findings with severity and evidence; praise specific good decisions briefly; list what you did not review.

## Severity labels
- **Blocker:** security hole, data loss/corruption, crash, broken contract, failing build/tests, violated acceptance criteria.
- **Major:** likely bug, missing failure handling, missing tests for risky logic, perf problem on a hot path.
- **Minor:** maintainability issues, small inconsistencies.
- **Nit:** taste/style (batch them; mark non-blocking).
Each finding: `file:line`, what is wrong, why it matters (impact), concrete fix or question. Prefer questions when unsure ("What happens if `chatId` is not a member?").

## Stack checklists
**Flutter/Dart:** `mounted` after await; controllers/subscriptions disposed; no I/O in `build`; keys on list items; `const` where possible; no new state library; `ListView.builder`; images sized; strings localized (`localization-flutter`); a11y semantics; platform channel errors handled.
**Kotlin/Compose:** no `GlobalScope`/`runBlocking` on main; flows collected with lifecycle; state hoisted; stable lazy keys; no heavy work in composition; permissions/foreground-service types correct; `exported` flags; ProGuard/R8 keep rules; DB migrations tested.
**Node/TS:** every route validated and authorized; async errors handled (no unhandled rejections); no secrets in logs; parameterized SQL; timeouts and limits; graceful shutdown; no sync fs/crypto in hot path; tests for 401/403/422.
**SQL/migrations:** reversible or documented, lock-safe, batched backfills, indexes concurrent, RLS present and tested (`database-*`).
**Web:** escaping, CSP/CORS, focus and keyboard, contrast, responsive, performance budget, no layout shift.

## Review etiquette
Be specific and kind; critique code, not people; explain the "why"; distinguish must-fix from suggestions; keep reviews timely and small (ask to split diffs > ~500 lines); don't bikeshed what a formatter/linter decides; if you disagree on approach, state trade-offs and let the owner decide unless it is a blocker.

## Output template
```
## Verdict: APPROVE / APPROVE WITH COMMENTS / REQUEST CHANGES / BLOCK
## Evidence: commands run + results (or "not run: reason")
## Blockers / Major / Minor / Nits (table or list with file:line)
## Risks & rollback notes
## Not reviewed
```

## Pitfalls
- Approving without running anything.
- Reviewing only the diff and missing the unchanged caller that now breaks.
- 40 nits and no verdict.
- Rewriting the author's design in review comments instead of flagging the actual problem.

## Verify (your own review)
Before sending: every finding has file:line and evidence; commands you ran are listed with results; blockers are separated from nits; you stated what you did not review.
