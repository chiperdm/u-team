# /deploy-prep
Prepare (not perform) a deployment to Render or a VPS with Docker/nginx.

**Agents:** release-engineer
**Skills:** `devops-render-deploy`, `devops-docker-nginx`, `release-checklist-rollback`, `security-secrets-logging`

## Steps
1. Inspect app start command, port binding, health endpoints, env vars, storage (ephemeral?), migrations.
2. Write render.yaml or Dockerfile/compose/nginx configs.
3. Dry-run locally; list secrets to set (names only); write rollback steps.

## Output
Config files, env var list, verification commands, rollback plan.

## Guardrail
Do not deploy or change production without explicit approval.
