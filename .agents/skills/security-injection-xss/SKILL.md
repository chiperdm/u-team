---
name: security-injection-xss
description: "Review input handling for SQL injection, XSS, command injection, SSRF, unsafe deep links and link rendering, especially in chat, bots and single-file HTML apps. Use for any code that renders user text, builds queries or commands, fetches user-supplied URLs, or handles deep links/intents."
domain: security
---

# Injection and XSS

- **SQL:** parameterized queries only (`$1`), including `LIKE` patterns (escape `%`/`_` if needed) and `ORDER BY` (allowlist column names, never interpolate).
- **Validate at the boundary** with a schema (zod/ajv): types, lengths, enums; reject, don't "clean".
- **Output encoding:** treat message text as plain text. In web UIs never `innerHTML` user content; if rich text is required use a vetted sanitizer with a tight allowlist. Add a CSP.
- **Links in chat:** show the real destination, allow only `http/https`, no `javascript:`/`data:`; consider warning on lookalike domains.
- **Deep links / intents:** validate every parameter; never perform state-changing actions from a link without user confirmation.
- **Command execution:** avoid shell; use `execFile` with arg arrays, never string concatenation of user input.
- **SSRF** (link previews, webhooks, avatar fetch): resolve DNS, block private/link-local/loopback ranges (127.0.0.0/8, 10/8, 172.16/12, 192.168/16, 169.254/16, ::1), limit redirects, size and time.
- Review method: list every place external input enters, follow it to every sink (DB, HTML, shell, URL fetch, file path), and test with hostile samples.

## Client-side rules (HTML apps)
`textContent` not `innerHTML`; sanitize with DOMPurify when HTML is required; set a CSP (`default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'`); `rel="noopener noreferrer"` on external links; validate `href` protocol; avoid `eval`/`new Function`; never put tokens in URLs.

## Verify
Hostile samples: `<img src=x onerror=alert(1)>`, `' OR 1=1 --`, `../../etc/passwd`, `javascript:alert(1)`, `http://169.254.169.254/`, very long strings, RTL override characters; confirm each is rejected or rendered inert.

## Related
`backend-api-design-validation`, `html-single-file-app`, `telegram-bot-development`, `llm-integration-safety` (model output is untrusted).
