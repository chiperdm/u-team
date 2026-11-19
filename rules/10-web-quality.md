# Web Quality Standard
- Semantic HTML, one `h1`, landmarks, `lang` attribute, visible focus, skip link.
- Responsive from 320 px to 1920 px with no horizontal scroll; `rem`/`clamp`, container queries where helpful.
- Dark mode and `prefers-reduced-motion` supported; glass has `@supports` and reduced-transparency fallbacks.
- Performance: images sized (width/height, AVIF/WebP), hero image prioritized, scripts deferred, no needless libraries; Core Web Vitals targets in `web-performance-seo`.
- Security: no `innerHTML` with user data, no secrets in HTML/JS, external scripts pinned (SRI) or avoided, `rel="noopener"` on external links.
- Content: real copy; no fabricated testimonials, statistics, logos or reviews; placeholders listed in the final report.
- Storage and browser APIs are feature-detected and wrapped in try/catch; the page works with them blocked.
