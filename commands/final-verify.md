# /final-verify
Independently verify the result against the original request.

**Agents:** final-verifier
**Skills:** `release-checklist-rollback`

## Steps
1. List acceptance criteria and claimed evidence.
2. Inspect final diff and scope creep.
3. Re-run key checks; inspect screenshots/build evidence.
4. Flag unsupported claims.

## Output
Verdict per criterion (verified / unverified / failed), residual risks.

## Guardrail
Do not modify files.
