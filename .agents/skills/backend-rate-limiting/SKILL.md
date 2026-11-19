---
name: backend-rate-limiting
description: "Add or review rate limiting for HTTP and WebSocket endpoints (login, OTP, messages, uploads, LLM calls): token bucket vs sliding window, key choice, Redis storage, proxy IP handling, 429 responses. Use when abuse, scraping, brute force or cost spikes are a concern, or before exposing any public endpoint."
domain: backend
---

# Rate limiting

- Choose by need: **token bucket** (bursts allowed), **sliding window** (strict), fixed window only for coarse limits.
- **Keys:** per IP for anonymous routes; per user id after auth; per email for OTP/login; combine (ip+route). One key type is easy to evade.
- **Storage:** in-memory only for a single instance; use Redis (atomic INCR+EXPIRE or Lua) when scaled out.
- **Behind a proxy/CDN** configure `trust proxy` correctly (Express) or every request appears to come from the proxy IP and one client blocks everyone; but never trust `X-Forwarded-For` from the open internet.
- Respond `429` with `Retry-After`; do not reveal which limit key matched.
- Stricter on expensive/abusable routes: login, OTP send/verify, password reset, search, file upload, invite/contact lookup.
- WebSocket: limit messages/sec per connection and per user; close with a policy code on abuse.
- Exempt health checks; log limit hits as metrics (not with secrets).
- Test: N+1 requests produce 429, window resets, different users do not affect each other, proxy header spoofing does not bypass.

## Snippet (express-rate-limit style, per user then IP)
```js
const keyBy = (req) => req.user?.id ?? req.ip;
app.use('/v1/auth', rateLimit({ windowMs: 15 * 60_000, limit: 10, standardHeaders: 'draft-7', legacyHeaders: false, keyGenerator: keyBy }));
app.set('trust proxy', 1);   // number of proxy hops you actually have
```
Use a shared store (Redis) when more than one instance runs.

## Pitfalls
- Counting only per IP: mobile carrier NAT blocks innocent users, attackers rotate IPs.
- In-memory limits on multi-instance deployments (each instance has its own counter).
- Trusting `X-Forwarded-For` without `trust proxy` configured to the real hop count.

## Verify
Integration test: N+1 requests in the window -> 429 with `Retry-After`; window reset allows requests again; two users do not affect each other; spoofed `X-Forwarded-For` from outside does not bypass; health check exempt; limits survive a restart when Redis-backed.

## Related
`backend-authentication`, `backend-node-otp-email`, `llm-integration-safety`, `devops-docker-nginx` (proxy-level `limit_req`).
