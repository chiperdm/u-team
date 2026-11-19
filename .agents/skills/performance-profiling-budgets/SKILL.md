---
name: performance-profiling-budgets
description: "Measure and improve performance with baselines and budgets for startup, frames, memory, app size and backend latency across Flutter, Android, web and Node. Use when asked to 'make it faster', before optimizing anything, when users report lag or battery drain, or to set quality gates in CI."
domain: quality
---

# Profiling and budgets

1. Define the budget first (examples to adapt): cold start, frame time p95, memory ceiling, APK/AAB size, API p95 latency, WS delivery latency.
2. Baseline on a representative mid-range device / realistic data volume; note method, device, build mode (profile/release).
3. Change ONE thing; re-measure with the same method; keep the change only if numbers improve and nothing regresses.
4. Tools: Flutter DevTools (Performance, Memory), `flutter build --analyze-size`, Android Studio Profiler / Perfetto, Node `--cpu-prof`/`clinic`, `EXPLAIN ANALYZE`, load tools (k6/autocannon).
5. Fix the demonstrated bottleneck (Amdahl); don't micro-optimize cold paths.
6. Report: before/after table, method, caveats. Never invent measurements.

## Budget table template
| Metric | Budget | Baseline | Method / device | After |
|---|---|---|---|---|
| Cold start (Android) | <= 1.5 s | | `adb shell am start -W` | |
| Frame time p95 | <= 16 ms (60 Hz) | | DevTools / Macrobenchmark | |
| API p95 | <= 300 ms | | k6 / logs | |
| WS delivery p95 | <= 500 ms | | two-client test | |
| LCP (web) | <= 2.5 s | | Lighthouse | |
| APK size | <= N MB | | `--analyze-size` | |
Mobile references: `flutter-performance-jank`, Compose Macrobenchmark + Baseline Profiles (`kotlin-compose-foundations`), `web-performance-seo`.

## Verify
Numbers come from real runs with the method recorded; each optimization lists before/after and was re-run to rule out noise (>= 3 runs, report median).

## Pitfalls
Optimizing without a profile; trusting emulator numbers; comparing across different devices or build modes.

## Related
`database-indexing-query-plans`, `kotlin-compose-liquid-glass`, `flutter-liquid-glass`, `web-motion-scroll`.
