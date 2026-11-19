---
name: flutter-performance-jank
description: "Diagnose and fix Flutter UI jank, slow lists, heavy blur/shadows, large images, shader warmup, and JSON/crypto work on the main isolate using DevTools in profile mode. Use for dropped frames, scroll stutter, slow startup, high memory, or after adding glass/blur effects."
domain: flutter
---

# Flutter performance

- **Measure in profile mode on a real mid-range device**, not debug/emulator. DevTools Performance: look for frames over 16 ms (60 Hz) / 8 ms (120 Hz), raster vs UI thread.
- UI-thread heavy: rebuild storms, big `build()`, sync parsing. Fix with `const`, narrower rebuilds, `compute`/`Isolate.run` for JSON/crypto/image work.
- Raster-heavy: `BackdropFilter`, `saveLayer` (`Opacity`, `ShaderMask`, `ClipRRect` with antialias-layers, big shadows), overdraw. Replace `Opacity` with color alpha; limit blur to small clipped regions.
- Lists: `ListView.builder`, stable `Key`s, avoid shrinkWrap in long lists, fixed `itemExtent` when possible, no heavy work in item `build`.
- Images: `cacheWidth/cacheHeight` close to display size, thumbnails for chat lists, `precacheImage` only for the next screen.
- `RepaintBoundary` only where profiling shows repaint isolation helps.
- Animations: prefer implicit/`AnimatedBuilder` scoped to the moving subtree; no animated blur by default.
- Report before/after numbers (avg/worst frame time, jank count) and device model.

## Procedure
1. Profile build on a mid-range device: `flutter run --profile`; DevTools Performance -> record the janky interaction.
2. Classify: UI thread (build/layout) vs raster thread (paint/GPU) vs jank on first run (shader compilation; Impeller reduces this on supported platforms).
3. Fix the top offender only; re-measure with the same steps; record avg/worst frame ms and jank count.
4. Memory: DevTools Memory snapshot before/after a screen is closed (leaks from listeners/controllers/images).
Startup: defer non-critical init (`runApp` early), lazy-load heavy services, avoid sync file/JSON work before first frame; check `flutter build apk --analyze-size`.

## Verify
Numbers before/after in the report with device model, build mode and steps; no regressions on a low-end device; glass effects have an opaque fallback (`ui-glassmorphism`, `flutter-liquid-glass`).

## Pitfalls
- Judging performance in debug mode or on an emulator.
- `RepaintBoundary` everywhere (adds layers/memory).
- Full-screen `BackdropFilter` or animated blur.
- Decoding full-size images for thumbnails (`cacheWidth`).

## Related
`performance-profiling-budgets`, `flutter-chat-ui`, `kotlin-compose-foundations` (the Compose equivalents).
