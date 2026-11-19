---
name: ui-glassmorphism
description: "Implement glassmorphism (frosted translucent surfaces with blur) safely in Flutter, Compose or CSS: tokens, contrast, opaque fallback, performance, one-component pilot. Use for glass cards, bars, sheets and dialogs, 'frosted' or 'blur' backgrounds; for refraction/Liquid Glass use the liquid-glass skills."
domain: ui
---

# Glassmorphism

## Principles
- It is a surface recipe, not a global filter: tint + subtle 1 px edge highlight + restrained shadow + backdrop blur.
- Start with ONE surface (nav bar or card) behind the existing component API; compare before/after screenshots at identical viewport/theme/text scale; profile; then expand.
- Define tokens once: `glassSigma 12-20`, `glassTintAlpha 0.08-0.18 (dark) / 0.45-0.7 (light)`, `glassBorderAlpha 0.15-0.3`, `glassFallbackColor`.
- Text/icons need >= 4.5:1 contrast over the WORST background the glass can sit on; add a scrim over busy images.
- Cost: backdrop blur is expensive. No nested blurs, no full-screen blur layers, no animated sigma, keep blurred areas small and clipped. Provide an opaque fallback for low-end devices, high-contrast/reduced-transparency settings and unsupported platforms.

## Flutter
```dart
class GlassSurface extends StatelessWidget {
  const GlassSurface({super.key, required this.child, this.radius = 20, this.sigma = 16, this.enableBlur = true});
  final Widget child; final double radius, sigma; final bool enableBlur;

  @override
  Widget build(BuildContext context) {
    final r = BorderRadius.circular(radius);
    final cs = Theme.of(context).colorScheme;
    if (!enableBlur || MediaQuery.highContrastOf(context)) {
      return DecoratedBox(decoration: BoxDecoration(color: cs.surface, borderRadius: r), child: child);
    }
    return ClipRRect(
      borderRadius: r,
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: sigma, sigmaY: sigma),
        child: DecoratedBox(
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.10),   // Flutter >= 3.27; older: withOpacity
            borderRadius: r,
            border: Border.all(color: Colors.white.withValues(alpha: 0.20)),
          ),
          child: child,
        ),
      ),
    );
  }
}
```
`enableBlur` comes from a user/perf setting (e.g. low-end device flag). BackdropFilter blurs everything behind it, so keep it inside a ClipRRect/ClipRect.

## CSS
```css
.glass { background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.22); border-radius: 20px; }
@supports (backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px)) {
  .glass { -webkit-backdrop-filter: blur(16px) saturate(140%); backdrop-filter: blur(16px) saturate(140%); }
}
@media (prefers-reduced-transparency: reduce) { .glass { background: var(--surface-opaque); backdrop-filter: none; } }
```

## Compose glass-lite
`Modifier.blur` blurs the composable's **own content**, not what is behind it, so it cannot make a glass bar by itself (and is a no-op below API 31). Backdrop blur in Compose needs either a library (Haze) or a captured background layer: see `kotlin-compose-liquid-glass` (library path and `GraphicsLayer` path, API-level fallbacks). Keep the same tokens (`design-system-tokens`) and an opaque `surfaceContainer` fallback.

## Escalation path
Frosted (this skill) -> Liquid Glass with refraction: `kotlin-compose-liquid-glass`, `flutter-liquid-glass`, `web-liquid-glass-css`. Tokens: `design-system-tokens`. Review: `ui-design-review`, `rules/12-liquid-glass.md`.

## Verify
Before/after screenshots at identical state; contrast over worst backdrop; opaque fallback renders when blur is off; profile numbers on a mid-range device (`flutter-performance-jank` or Perfetto).

## Pitfalls
Glass over a flat color (no effect), stacked glass layers, animating sigma, text directly on busy photos, forgetting Safari's `-webkit-backdrop-filter`.
