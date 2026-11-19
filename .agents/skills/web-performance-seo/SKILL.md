---
name: web-performance-seo
description: "Make websites fast and discoverable: Core Web Vitals (LCP, INP, CLS), image/font/JS/CSS loading, caching, compression, plus SEO basics (meta, canonical, Open Graph, JSON-LD, sitemap, robots, hreflang for ru/kk/en). Use when optimizing page speed or Lighthouse scores, preparing a site for launch, or when the user asks about SEO, indexing, link previews or sharing cards."
domain: web
---

# Web performance and SEO

Measure first (`performance-profiling-budgets`): Lighthouse (mobile, throttled), PageSpeed Insights (field data), WebPageTest, Chrome DevTools Performance/Network. Record before/after. Never invent scores.

## Targets (75th percentile of real users)
LCP <= 2.5 s, INP <= 200 ms, CLS <= 0.1. Page weight budget for a landing page: <= 500 KB above the fold, <= 1.5 MB total.

## LCP (largest content appears fast)
- Identify the LCP element (usually hero image or headline). Give it `fetchpriority="high"`, no `loading="lazy"`, correct size; preload it only if it is discovered late (CSS background images).
- Eliminate render-blocking: inline small critical CSS, `defer` scripts, no `@import` chains, no huge CSS frameworks for a simple page.
- Server: compression (Brotli/gzip), HTTP/2 or 3, CDN, low TTFB, `Cache-Control: public, max-age=31536000, immutable` for hashed assets; HTML revalidated.
- Images: AVIF/WebP with fallback, `srcset` + `sizes`, right dimensions (never ship 4000 px for a 400 px slot), `decoding="async"`.
```html
<img src="hero-800.webp" srcset="hero-480.webp 480w, hero-800.webp 800w, hero-1600.webp 1600w"
     sizes="(min-width: 900px) 50vw, 100vw" width="1600" height="1200" alt="..." fetchpriority="high">
```

## CLS (nothing jumps)
- `width`/`height` (or `aspect-ratio`) on every image/video/iframe/ad slot; reserve space for banners and embeds.
- Fonts: `font-display: swap` plus `size-adjust`/fallback metrics to reduce reflow; preload the single critical WOFF2 (`crossorigin`).
- Don't insert content above existing content after load.

## INP (taps respond)
- Break long tasks (> 50 ms): split work, `requestIdleCallback`/`setTimeout`/`scheduler.yield()` where available, move heavy work to a Web Worker.
- Keep handlers light; debounce input; avoid layout thrash (read then write DOM, batch with `requestAnimationFrame`).
- Third-party scripts (analytics, chat widgets, maps): load after interaction/idle, `async`, or drop them.

## JS and CSS hygiene
Remove unused libraries; tree-shake; use native features (`<dialog>`, `<details>`, CSS scroll snap, `loading=lazy`) instead of plugins. Check coverage in DevTools (Coverage tab).

## SEO checklist
- One `<h1>`, logical headings, descriptive `<title>` (<= 60 chars) and meta description (120-155 chars), unique per page.
- `<link rel="canonical">`; `robots` meta only to block (default is indexable); `robots.txt` pointing to `sitemap.xml`; HTTPS everywhere, redirect `http` and `www` variants to one canonical host.
- Open Graph + Twitter card (image 1200x630, absolute URLs) so shares in Telegram/WhatsApp/Slack render; verify with the platform's debugger or by sending the link.
- Structured data (JSON-LD) matching visible content only:
```html
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"SoftwareApplication","name":"App","applicationCategory":"CommunicationApplication",
 "operatingSystem":"Android","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"}}
</script>
```
  Common types: `Organization`, `WebSite`, `Article`, `Product`, `FAQPage` (only for real FAQs), `BreadcrumbList`.
- Multilingual: separate URLs per language (`/ru/`, `/kk/`, `/en/`), `<html lang>`, `hreflang` alternates including `x-default`, no auto-redirect based on IP only.
- Content: real text in HTML (not only in images or JS-rendered after load), meaningful `alt`, descriptive link text, internal links, a useful 404 page.
- Search Console: verify the domain, submit the sitemap, watch coverage and Core Web Vitals reports.

## Verify
```bash
npx lighthouse https://example.com --preset=desktop --only-categories=performance,seo,accessibility,best-practices --output=html --output-path=./lh.html
npx lighthouse https://example.com --form-factor=mobile --throttling-method=simulate --view
curl -sI https://example.com | grep -iE 'cache-control|content-encoding|strict-transport'
```
Check the Network panel for compressed responses, cache headers, and the LCP request timing; check the rendered page with JS disabled for crawlability.

## Pitfalls
- Lazy-loading the hero image (hurts LCP). Preloading everything (defeats priority).
- Carousels and autoplay video above the fold.
- A cookie/chat widget that shifts layout.
- Blocking crawlers by accident (`Disallow: /`, `noindex` left from staging).
