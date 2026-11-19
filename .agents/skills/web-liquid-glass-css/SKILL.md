---
name: web-liquid-glass-css
description: "Create Liquid Glass / glassmorphism for HTML and CSS sites: backdrop-filter blur and saturate, SVG displacement-map refraction (Chromium), specular rim, dark and light variants, fallbacks for Safari and Firefox, reduced transparency, performance. Use for glass navbars, cards, modals, buttons, dock bars, or whenever a website needs an iOS 26 / frosted glass look."
domain: web
---

# Liquid Glass for the web

Three tiers, always layered as progressive enhancement. Tier 1 is the baseline everywhere.

## Tier 1: frosted glass (all modern browsers)
```css
:root {
  --glass-bg: rgb(255 255 255 / .10);
  --glass-border: rgb(255 255 255 / .22);
  --glass-opaque: #1c1f26;                       /* fallback, used when blur is unavailable */
}
.glass {
  position: relative; isolation: isolate;
  border-radius: 28px;
  background: var(--glass-opaque);
  border: 1px solid var(--glass-border);
  box-shadow:
    inset 0 1px 0 rgb(255 255 255 / .45),         /* top specular edge */
    inset 0 -1px 0 rgb(255 255 255 / .08),
    0 10px 30px rgb(0 0 0 / .25);                 /* soft drop shadow */
}
@supports (backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px)) {
  .glass {
    background: var(--glass-bg);
    -webkit-backdrop-filter: blur(16px) saturate(160%);
    backdrop-filter: blur(16px) saturate(160%);
  }
}
@media (prefers-reduced-transparency: reduce), (prefers-contrast: more) {
  .glass { background: var(--glass-opaque); -webkit-backdrop-filter: none; backdrop-filter: none; }
}
```
Gradient rim (specular highlight) without extra markup:
```css
.glass::before {
  content: ""; position: absolute; inset: 0; border-radius: inherit; padding: 1px; pointer-events: none;
  background: linear-gradient(135deg, rgb(255 255 255 / .6), rgb(255 255 255 / .05) 45%, rgb(255 255 255 / .3));
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
}
```

## Tier 2: refraction with an SVG displacement map (Chromium only)
`backdrop-filter: url(#filter)` with SVG filters works in Chromium browsers (Chrome, Edge, Opera, Android WebView). Safari and Firefox ignore it, so keep tier 1 as the base and apply tier 2 only after detecting Chromium. Never rely on `CSS.supports` alone for this.
```html
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <filter id="lens" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
    <feImage id="lens-map" result="map" preserveAspectRatio="none"/>
    <feDisplacementMap in="SourceGraphic" in2="map" scale="40" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
</svg>
```
```js
// Builds a displacement map for a rounded rect: neutral = rgb(128,128), edge pixels push samples inward.
function lensMap(w, h, r, depth = 24) {
  const c = Object.assign(document.createElement('canvas'), { width: w, height: h });
  const g = c.getContext('2d'), img = g.createImageData(w, h);
  const hx = w / 2, hy = h / 2;
  const sd = (x, y) => { const qx = Math.abs(x) - hx + r, qy = Math.abs(y) - hy + r;
    return Math.min(Math.max(qx, qy), 0) + Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) - r; };
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const px = x - hx, py = y - hy, d = sd(px, py);
    const t = Math.min(Math.max(-d / depth, 0), 1), k = Math.pow(1 - t, 3);
    const nx = sd(px + 1, py) - sd(px - 1, py), ny = sd(px, py + 1) - sd(px, py - 1);
    const len = Math.hypot(nx, ny) || 1;
    const i = (y * w + x) * 4;
    img.data[i]     = 128 - (nx / len) * k * 127;   // R -> x displacement
    img.data[i + 1] = 128 - (ny / len) * k * 127;   // G -> y displacement
    img.data[i + 2] = 128; img.data[i + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  return c.toDataURL();
}
const isChromium = !!navigator.userAgentData?.brands?.some(b => /Chromium/.test(b.brand));
document.querySelectorAll('.glass.lens').forEach(el => {
  if (!isChromium) return;
  const { width, height } = el.getBoundingClientRect();
  document.getElementById('lens-map').setAttribute('href', lensMap(Math.round(width), Math.round(height), 28));
  el.style.backdropFilter = 'url(#lens) blur(2px) saturate(160%)';
});
```
Notes: one filter per distinct size (clone the `<filter>` with a unique id per element when sizes differ); regenerate on resize with a debounce; the map is computed once per size, never per frame. The same-size `scale` attribute controls strength (`scale=40` is a starting value, tune by eye).

## Tier 3: interaction
- Hover/press: `transform: scale(1.03)` with `transition: transform .35s cubic-bezier(.2,.9,.3,1.3)`; brighter rim on `:hover`/`:focus-visible`.
- Morphing dock/tab indicator: animate `translate` + `width` of a glass pill (CSS `anchor` positioning is optional and still new, check support).
- Respect `@media (prefers-reduced-motion: reduce)`: no scale, no spring.

## Rules that save you hours
- A **backdrop root** limits what a `backdrop-filter` can see. An ancestor with `filter`, `opacity < 1`, `mask`, `mix-blend-mode`, `will-change: filter/opacity` or its own `backdrop-filter` makes the child blur only that ancestor's content. Keep glass elements close to the root stacking context; don't put one glass inside another.
- Glass needs something to blur: use gradient mesh, imagery, or colored blobs behind it. On flat color it looks like a bad card.
- Text contrast >= 4.5:1 over the worst backdrop: add a tint (`--glass-bg` alpha .18-.30 on light imagery) or a scrim behind small text. Don't put long paragraphs on glass.
- Performance: small surfaces, <= 3 visible, no animated blur radius, no `backdrop-filter` on a full-viewport scrolling element. Check with Chrome DevTools Performance and Layers panels.
- Safari needs the `-webkit-` prefix for `backdrop-filter`.

## Verify
Chrome, Safari (macOS/iOS) and Firefox screenshots; toggle `prefers-reduced-transparency` and `prefers-contrast` in DevTools rendering emulation; Lighthouse accessibility contrast audit; confirm the page is fully usable (and readable) with `backdrop-filter` disabled.
