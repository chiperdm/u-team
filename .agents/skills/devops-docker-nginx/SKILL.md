---
name: devops-docker-nginx
description: "Containerize and deploy a Node backend on a VPS: multi-stage non-root Dockerfile, .dockerignore, docker compose with Postgres/Redis, health checks, nginx reverse proxy with WebSocket upgrade, TLS via Let's Encrypt, security headers, rate limiting at the proxy, backups with restore test, zero-downtime reload. Use when deploying to a VPS/server, writing Dockerfiles or compose files, configuring nginx or HTTPS, or debugging 502/WebSocket drops behind a proxy."
domain: devops
---

# Docker and nginx on a VPS

Production changes need explicit human approval (`rules/08-release-and-deploy.md`). Prefer a managed platform when the team is tiny (`devops-render-deploy`); use this when you need a VPS.

## Dockerfile (Node, multi-stage, non-root)
```dockerfile
# Use the current Node LTS tag (check nodejs.org/releases); pin a digest for strict reproducibility.
FROM node:lts-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

FROM node:lts-alpine
ENV NODE_ENV=production
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --chown=node:node . .
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s CMD node -e "fetch('http://127.0.0.1:3000/healthz').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["node", "src/index.js"]
```
`.dockerignore`: `node_modules`, `.git`, `.env*`, `*.log`, `coverage`, `Dockerfile*`, test files. No secrets in the image or build args; pass via env/secrets at runtime. Run as non-root; read-only root fs where possible (`read_only: true` + tmpfs).

## docker compose
```yaml
services:
  api:
    build: .
    init: true                         # proper signal handling / zombie reaping
    restart: unless-stopped
    env_file: .env                     # not committed
    environment: { NODE_ENV: production, PORT: "3000" }
    depends_on: { db: { condition: service_healthy } }
    ports: ["127.0.0.1:3000:3000"]     # only localhost; nginx is the public entry
    deploy: { resources: { limits: { memory: 512m } } }
    logging: { driver: json-file, options: { max-size: "10m", max-file: "5" } }
  db:
    image: postgres:16-alpine          # pin the major you tested; upgrade deliberately
    restart: unless-stopped
    environment: { POSTGRES_PASSWORD_FILE: /run/secrets/db_pw }
    secrets: [db_pw]
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck: { test: ["CMD-SHELL", "pg_isready -U postgres"], interval: 10s, retries: 5 }
volumes: { pgdata: {} }
secrets: { db_pw: { file: ./secrets/db_pw.txt } }
```
Never publish the DB port to the internet. Named volumes for data; back them up.

## nginx reverse proxy (HTTP + WebSocket + TLS)
```nginx
map $http_upgrade $connection_upgrade { default upgrade; '' close; }
limit_req_zone $binary_remote_addr zone=api:10m rate=20r/s;

server { listen 80; server_name api.example.com; return 301 https://$host$request_uri; }

server {
  listen 443 ssl;                       # nginx >= 1.25.1: also `http2 on;`
  server_name api.example.com;
  ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
  add_header X-Content-Type-Options nosniff always;
  add_header Referrer-Policy strict-origin-when-cross-origin always;
  client_max_body_size 10m;             # match app limits

  location / {
    limit_req zone=api burst=40 nodelay;
    proxy_pass http://127.0.0.1:3000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;          # WebSocket
    proxy_set_header Connection $connection_upgrade;
    proxy_read_timeout 3600s;                        # must exceed the WS heartbeat interval
    proxy_send_timeout 3600s;
  }
}
```
Set Express `trust proxy` to the proxy hop count (`backend-rate-limiting`). Test config: `sudo nginx -t`, then `sudo systemctl reload nginx` (no downtime).

## TLS
`sudo certbot --nginx -d api.example.com` (or `certbot certonly --webroot`), verify auto-renew: `sudo certbot renew --dry-run`; alert before expiry (30 days). HSTS only after HTTPS works everywhere.

## Server hygiene
Create a non-root sudo user; SSH keys only (`PasswordAuthentication no`, `PermitRootLogin no`); `ufw allow OpenSSH 80 443` then `ufw enable`; `unattended-upgrades` for security patches; fail2ban for SSH; time sync; monitor disk (logs, Docker images: `docker system df`, prune with care).

## Deploy flow (small team)
```bash
git pull --ff-only && docker compose build api && docker compose up -d api   # replaces the container
docker compose ps && curl -fsS https://api.example.com/readyz
```
Keep the previous image tag for rollback (`docker tag app:latest app:prev`); migrations via expand/contract (`database-migrations`) run before the new code; smoke test; rollback = `docker compose up -d` with the previous tag.

## Backups (a backup you have not restored is not a backup)
```bash
docker compose exec -T db pg_dump -U postgres -Fc app > /backups/app-$(date +%F).dump
# cron daily, keep 7 daily + 4 weekly, copy off-server (object storage), encrypt
docker compose exec -T db pg_restore -U postgres -d app_restore --clean --if-exists < /backups/app-2026-01-01.dump   # TEST on a scratch DB monthly
```

## Debug 502 / WebSocket drops
`docker compose logs --tail=100 api`; `curl -i http://127.0.0.1:3000/healthz` from the host (app up?); `sudo tail -f /var/log/nginx/error.log` (upstream refused/timeout); WS closes after 60 s -> missing `Upgrade` headers or low `proxy_read_timeout`; wrong client IPs -> `trust proxy`; 413 -> `client_max_body_size`.

## Verify
`docker build` succeeds, container runs as non-root (`docker compose exec api id`), `nginx -t` passes, `curl -I` shows HSTS and redirect, WebSocket handshake works (`websocat wss://...`), SSL Labs/`testssl.sh` grade, backup restore tested.

## Pitfalls
- `latest` tags for databases; `docker compose down -v` deletes volumes.
- Secrets in `docker-compose.yml` committed to git.
- Running the app as root; exposing 3000/5432 publicly.
- Forgetting Docker bypasses `ufw` for published ports: bind to `127.0.0.1`.
