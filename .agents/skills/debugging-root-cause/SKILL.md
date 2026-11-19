---
name: debugging-root-cause
description: "Systematic debugging for any bug: reproduce, minimize, hypothesize, bisect, instrument, fix the cause, add a regression test, report. Use before changing code for any bug report, flaky behavior, 'it worked yesterday' regression, or when previous fix attempts did not work."
domain: quality
---

# Root-cause debugging

1. **Reproduce** reliably; write exact steps, version, device, data. If not reproducible, add targeted logging and wait, do not guess-fix.
2. **Minimize** to the smallest failing case.
3. **Hypothesize** 2-3 causes; for each, state what observation would confirm/refute it.
4. **Narrow:** `git bisect` for regressions; binary-search by disabling halves; compare working vs failing environment.
5. **Instrument** (logs, breakpoints, network inspector) and record evidence, not impressions.
6. **Fix the cause**, not the symptom; ask "why" until a process/design gap shows (5 whys).
7. **Regression test** that fails before and passes after.
8. **Report:** symptom, root cause, fix, test, other places with the same pattern, residual risk.
Avoid shotgun changes: one change per experiment.

## Evidence log template
```
Symptom:        <exact message / screenshot / metric>
Environment:    <version, device/OS, data, config>
Repro steps:    1..n (minimal)
Hypotheses:     H1 ... (confirm by X) / H2 ...
Experiments:    <one change> -> <result>
Root cause:     <file:line, why>
Fix + test:     <commit> / <test name>
Same pattern elsewhere: <grep results>
```

## Techniques
`git bisect run <script>` for regressions; add a failing test first; print/log at boundaries (inputs and outputs of each layer); compare a working vs failing trace; rubber-duck the assumptions list ("what must be true for this line to run?"); check recent dependency/config/data changes before suspecting the compiler.

## Pitfalls
- Changing several things at once.
- Declaring victory because the symptom vanished (heisenbugs, timing).
- Skipping the regression test.

## Verify
The regression test fails on the old code and passes on the fix; the original reproduction steps no longer fail; a search for the same pattern elsewhere is recorded; no unrelated changes in the diff.

## Related
`debugging-android-crash-anr`, `testing-strategy`, `realtime-reconnect-client`, `refactoring-characterization`.
