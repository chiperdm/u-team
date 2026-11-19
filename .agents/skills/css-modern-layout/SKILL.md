---
name: css-modern-layout
description: "Write modern, robust CSS layout: grid and flexbox patterns, container queries, fluid type with clamp, logical properties, dvh/svh viewport units, :has(), cascade layers, color-mix/oklch, sticky and overflow pitfalls. Use when fixing layout bugs, making a page responsive, replacing media-query hacks, or when CSS looks fragile or overflows on mobile."
domain: web
---

# Modern CSS layout

Check support on MDN/Baseline before using anything newer than your audience's browsers; provide a sane fallback.

## Patterns that replace most media queries
```css
/* Auto-fit card grid: no breakpoints */
.grid { display: grid; gap: 1.5rem; grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr)); }

/* Sidebar that wraps by itself */
.with-sidebar { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.with-sidebar > :first-child { flex: 1 1 16rem; }
.with-sidebar > :last-child  { flex: 999 1 24rem; }

/* Centered content column with full-bleed escape */
.wrap { width: min(1120px, 100% - 2rem); margin-inline: auto; }

/* Fluid type and spacing (min, preferred, max) */
h1 { font-size: clamp(2.2rem, 1.6rem + 3vw, 4rem); }
section { padding-block: clamp(3rem, 8vw, 7rem); }

/* Stack with consistent rhythm */
.stack > * + * { margin-block-start: var(--stack, 1rem); }

/* Keep media from distorting */
.thumb { aspect-ratio: 16 / 9; object-fit: cover; width: 100%; }
```

## Container queries: components respond to their slot, not the viewport
```css
.card-wrap { container-type: inline-size; container-name: card; }
.card { display: grid; gap: 1rem; }
@container card (min-width: 32rem) { .card { grid-template-columns: 12rem 1fr; } }
```

## Viewport units on mobile
`100vh` ignores the dynamic browser toolbar. Use `100svh` (small, always visible), `100dvh` (dynamic), `100lvh` (large). Full-screen hero: `min-height: 100svh`. Sticky bottom bars: `padding-bottom: env(safe-area-inset-bottom)` and `<meta name="viewport" content="..., viewport-fit=cover">`.

## Selectors and cascade
- `:has()` for parent/state styling: `.field:has(input:invalid) { border-color: crimson; }`.
- `:where()` has zero specificity (good for resets/utility defaults); `:is()` keeps the highest specificity inside.
- `@layer reset, base, components, utilities;` makes override order explicit and ends `!important` wars.
- Native nesting is supported in current browsers (`.card { &:hover { ... } .title { ... } }`).
- Logical properties for RTL/i18n: `margin-inline`, `padding-block`, `inset-inline-start`, `border-start-start-radius`.
- Colors: `oklch()` for perceptual ramps; `color-mix(in srgb, var(--accent) 20%, transparent)` for tints; `light-dark(#fff, #000)` with `color-scheme: light dark`.

## Sticky, scroll and overflow
- `position: sticky` fails if any ancestor has `overflow: hidden/auto/scroll` (use `overflow: clip` on the ancestor) or the element has no `top`.
- Grid/flex children overflow because of `min-width: auto`: set `min-width: 0` on the child (or `overflow: hidden`) so long words, `<pre>`, tables and images shrink.
- Horizontal page scroll: find the culprit with `* { outline: 1px solid red }` or `document.querySelectorAll('*')` checking `scrollWidth > clientWidth`; usual suspects are `100vw` (includes scrollbar; use `100%`), negative margins, wide tables/code, fixed widths.
- Scroll containers: `overscroll-behavior: contain`, `scroll-snap-type: x mandatory` + `scroll-snap-align: start`, `scrollbar-gutter: stable`.
- `z-index` only works within a stacking context: `isolation: isolate` on a component stops z-index leaks; `transform`, `filter`, `opacity < 1`, `position: fixed` all create contexts.

## Debug recipe
1. DevTools: toggle grid/flex overlays, inspect computed `min-width`, `width`, stacking context.
2. Reproduce at 320 px and with 200% text zoom.
3. Fix at the root layout rule, not with a per-element pixel patch.

## Verify
320/375/768/1024/1440 px screenshots, text zoom 200%, RTL (`dir="rtl"`) if i18n matters, print stylesheet if the page is printed, no horizontal scroll.

## Pitfalls
- Using `px` for font sizes breaks user font preferences: use `rem`.
- `gap` on flex works in all modern browsers; avoid margin hacks.
- Don't set `height: 100%` chains; use `min-height` and let content grow.
- `aspect-ratio` plus explicit `height` fights: choose one.
