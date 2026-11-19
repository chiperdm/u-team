---
name: security-cors
description: "Configure or review CORS for Node APIs and WebSocket origins: exact allowlists, credentials, preflight, Vary, max-age. Use when a browser client gets CORS errors, when adding a web client or admin panel, or when auditing Access-Control-* headers."
domain: security
---

# CORS

CORS is a browser-only mechanism. Native apps, curl and servers ignore it, so it is NOT authentication.

## Rules
- Allowlist exact origins from env (`CORS_ORIGINS=https://app.example.com,https://admin.example.com`). Never reflect the `Origin` header blindly.
- Never combine `Access-Control-Allow-Origin: *` with credentials (browsers reject it; "fixing" it by reflecting Origin makes it exploitable).
- Answer preflight (`OPTIONS`) BEFORE auth middleware, otherwise preflights fail with 401.
- When the allowed origin is dynamic, send `Vary: Origin`.
- Set `Access-Control-Max-Age` (e.g. 600) to cut preflight traffic; list only the methods/headers you really use.
- WebSocket upgrades are not covered by CORS: check `req.headers.origin` yourself for browser clients, and authenticate the handshake.

## Express
```js
import cors from 'cors';
const allowed = new Set((process.env.CORS_ORIGINS ?? '').split(',').filter(Boolean));
app.use(cors({
  origin: (origin, cb) => (!origin || allowed.has(origin)) ? cb(null, true) : cb(null, false),
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 600,
}));
```
(`!origin` allows non-browser clients; that is fine because auth, not CORS, protects the API.)

## Verify
```bash
curl -si -X OPTIONS https://api.example.com/v1/me \
  -H 'Origin: https://evil.example' -H 'Access-Control-Request-Method: GET' | grep -i access-control
# expect: no Access-Control-Allow-Origin header
```
Repeat with an allowed origin and expect it echoed back plus `Vary: Origin`.

## Pitfalls
- Reflecting any `Origin` with `credentials: true` (full cross-site access).
- Allowing `null` origin (sandboxed iframes, local files) in production.
- Treating CORS as protection for non-browser clients: it is not (`backend-authentication`).
- Forgetting that single-file HTML apps opened from `file://` send `Origin: null`: use a dev-only allowance, never in prod.

## Related
`backend-node-websocket` (Origin check), `devops-docker-nginx`, `devops-render-deploy`, `html-single-file-app`.
