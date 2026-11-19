---
name: backend-authentication
description: "Design or review authentication and sessions in Node backends: short-lived access JWT, rotating hashed refresh tokens, revocation, password hashing, WebSocket auth. Use for login, token refresh, session theft concerns, 'log out everywhere', JWT verification bugs or any auth code review."
domain: security
---

# Authentication

- **Access token:** short-lived (10-15 min) JWT. Verify signature with an explicit algorithm allowlist (`algorithms: ['RS256']` or `['HS256']`), plus `iss`, `aud`, `exp`. Never accept `alg: none` or algorithm taken from the token header.
- **Refresh token:** random 256-bit opaque value, stored HASHED server side, bound to a device/session row. **Rotate on every use**; if an already-used refresh token appears again, revoke the whole session family (token theft signal).
- **Storage on client:** mobile: platform secure storage (Keychain / Keystore-backed). Web: httpOnly + Secure + SameSite cookie for refresh; keep access token in memory.
- JWT carries only ids/roles needed; no PII, no secrets. Authorization decisions use fresh DB data for sensitive actions.
- Logout = delete session row; "log out everywhere" + automatic revoke on password/email change.
- Passwords (if any): argon2id (or bcrypt with a sane cost) with per-hash salt; never SHA-256 alone; enforce length, not silly composition rules; rate limit logins.
- Constant-time comparisons for secrets; generic errors ("invalid credentials").
- WebSocket: validate the token at handshake and re-validate/close when the session is revoked or expires.
- Tests: expired, wrong aud/iss, tampered payload, reused refresh token, revoked session.

## Verify
Tests: expired token, wrong `aud`/`iss`, `alg: none`, tampered payload, reused refresh token (whole family revoked), revoked session, password change invalidates sessions, WebSocket closes on revoke. Run a manual replay of a stolen refresh token against staging.

## Pitfalls
- Storing refresh tokens in plaintext in the DB (hash them).
- Long-lived access tokens "to avoid refresh bugs".
- Putting roles in a JWT and never re-checking on sensitive actions.
- Different error messages for unknown user vs wrong password (enumeration).

## Related
`backend-node-otp-email`, `backend-rate-limiting`, `security-secrets-logging`, `kotlin-android-keystore`, `firebase-rules-auth`.
