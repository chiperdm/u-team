# Liquid Glass Standard (extends 03-glassmorphism)
Liquid Glass = backdrop blur + lens refraction at the rim + specular rim + tint + springy interaction.
- Pilot ONE surface first; tokens: sigma, tint alpha (dark/light), border alpha, refraction, depth, fallback color.
- Tiered implementation: refraction where supported (Android API 33+ AGSL, Flutter fragment shaders, Chromium SVG displacement), blur-only where not, opaque tonal fallback everywhere else.
- Fallback triggers: battery saver, low-RAM device, reduced transparency / high contrast, unsupported API/browser, shader load failure.
- Budget: <= 2-3 glass surfaces visible, small areas, no nested glass, no animated blur radius, no full-screen refraction.
- Needs a backdrop worth blurring (texture/color variety); otherwise use a plain surface.
- Contrast >= 4.5:1 for text over the worst backdrop; add tint/scrim; keep semantics unchanged.
- Evidence required: before/after screenshots (light/dark/large text), frame/raster numbers on a mid-range device, fallback screenshots. Say "not run" if no device was available.
