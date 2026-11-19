---
name: devops-render-deploy
description: "Deploy and operate Node/Python web services, WebSocket servers, static sites and bots on Render: render.yaml blueprint, PORT binding, health checks, env vars and secrets, free-tier sleep/cold start behavior, ephemeral disk, databases, cron, logs, rollbacks and common deploy failures. Use when deploying to Render, fixing a failed or slow Render deploy, or choosing hosting for a small backend."
domain: devops
---

# Render deployment

Check current plan limits on Render's pricing/docs before promising behavior: limits change. Publishing/production changes need human approval (`rules/08-release-and-deploy.md`).

## Service types
Web Service (HTTP + WebSocket), Static Site (free CDN hosting for plain HTML/SPA), Background Worker (bots, queues), Cron Job, Postgres, Key Value (Redis-compatible). Pick the smallest that fits: a static landing page -> Static Site; a Telegram bot with polling -> Background Worker (a web service sleeps on free plans).

## render.yaml (Blueprint)
```yaml
services:
  - type: web
    name: chiper-api
    runtime: node
    region: frankfurt                 # choose near users/DB
    plan: free                        # starter or higher for always-on
    rootDir: server
    buildCommand: npm ci
    startCommand: node src/index.js
    healthCheckPath: /healthz
    autoDeploy: true
    envVars:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase: { name: chiper-db, property: connectionString }
      - key: JWT_SECRET
        generateValue: true
      - key: LLM_API_KEY
        sync: false                   # set manually in the dashboard, never in git
  - type: web
    name: chiper-site
    runtime: static
    buildCommand: ""                  # plain HTML
    staticPublishPath: ./site
databases:
  - name: chiper-db
    plan: free                        # free Postgres is time-limited; check current policy and back up
```
Validate the file before pushing (Render dashboard Blueprint preview shows errors).

## Must-do app settings
- Bind `0.0.0.0` and `process.env.PORT` (Render injects it; default 10000): `server.listen(process.env.PORT || 3000, '0.0.0.0')`. Binding `localhost` = deploy "no open ports detected" timeout.
- Health endpoint fast and dependency-light (`/healthz`), otherwise deploys fail or restart-loop.
- Filesystem is **ephemeral** (wiped on deploy/restart) unless a paid persistent disk is attached: no SQLite files, uploads or sessions on local disk; use Postgres/Supabase/S3-compatible storage. This is the #1 data-loss cause.
- Graceful shutdown on `SIGTERM` (`backend-errors-observability`): Render sends it on deploy; finish requests, close WebSockets with 1001.
- Trust proxy: `app.set('trust proxy', 1)` so client IPs and `req.protocol` are right (`backend-rate-limiting`).
- WebSockets work on web services; heartbeats (ping/pong every 25-30 s) avoid idle disconnects through the proxy; clients must reconnect (`realtime-reconnect-client`) because deploys and sleeps drop sockets.
- CORS origins from env (`security-cors`); never `*` with credentials.

## Free-tier behavior to design around
Free web services spin down after a period of inactivity and take a noticeable time to wake on the next request; instance hours are limited per month. Consequences: first request slow (show a "waking up" state in clients, retry with backoff), WebSocket connections drop on sleep, in-memory state lost, scheduled in-process timers do not run while asleep. Keeping it awake with external pings is fragile and may conflict with fair-use rules: move to a paid always-on instance for anything user-facing and serious.

## Environment variables and secrets
Dashboard env vars or `sync: false` entries; Environment Groups for shared values; never commit `.env`; rotate if leaked (`security-secrets-logging`); separate staging/production services.

## Build/deploy failures (diagnose in order)
1. Logs: Dashboard -> service -> Events/Logs (read the first error, not the last).
2. Node version mismatch: set `engines.node` in `package.json` or `NODE_VERSION` env var; use the same version locally.
3. `npm ci` fails: lockfile out of sync with `package.json` (`npm install` locally and commit the lock).
4. Case-sensitive filenames (Linux) vs Windows/macOS.
5. Missing build tools for native modules (prefer pure-JS or prebuilt binaries).
6. "Port scan timeout": wrong host/port binding or app crash on boot (missing env var).
7. Out of memory on free instance: reduce concurrency, avoid bundling heavy tools at runtime, build locally and deploy artifacts.
8. Root directory/monorepo paths wrong (`rootDir`, build filter).

## Operations
- Rollback: Dashboard -> Events -> Rollback to a previous deploy (code only; DB migrations are not reverted, so keep them backward compatible: `database-migrations`).
- Preview environments per PR if enabled; manual deploy for risky releases (`autoDeploy: false`).
- Alerts: uptime check on `/readyz` from an external monitor you control; log drains if needed; watch response times and 5xx.
- Cost control: right-size instance, delete unused services/databases, check bandwidth.
- Custom domain: add in dashboard, create the DNS record Render shows, wait for TLS issuance; redirect www/non-www.

## Verify
`curl -fsS https://<service>.onrender.com/healthz`; open the site; test WebSocket from a client (`websocat wss://...`); trigger a redeploy and confirm clients reconnect and no data is lost; confirm secrets are absent from the repo (`hooks/pre-commit-secret-scan.sh --all .`).

## Pitfalls
- SQLite or uploads on the local disk (lost on restart).
- Using `localhost` for the DB/Redis URL instead of the internal connection string.
- Long cold starts mistaken for outages; no client-side retry.
- Auto-deploying a broken main branch: require CI green first (`devops-ci-flutter-node`).
