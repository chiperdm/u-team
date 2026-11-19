---
name: backend-node-otp-email
description: "Implement or audit email OTP (one-time code) login: crypto-random codes, HMAC-hashed storage, expiry, attempt limits, resend cooldown, enumeration protection, atomic consume. Use for passwordless login, email verification, password reset codes or when OTP abuse and spam are reported."
domain: security
---

# Email OTP

## Rules
- Generate with `crypto.randomInt`, never `Math.random`.
- Store only an HMAC of the code (secret from env), not the plaintext. Bind it to the email: `HMAC(secret, email + ':' + code)`.
- TTL 5-10 min, single use (delete/mark used atomically on success), max 5 wrong attempts then invalidate, new code invalidates the previous one.
- Compare with `timingSafeEqual`.
- Rate limit by email AND IP AND per day; resend cooldown ~60 s.
- Same response whether the account exists or not (no user enumeration); keep timing similar.
- Never log the code or put it in URLs. Subject/body must not contain more than the code and a short warning.
- Provider outage must not leak to the client as "email not found"; queue and retry.

## Code
```js
import { randomInt, createHmac, timingSafeEqual } from 'node:crypto';
const gen = () => String(randomInt(0, 1_000_000)).padStart(6, '0');
const mac = (email, code) => createHmac('sha256', process.env.OTP_SECRET).update(`${email}:${code}`).digest();

async function verify(email, code) {
  const row = await db.otp.findActive(email);                 // not expired, not used
  if (!row || row.attempts >= 5) return false;
  const ok = timingSafeEqual(mac(email, code), row.hash);      // both 32 bytes
  if (!ok) { await db.otp.incAttempts(row.id); return false; }
  return db.otp.consume(row.id);                               // UPDATE ... WHERE used=false RETURNING (atomic)
}
```

## Tests to write
expired code, reused code, 6th attempt, concurrent verify of the same code (only one succeeds), unknown email gives same response, resend inside cooldown.

## Delivery
Use a transactional provider (SMTP/API) with SPF, DKIM and DMARC configured on the sending domain, a stable From address, and a plain, short template; queue sends with retries (idempotent per request id) so a provider outage never changes the API response. Monitor bounce and complaint rates.

## Verify
Run the "Tests to write" list above plus: the code never appears in logs (`grep` the log output of a test run), emails to unknown addresses return the same response and similar timing, per-IP and per-email limits trigger 429.

## Pitfalls
- 4-digit codes without strict attempt limits.
- Code in the email subject or in a URL query.
- Resend button that lets an attacker spam someone's inbox (cooldown + daily cap per email).

## Related
`backend-authentication`, `backend-rate-limiting`, `security-secrets-logging`, `api-idempotency`.
