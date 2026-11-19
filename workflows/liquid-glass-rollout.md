# Workflow: Liquid Glass Rollout
1. Baseline: screenshots (light/dark, large text), frame timing on a mid-range device.
2. Tokens: glass sigma/tint/border/refraction/depth/fallback in `tokens.json`; generate platform files.
3. Pilot ONE surface (bottom bar or card) using the tiered implementation (`kotlin-compose-liquid-glass`, `flutter-liquid-glass`, `web-liquid-glass-css`).
4. Fallback matrix verified: older API/browser, battery saver, reduced transparency, high contrast.
5. Measure: frame/raster cost, memory, battery spot check; compare to the budget (max 2-3 glass surfaces/screen).
6. Review: `design-reviewer` (does the glass have something worth blurring?), `accessibility-reviewer` (contrast over worst backdrop).
7. Expand one surface at a time; stop when the budget is reached.
8. Document tokens, fallbacks and limits (ADR).
