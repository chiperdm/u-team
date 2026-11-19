---
name: security-secrets-logging
description: "Keep secrets out of repos, prompts, APKs, HTML files and logs: env/secret managers, scanning, redaction, key rotation and incident response for leaked keys. Use when handling API keys, tokens, keystores, .env files, before committing, when a secret may have leaked, or when setting up logging."
domain: security
---

# Secrets and logging

- Secrets live in env/secret manager. Commit `.env.example` with names only; `.env` in `.gitignore`.
- **A leaked secret is compromised forever:** rotate it first, then clean history. Deleting the commit is not enough.
- Scan staged changes before commit (see `hooks/pre-commit-secret-scan.sh`) and in CI with a dedicated tool (gitleaks or trufflehog); the bundled hook is a safety net, not a scanner.
- Do not paste real keys/tokens/user data into AI prompts, issues or screenshots.
- **Logging:** structured JSON, request id, no bodies by default. Redact: `authorization`, `cookie`, `token`, `password`, `otp`, `code`, `refresh`, `apikey`, message text, emails/phones (mask). In pino: `redact: ['req.headers.authorization','req.headers.cookie','*.password','*.token','*.otp']`.
- Never log decrypted E2EE content or private keys, even at debug level.
- Client errors: generic message + error code; stack traces stay in server logs.
- Separate keys per environment; least privilege (e.g. DB role without DDL for the app).

## Leak response (do in this order)
1. Revoke/rotate the secret at the provider (BotFather `/revoke`, provider dashboard, Supabase JWT/keys, GitHub token).
2. Check provider logs/usage for abuse; invalidate sessions if relevant.
3. Remove from the repo and history (`git filter-repo`/BFG) only after rotation; force-push needs approval.
4. Add a scanner to CI (`gitleaks`/`trufflehog`) and the pre-commit hook; document the incident briefly.

## Client-side reality
Anything inside an APK, Flutter bundle, or HTML file is public: use only public/anon identifiers there, and call your backend for privileged operations (`llm-integration-safety`, `database-rls-supabase`).

## Verify
`hooks/pre-commit-secret-scan.sh --all .` clean; `git log -p | grep` spot checks for key prefixes; logs from a test run contain no tokens/OTP/message text.

## Related
`dependency-supply-chain`, `devops-ci-flutter-node`, `termux-android-dev`, `firebase-rules-auth`.
