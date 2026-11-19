# Glassmorphism Quality Standard
## Surface recipe
Use a restrained layered surface: translucent tint/fill, subtle 1px edge highlight, optional low-opacity shadow, and backdrop blur only when supported and measured.

## Required implementation sequence
1. Inspect renderer/framework/platform and current theme/surface components.
2. Identify one pilot surface (for example, a navigation bar or card).
3. Define reusable tokens for tint, alpha, blur, border, shadow, and fallback.
4. Keep text/icons readable over both light and dark or variable backgrounds.
5. Add an opaque fallback for unsupported devices, reduced transparency, or performance pressure.
6. Avoid nested backdrop filters, huge blur radii, full-screen blur layers, blanket parent opacity, excessive glow, and animated blur by default.
7. Preserve layout dimensions, navigation state, hit targets, semantics, gestures, and scrolling.
8. Capture before/after screenshots at identical viewport, theme, text scale, and state.
9. Profile on a representative low/mid-range device if blur is used.
10. Expand only after the pilot passes visual, accessibility, and performance checks.

## Never
- Do not put critical text directly on a busy image without a scrim.
- Do not blur every container.
- Do not introduce a new design framework just to create glass.
- Do not delete existing theme variants or component APIs.
