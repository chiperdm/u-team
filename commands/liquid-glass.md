# /liquid-glass
Implement iOS-26-style Liquid Glass (blur + refraction + specular rim) for Compose, Flutter or web as a measured pilot.

**Agents:** glass-ui-engineer, compose-ui-engineer or flutter-engineer or web-frontend-engineer
**Skills:** `kotlin-compose-liquid-glass`, `flutter-liquid-glass`, `web-liquid-glass-css`, `design-system-tokens`

## Steps
1. Detect the platform and minimum API/browser support; choose the tier (library vs own; refraction vs blur-only).
2. Define glass tokens (sigma, tint, border, refraction, depth, fallback).
3. Implement ONE surface (bottom bar, card or button) with fallbacks per `rules/12-liquid-glass.md`.
4. Screenshot light/dark/large text over bright and dark backdrops; profile on a mid-range device.
5. Write the rollout plan (max 2-3 surfaces per screen).

## Output
Pilot code, token file, fallback matrix (API/browser -> result), screenshots, frame numbers or "not run".

## Guardrail
State clearly that samples were not compiled/run if no device was available.
