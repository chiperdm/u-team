# /release-check
Release-readiness review without publishing.

**Agents:** release-engineer, final-verifier
**Skills:** `release-checklist-rollback`, `devops-android-release`, `devops-docker-nginx`, `devops-render-deploy`

## Steps
1. Check version/build config, signing (without exposing keys), permissions, API compatibility, migrations, tests, artifact integrity, privacy/security.
2. Verify rollback steps and rollout plan.

## Output
GO / NO-GO with blockers, evidence, residual risks.

## Guardrail
Do not publish, deploy or touch production.
