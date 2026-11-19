---
name: e2ee-messaging-review
description: "Review end-to-end encryption design and implementation in a messenger: threat model, protocol choice (Signal/PQXDH + Double Ratchet, MLS for groups), identity key verification, metadata, multi-device, encrypted backups, media encryption, notifications, local storage, red-flag crypto patterns, and a findings report. Use when someone proposes or implements E2EE, secret chats, key exchange, or asks whether messages are really private. Read-only: never invent cryptography."
domain: security
---

# E2EE messaging review (read-only)

Owner: `crypto-reviewer`. Output goes through `templates/review-report.md`. This is a design/code review aid, **not a substitute for an independent cryptographic audit** before claiming "end-to-end encrypted" to users.

## Golden rules
1. **Do not design or implement your own protocol or primitives.** Use a vetted protocol and a maintained library; review integration, not the math.
2. Be precise in claims: "encrypted in transit" (TLS) ≠ "encrypted at rest on server" ≠ **E2EE** (server cannot read content). Marketing text must match what is built.
3. Plaintext must not touch the server, logs, push providers, link-preview services, analytics or crash reports.

## Protocol reference points
- **1:1:** Signal protocol family: X3DH, upgraded to PQXDH (post-quantum hybrid) in Signal, + Double Ratchet (forward secrecy + post-compromise security). Multi-device handled by per-device sessions (Sesame-style).
- **Groups:** Sender Keys (simple, weaker PCS) or **MLS (RFC 9420)** (scalable, tree-based, membership change security). Many-member groups with per-recipient 1:1 fan-out do not scale.
- **Transport:** TLS 1.2+/1.3 always; Noise-based channels optional. TLS protects the pipe, not the content.
- **Libraries:** libsignal (check its licence: AGPL implications for closed-source distribution), OpenMLS, libsodium/NaCl bindings for primitives. Verify maintenance, audits, platform bindings (Android/Flutter/Node) with `dependency-supply-chain`.

## Primitive checklist
Good: X25519/Ed25519, AES-256-GCM or ChaCha20-Poly1305 (AEAD), HKDF-SHA-256, Argon2id for passphrases, CSPRNG (`SecureRandom`, `crypto.randomBytes`, `Random.secure()`).
Red flags: custom protocols, ECB, CBC/CTR without MAC, static or repeated IV/nonce with the same key (GCM catastrophic), RSA PKCS#1 v1.5 encryption, MD5/SHA-1, ad-hoc KDF (`sha256(password)`), `Math.random()`/`Random()` for keys, hardcoded keys, keys derived from user id/phone, same key for both directions, unauthenticated ciphertext, signature checks skipped, key comparison with `==` (use constant time), reusing one symmetric key for all chats.

## Key management and trust
- Private keys generated on device, stored in Keystore/Keychain-wrapped storage (`kotlin-android-keystore`), never sent to the server; prekey bundles (signed prekey + one-time prekeys) published, replenished, rotated.
- **Identity verification:** safety number / QR comparison; **key-change warnings** (do not silently accept a changed identity key); optional key transparency for server-compromise resistance. TOFU without warnings = server can MITM.
- Server integrity: can a malicious server add a device/member silently? Is the member list authenticated (signed)? Are new devices announced to the user?
- Account recovery/PIN: recovery must not give the server the keys; rate limit guesses (hardware-backed or SVR-like designs are complex: flag, don't invent).

## Data flows to inspect
| Surface | Questions |
|---|---|
| Message send/receive | encrypted per recipient device/group epoch; message ids/timestamps visible to server? padding of lengths? replay protection, ordering, deduplication (`api-idempotency`) |
| Media/files | random 256-bit key per file, AEAD or encrypt-then-MAC, chunked streaming (e.g. secretstream), key + hash inside the encrypted message, server stores ciphertext only (`security-file-upload`); thumbnails and filenames also encrypted |
| Push notifications | FCM/APNs payload must not contain plaintext: send a wake-up/ID, fetch and decrypt locally, build the notification on device |
| Link previews | generated client-side or via a privacy proxy; server-side fetching leaks content/IP |
| Search | on-device index only (encrypted at rest) |
| Backups | cloud/auto-backup of the plaintext DB defeats E2EE; encrypted backup needs a user-held key; set `allowBackup`/`dataExtractionRules` deliberately |
| Local storage | DB encrypted (SQLCipher or Keystore-wrapped key), screenshots blocked on secret chats (`FLAG_SECURE`), lock screen previews hidden |
| Disappearing messages | enforced locally and acknowledged; do not claim guarantees against screenshots |
| Calls | SRTP with E2E key exchange (DTLS-SRTP + signaling authentication); TURN servers see only ciphertext |
| Logs/analytics/crash | no plaintext, keys, tokens (`security-secrets-logging`) |
| Metadata | who talks to whom, when, IP, device, group membership, contact discovery: enumerate and minimize; sealed-sender style techniques are advanced: flag as roadmap |

## Process
1. Write the claim ("what can the server see?") and the adversaries (network, curious server operator, compromised server, stolen phone, malicious contact, malicious group admin).
2. Map the actual flows from code (follow plaintext from compose box to socket and back).
3. Check each row of the table and the primitive list; run the secret-scan hook; grep for crypto APIs: `grep -RniE "AES/|Cipher\.getInstance|createCipher|createHmac|MessageDigest|Random\(|Math\.random|SecureRandom|encrypt\(|decrypt\(" .`
4. Verify with tests/evidence where possible: tampered ciphertext rejected, wrong key fails, replayed message rejected, key change triggers warning, no plaintext in server logs/DB (inspect actual rows).
5. Report.

## Report format
| ID | Finding | Evidence (file:line / test) | Severity | Impact | Recommendation | Verified? |
Severity: Critical (server/attacker can read or forge messages), High (key mishandling, no auth), Medium (metadata leaks, weak recovery), Low. Add "Out of scope / not analysed" and "Claims the product may/must not make".

## Pitfalls
- "We use AES-256" as the whole answer.
- Treating the Firebase/Supabase TLS as E2EE.
- Adding E2EE to groups without handling member removal (new keys) and multi-device.
- Forgetting that backups, notifications, previews and logs are separate leak paths.

## Verify (the review itself)
Every claim in the report cites code or a test; at least one tamper/replay/key-change test was actually run or is marked "not run"; plaintext search of server DB/logs was performed on real data from a test account.
