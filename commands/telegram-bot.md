# /telegram-bot
Build or fix a Telegram bot with persistent state and safe deployment.

**Agents:** backend-engineer
**Skills:** `telegram-bot-development`, `security-secrets-logging`, `devops-render-deploy`

## Steps
1. Pick library/mode (polling vs webhook); define flows and storage.
2. Persist step state in the DB; make handlers idempotent.
3. Add admin controls by user id; rate limits; error handling.
4. Test restart mid-flow, blocked user, 429.

## Output
Bot code, env var list (names only), run/deploy instructions.

## Guardrail
Token only in env; one running instance per token.
