# /security-audit
Threat-focused read-only security audit.

**Agents:** security-auditor, crypto-reviewer, privacy-engineer
**Skills:** `security-threat-modeling`, `security-injection-xss`, `security-secrets-logging`, `e2ee-messaging-review`

## Steps
1. Scope assets, actors, trust boundaries.
2. Inspect auth, authorization (every object), validation, secrets, storage, crypto, DB rules/RLS, deep links, logs, dependencies.
3. Collect evidence with safe local tests.

## Output
Table: Finding | Severity | Evidence | Impact | Remediation | Test + "not checked" list.

## Guardrail
Never exploit external systems or change production.
