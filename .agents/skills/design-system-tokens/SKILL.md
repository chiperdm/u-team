---
name: design-system-tokens
description: "Define and generate design tokens shared across CSS, Jetpack Compose and Flutter: colors with light/dark and contrast checks, spacing, radii, type scale, elevation, motion and glass tokens; naming tiers and a generator script. Use when starting a UI, unifying look across web/Android/Flutter, adding dark mode or a theme, or when colors and spacing are hardcoded all over the code."
domain: ui
---

# Design tokens

One source of truth (`tokens.json`) -> generated CSS variables, Kotlin object, Dart class. Components consume tokens, never raw values. Bundled: `assets/tokens.example.json`, `scripts/gen_tokens.py`.

## Tiers and naming
1. **Primitive** (raw): `blue-500 = #5b4bff`, `space-4 = 16`.
2. **Semantic** (role): `bg`, `surface`, `text`, `muted`, `accent`, `onAccent`, `border`, `danger`, `success`. Components use these.
3. **Component** (only when needed): `button.radius`, `glass.sigma`.
Rules: name by role not by value (`accent`, not `purple`); one meaning per token; no token for one-off values; document each token's purpose.

## What to define
- **Color:** light and dark sets designed separately (dark is not inverted: lower saturation, elevated surfaces lighter, avoid pure black/white). Required pairs: `text/bg`, `text/surface`, `onAccent/accent`, `muted/bg` -> contrast >= 4.5:1 (3:1 for large text and UI borders/icons). The generator warns on failures.
- **Spacing:** 4-pt scale `4 8 12 16 24 32 48 64 96`. Layout uses the scale only.
- **Radius:** `sm 8, md 16, lg 28, pill 999`; keep a consistent radius family (glass UIs lean larger).
- **Type:** modular scale (e.g. 1.2-1.25): `12 14 16 18 22 28 36 48`; weights 400/500/600/700; line-height 1.4-1.6 body, 1.1-1.25 headings. Respect user font scale.
- **Elevation/shadow:** 3-4 levels with consistent light direction; in dark themes use surface lightness rather than heavy shadows.
- **Motion:** durations `fast 150 / base 250 / slow 400` ms, easing curves, spring params (`damping 0.6-0.8, stiffness 300-500`), reduced-motion variants.
- **Glass (see `ui-glassmorphism`, `rules/12-liquid-glass.md`):** `sigma 12-20`, `tintAlpha` dark 0.08-0.18 / light 0.45-0.7, `borderAlpha 0.15-0.3`, `fallback` opaque color, `refraction 0.4-0.7`, `depth 16-28`.
- **Z-index/layers:** `base, sticky, overlay, modal, toast` named scale.

## Using the generator
```bash
python3 .agents/skills/design-system-tokens/scripts/gen_tokens.py tokens.json --css out/tokens.css --kotlin out/Tokens.kt --dart out/tokens.dart --package com.example.app.ui
```
- Writes `:root {}` + `@media (prefers-color-scheme: dark)` for CSS; `object Tokens` with `Light`/`Dark` `Color` sets for Compose; `abstract final class Tokens` for Flutter.
- Exit code 1 and a printed table if any required contrast pair fails.
- Generated files carry a "DO NOT EDIT" header: edit `tokens.json` instead and regenerate in CI to catch drift.

## Wiring
- **CSS:** `color-scheme: light dark;` + variables; JS theme toggle sets `data-theme` and persists the choice; `<meta name="theme-color">` per scheme.
- **Compose:** map tokens to `lightColorScheme/darkColorScheme` and a `CompositionLocal` for extras (glass, spacing); dynamic color optional.
- **Flutter:** `ThemeData(colorScheme: ...)` + `ThemeExtension<AppTokens>` for extras (`Theme.of(context).extension<AppTokens>()!`), `copyWith`/`lerp` implemented.

## Migration of an existing app (no rewrite)
1. Inventory raw colors/sizes: `grep -RnoE '#[0-9a-fA-F]{6,8}|Color\(0x' lib app/src src | sort | uniq -c | sort -rn | head -50`.
2. Define tokens that match the *current* look first (zero visual change), screenshot before/after.
3. Replace usages one screen/component at a time; delete dead values.
4. Only then change the look through tokens (one commit).

## Verify
Generator exits 0; screenshots light/dark at 100% and 200% font scale; contrast report attached; no raw hex left in migrated files (`grep`).

## Pitfalls
- Tokens that mirror implementation (`padding-card-left`) instead of intent.
- Dark theme by `filter: invert()`.
- Hardcoded `Colors.white`/`Color.White` for text on glass (breaks light mode).
- Too many near-identical tokens (`gray-100..gray-900` plus 12 custom grays).
