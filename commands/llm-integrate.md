# /llm-integrate
Integrate an LLM API into an app, bot or backend safely.

**Agents:** llm-integration-engineer, security-auditor
**Skills:** `llm-integration-safety`, `backend-api-design-validation`, `backend-rate-limiting`

## Steps
1. Place the provider key server-side; design the proxy endpoint with auth, quotas, timeouts, fallback.
2. Implement streaming + cancellation; validate structured output.
3. Define tool allowlist and confirmation gates.
4. Create a golden-prompt eval set including injection and ru/kk/en.

## Output
Endpoint contract, limits, eval results, privacy notes.

## Guardrail
No keys in clients; no unvalidated model output to shell/SQL/Intents.
