---
name: web-motion-scroll
description: "Add tasteful web animation: CSS transitions/keyframes, Intersection Observer reveals, scroll-driven animations (animation-timeline), View Transitions API, Web Animations API, spring-like easing with linear(), reduced-motion support and performance rules. Use when the user wants animated sections, scroll effects, page transitions, micro-interactions or a more alive site."
domain: web
---

# Web motion and scroll effects

Motion explains change and gives feedback; it is not decoration. Budget: 150-400 ms for UI feedback, up to ~800 ms for large entrances, one orchestrated entrance per view.

## Rules
1. Animate only `transform` and `opacity` (compositor-friendly). Avoid animating `width/height/top/left/margin`, large `box-shadow`, or `filter: blur()` on big areas.
2. Respect users: wrap non-essential motion in `@media (prefers-reduced-motion: no-preference)` (or disable inside `reduce`). Provide pause for anything that loops > 5 s.
3. Progressive enhancement: content must be visible without JS/animation support (add the "hidden" state with a `.js` class set by script, as in `html-site-builder/assets/starter.html`).
4. No scroll-jacking, no parallax on text, no animation blocking interaction.
5. `will-change` only on elements about to animate, and remove after.

## Recipes
**Hover/press feedback with overshoot (spring-like) using `linear()`**
```css
:root { --spring: linear(0, .22 8%, .65 19%, .98 31%, 1.1 42%, 1.04 56%, .99 70%, 1 100%); }
.btn { transition: transform .5s var(--spring); }
.btn:hover { transform: scale(1.04); } .btn:active { transform: scale(.97); }
```
**Reveal on scroll (Intersection Observer, works everywhere)**
```js
const io = new IntersectionObserver((es) => es.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
}), { threshold: .15, rootMargin: '0px 0px -10% 0px' });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));
```
Stagger with `style="--i:2"` and `transition-delay: calc(var(--i) * 80ms)`.

**Scroll-driven animation (CSS only; check current browser support, keep the IO fallback)**
```css
@supports (animation-timeline: view()) {
  .reveal { animation: rise linear both; animation-timeline: view(); animation-range: entry 0% entry 60%; }
  @keyframes rise { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: none; } }
}
.progress { position: fixed; inset: 0 0 auto 0; height: 3px; transform-origin: 0 50%; background: var(--accent);
  animation: grow linear both; animation-timeline: scroll(root); }
@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
```
**View Transitions (smooth state or page changes)**
```js
function go(update) {
  if (!document.startViewTransition || matchMedia('(prefers-reduced-motion: reduce)').matches) return update();
  document.startViewTransition(update);               // same-document (SPA-like) transitions
}
```
```css
@view-transition { navigation: auto; }              /* cross-document transitions for multi-page sites (where supported) */
.card-img { view-transition-name: hero; }           /* unique name per element on screen */
```
**Web Animations API for dynamic values**
```js
el.animate([{ transform: 'translateY(12px)', opacity: 0 }, { transform: 'none', opacity: 1 }],
           { duration: 350, easing: 'cubic-bezier(.2,.8,.2,1)', fill: 'both' });
```
**Marquee/ticker, loaders:** CSS keyframes with `transform: translateX`, `animation-play-state: paused` on `:hover` and under reduced motion.

## Verify
DevTools Performance: no long tasks or layout/paint storms during the animation; Rendering panel "Paint flashing" and "Layout shift regions"; emulate `prefers-reduced-motion: reduce`; test on a low-end phone profile (CPU 4x slowdown).

## Pitfalls
- Animating from `display: none` does nothing: toggle a class/`hidden`, or use `@starting-style` + `transition-behavior: allow-discrete` where supported.
- `position: fixed` inside a `transform`ed ancestor stops being viewport-fixed.
- Scroll-linked JS on every `scroll` event: use IO, CSS timelines, or passive listeners with `requestAnimationFrame`.
- Infinite animations on many elements drain battery.
