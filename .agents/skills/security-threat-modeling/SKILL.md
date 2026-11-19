---
name: security-threat-modeling
description: "Run a quick STRIDE-style threat model for a feature or system (chat, login, file sharing, assistant with phone control, LLM tools) and output prioritized risks with mitigations and tests. Use before building sensitive features, during design review, or when asked 'is this secure?'."
domain: security
---

# Quick threat model

Steps: 1) assets (messages, tokens, contacts, keys), 2) actors (user, other user, anonymous, admin, compromised device, malicious server operator), 3) trust boundaries (app-network-API-DB-3rd parties), 4) walk STRIDE per boundary, 5) rank by impact x likelihood, 6) map each to a mitigation and a test.

| STRIDE | Ask | Typical chat example |
|---|---|---|
| Spoofing | Can I act as someone else? | forged sender_id, stolen refresh token |
| Tampering | Can data be altered in transit/rest? | editing others' messages via API |
| Repudiation | Can actions be denied/untraceable? | no audit of admin actions |
| Info disclosure | What leaks? | IDOR on chat/media id, verbose errors |
| DoS | Can it be exhausted? | message floods, huge uploads |
| Elevation | Can I gain rights? | joining private chat by guessing id |

Output format: table `Threat | Boundary | Severity | Mitigation | Test | Owner`, then "not analysed" list. Read-only: do not exploit real systems.

## Worked mini-example (assistant that can send messages by voice)
Assets: contacts, message history, the ability to act as the user. Actors: user, nearby person/TV audio, malicious app, remote attacker via prompt injection in incoming messages. Threats: spoofed voice command (S), injected instruction in a received message triggers a send (T/E), transcript leaks to logs (I), command flood drains battery/cost (D). Mitigations: confirmation before send, tool allowlist, redaction, rate limits. Tests: injection sample does not cause an action, logs contain no transcript.

## Verify
Every high risk has an owner, mitigation and a test or monitoring item; the "not analysed" list is explicit.

## Related
`e2ee-messaging-review`, `llm-integration-safety`, `android-overlay-accessibility`, `database-rls-supabase`, `security-injection-xss`.
