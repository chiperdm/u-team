---
name: html-site-builder
description: "Build complete, polished, responsive HTML/CSS/JS websites (landing pages, portfolios, product pages, docs, app promo sites) with semantic markup, design tokens, dark mode, accessibility, SEO and performance baked in. Use whenever the user asks for a website, landing page, HTML page, site for an app/bot/product, portfolio or promo page, even if they only say 'make a site' or 'сделай сайт'."
domain: web
---

# HTML site builder

Goal: a site that opens by double-click, looks designed rather than templated, passes basic a11y/perf checks, and is easy to edit. Starter file: `assets/starter.html` (tokens, dark mode, nav, hero, features, FAQ, CTA, footer). Copy it, then redesign; do not ship it unchanged.

## Process
1. **Brief (5 lines, assume if missing and state assumptions):** what it is, audience, the ONE primary action (download, sign up, contact), tone, languages (add ru/kk/en switch only if asked), assets available.
2. **Pick a direction before coding.** One memorable idea: type pairing, one accent color, layout rhythm. Examples: editorial (large serif + tight grid), product-tech (mono details + glass cards, see `web-liquid-glass-css`), playful (oversized type, sticker shapes). Avoid the generic look: purple gradient hero, three identical icon cards, emoji as icons, centered everything, stock testimonial grid.
3. **Information architecture:** hero (value in <= 12 words + CTA + visual) -> proof (numbers, logos, screenshots, short demo) -> how it works (3 steps) -> features (max 6, grouped) -> pricing or download -> FAQ (objections) -> final CTA -> footer (legal, contact). Cut sections that have no real content; never invent fake reviews, stats or logos.
4. **Tokens first** (`design-system-tokens`): colors (bg, surface, text, muted, accent, border), 4-pt spacing scale, type scale via `clamp()`, radii, shadows. Everything references variables.
5. **Build mobile-first**, semantic landmarks (`header nav main section footer`), one `h1`, headings in order.
6. **Layer enhancements:** dark mode, reduced motion, glass (optional), scroll reveals (`web-motion-scroll`).
7. **Content pass:** real copy, specific verbs, no lorem ipsum, no "revolutionary/cutting-edge". Alt text, link text that makes sense out of context.
8. **Quality pass:** run the checklist below.

## Structure and delivery choices
- Small site: single `index.html` with inline `<style>` and `<script>` (zero build, easy to host). Larger: `index.html`, `css/`, `js/`, `img/`; no framework unless the project already has one.
- Libraries only when they save real work; if used, pin versions and self-host or use a CDN with SRI (`integrity` + `crossorigin`).
- Fonts: system stack by default (`ui-sans-serif, system-ui, ...`); custom fonts self-hosted as WOFF2, subset, `font-display: swap`, preload only the one used above the fold. Cyrillic/Kazakh letters need a font that actually covers them (check `Ә Ғ Қ Ң Ө Ұ Ү Һ І`).
- Images: AVIF/WebP + fallback, explicit `width`/`height`, `loading="lazy"` below the fold, hero image `fetchpriority="high"`. SVG for icons/illustrations; inline only small ones.
- Forms: use a real endpoint (formspree-like service, your backend, `mailto:` as a fallback). Never fake a success message. Add `autocomplete`, `type`, `required`, visible labels; honeypot or CAPTCHA for public forms.
- Links: `rel="noopener"` for `target="_blank"` (default in modern browsers, still explicit). Phone `tel:`, mail `mailto:`.
- Legal: privacy policy link if you collect any data; cookie banner only if you actually set non-essential cookies.

## Head essentials (copy-paste)
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Product: what it does in 5 words | Brand</title>
  <meta name="description" content="One sentence, 120-155 chars, benefit + audience.">
  <link rel="canonical" href="https://example.com/">
  <meta name="theme-color" content="#0b0d12" media="(prefers-color-scheme: dark)">
  <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
  <meta property="og:title" content="..."><meta property="og:description" content="...">
  <meta property="og:image" content="https://example.com/og.png"><meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%236d5efc'/%3E%3C/svg%3E">
</head>
```

## Design rules of thumb
- Type: 1-2 families, 4 sizes in use, body 16-18 px, line-height 1.5-1.7, measure 45-75 characters (`max-width: 68ch`).
- Spacing: sections 64-128 px vertical on desktop, 48-72 on mobile; consistent 4/8-pt steps.
- One primary button per view; secondary = ghost/outline. Buttons >= 44 px tall.
- Color: neutral base + one accent + semantic states; check contrast (4.5:1 text, 3:1 large text/UI).
- Hierarchy through size, weight, contrast and whitespace, not through boxes everywhere.
- Hero visual should show the product (screenshot/device mock/animated demo), not a stock photo.
- Motion: purposeful, 150-400 ms, transform/opacity only, `prefers-reduced-motion` respected.

## Verify: deliverable checklist (all must be true)
- [ ] Opens offline from disk (or states what needs a server); no console errors; no 404s.
- [ ] Works at 320, 375, 768, 1024, 1440, 1920 px; no horizontal scroll; tap targets >= 44 px.
- [ ] Keyboard: logical tab order, visible `:focus-visible`, skip link, menu/FAQ operable with keyboard.
- [ ] Contrast OK in light and dark; `lang` set; images have `alt` (empty for decorative).
- [ ] Lighthouse (mobile): Performance, Accessibility, Best Practices, SEO >= 90 where achievable; record real numbers or say "not run".
- [ ] OG image, favicon, canonical, `robots.txt`/`sitemap.xml` for multi-page sites (`web-performance-seo`).
- [ ] HTML validates (`npx html-validate index.html` or the W3C Nu checker).
- [ ] Final answer lists files, how to open/deploy, what is placeholder.

## Hosting notes
Static hosts (GitHub Pages, Cloudflare Pages, Netlify, Vercel, Render Static Sites) need no build for plain HTML. Custom domain + HTTPS are on by default there. Set cache headers for hashed assets; keep `index.html` revalidated.

## Pitfalls
- `100vh` on mobile hides content behind browser UI: use `100svh`/`100dvh` (`css-modern-layout`).
- Text inside images is not accessible or translatable.
- Autoplay video/audio without `muted`/user gesture is blocked.
- Smooth-scroll hijacking and parallax everywhere hurt usability: use sparingly.
- A fixed header covers anchored sections: add `scroll-margin-top`.
