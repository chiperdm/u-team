---
name: refactoring-characterization
description: "Refactor existing code without changing behavior: characterization (golden-master) tests, seams, tiny reversible steps, Mikado method, strangler pattern, one-commit-per-step, and verification at each step. Use when asked to clean up, restructure, split a big file or class, modernize legacy code, remove duplication, or migrate an API, in Dart, Kotlin, JS/TS or Python, especially when there are few tests."
domain: quality
---

# Safe refactoring

Command: `/refactor-safe`. Rules: `rules/01-preserve-project.md`. Refactoring = **no behavior change**. Never mix it with features or bug fixes in one commit.

## Procedure
1. **Goal and boundary:** what hurts (duplication, 2000-line file, tangled state)? What is out of scope? Define the end state in 3 lines and the public contracts that must not change (API, routes, DB schema, storage format, channel names, exported functions).
2. **Baseline:** `git status`; run analyzer/tests/build and record results; for UI take screenshots at fixed state. If tests are missing, add characterization tests first.
3. **Characterize:** pin current behavior, including quirks, with tests that call the public surface.
   - Golden master: run the function on a representative set of inputs, store outputs (JSON/text/image), assert equality afterwards. Good for parsers, formatters, calculations, serializers, reducers.
   - For UI: widget/Compose screenshot tests or key semantics assertions (`flutter-testing`, `kotlin-compose-foundations`).
   - For side effects: inject a fake at the seam and assert calls.
4. **Create seams** where code is untestable: extract an interface/function parameter for clock, network, storage, random, platform; pass dependencies via constructor instead of globals. Seam creation itself must be behavior-preserving and tiny.
5. **Plan with Mikado:** write the target change; attempt it; when it breaks, note the prerequisite, revert, do the prerequisite first. The graph of leaf prerequisites is your ordered step list.
6. **Small steps, each green:** one mechanical move at a time, run the narrow tests after each, commit each step (`refactor: extract MessageMapper`). If red and the cause is not obvious in 5 minutes, revert the step (`git restore`/`git revert`, with approval for anything destructive).
7. **Finish:** remove dead code created by the move, update docs/ADR if structure changed, run the full suite, compare screenshots/golden outputs, summarize changed vs preserved.

## Catalog of safe moves
Rename (use the IDE/analyzer-driven rename), Extract function/method/widget/composable, Inline, Extract class/value object, Introduce parameter object, Replace magic numbers with named constants/tokens, Move to the right module/file (one move per commit, keep a re-export shim for external users), Replace conditional with polymorphism/strategy **only** when 3+ branches repeat, Split a large file by cohesion, Replace inheritance with composition, Extract interface at a seam, Convert callback code to async/await/coroutines **after** characterization.
Large migrations (state manager, router, DB layer, API v1->v2): **Strangler fig**: new path next to old, route one use case at a time behind a flag, delete the old path last; keep both working until parity is proven.

## Rules of the road
- No formatting-only diffs mixed in (run the formatter in its own commit, or not at all if it explodes the diff).
- Public names, JSON field names, DB columns, preference keys and deep links are contracts: leave them or migrate with compatibility.
- Don't "fix" suspicious behavior silently: record it as a separate issue/commit with its own test.
- Performance claims need measurements (`performance-profiling-budgets`).
- If the plan exceeds ~10 steps or touches high-risk areas (auth, crypto, migrations), pause and get approval on the plan (`/plan`).

## Verify
Same tests green before and after; golden outputs identical (`diff`); analyzer warnings not increased (`flutter analyze`, `./gradlew lint`, `eslint`, `tsc --noEmit`); app launches and the main flow works; `git diff --stat` matches the plan; report commands and results.

## Pitfalls
- Refactoring without a safety net "because it is just moving code".
- Big-bang rewrites labelled as refactors.
- Changing a function's signature and its behavior in the same step.
- Deleting code that looks unused but is referenced by reflection, serialization, deep links, or platform channels (grep for strings too).
