---
name: testing-strategy
description: "Plan tests from acceptance criteria and risk; keep them deterministic; handle flaky tests; choose unit/integration/e2e levels for Flutter, Kotlin, Node and web. Use when asked to add tests, decide what to test, fix flaky tests, or define the test plan for a feature."
domain: quality
---

# Test strategy

- Derive tests from acceptance criteria and regression risk; many fast unit tests, fewer integration, a few end-to-end on critical flows (login, send/receive, offline resend).
- Run the narrowest relevant test first, then the wider suite. Report exact commands and results; "could not run" is a valid, honest status.
- Deterministic: inject clocks/ids/random, fake network, no `sleep`; isolate state per test.
- Test behavior, not implementation; one reason to fail per test; name tests by scenario.
- Flaky policy: reproduce and fix the race/timing/shared state; quarantine with a ticket and deadline if needed. "Retry until green" hides bugs.
- Golden/snapshot tests only for stable widgets, pinned fonts/viewport/theme; review diffs, never bulk-accept.
- Boundaries: empty, max length, unicode/emoji, concurrent actions, permission denied, offline.
- Coverage is a signal, never a target to game; never fabricate numbers.

## Test plan template
| Criterion / risk | Level (unit/integration/e2e/manual) | Test name | Command | Status |
|---|---|---|---|---|
Add rows for: happy path, each failure path, permissions, offline, concurrency, boundaries, regression of the original bug.

## Stack pointers
Flutter: `flutter-testing`. Kotlin/Compose: `kotlin-compose-foundations` (Compose tests), `kotlin-coroutines-flow` (runTest/Turbine). Node: `backend-api-design-validation` (endpoint matrix), `testing-realtime`. Web: manual checklist in `html-site-builder`, Lighthouse in `web-performance-seo`. Refactors: `refactoring-characterization`.

## Verify
Tests fail when the feature is broken (mutation spot check: temporarily break the code and see red); the suite is deterministic across 3 consecutive runs.

## Related
`code-review-practice`, `debugging-root-cause`, `release-checklist-rollback`.
