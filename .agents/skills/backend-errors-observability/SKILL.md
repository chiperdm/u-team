---
name: backend-errors-observability
description: "Set up consistent error handling, structured logging, RED metrics, health/readiness checks and graceful shutdown in a Node service. Use when adding a service, debugging production incidents with no logs, handling unhandled rejections, or preparing for deploys with zero dropped requests."
domain: backend
---

# Errors and observability

- Typed errors (`AppError{code,status,expose}`); one central error handler. Unexpected errors -> 500 with generic body + request id; details only in logs.
- `process.on('unhandledRejection')` and `uncaughtException`: log, then exit (let the supervisor restart); don't continue in unknown state.
- Structured JSON logs (pino) with `reqId`, `userId` (id only), route, latency; redact secrets (see security-secrets-logging).
- Metrics (RED): Rate, Errors, Duration per route + WebSocket connections, messages/sec, reconnects, queue depth.
- `/healthz` (process alive) and `/readyz` (DB/Redis reachable) kept separate.
- Graceful shutdown: on SIGTERM stop listening, finish in-flight requests with a deadline, close DB pool, then exit.
- Alert on symptoms (error rate, p95 latency, auth failures spike), not on every log line.

## Snippet: central handler and shutdown
```js
class AppError extends Error { constructor(status, code, extra = {}) { super(code); Object.assign(this, { status, code, expose: status < 500, extra }); } }
app.use((err, req, res, _next) => {
  const e = err instanceof AppError ? err : new AppError(500, 'INTERNAL');
  req.log.error({ err, code: e.code }, 'request failed');
  res.status(e.status).type('application/problem+json').json({ status: e.status, code: e.code, requestId: req.id, ...(e.expose ? e.extra : {}) });
});
const shutdown = async (sig) => { server.close(); wss.clients.forEach(c => c.close(1001)); await db.end(); process.exit(0); };
['SIGTERM', 'SIGINT'].forEach(s => process.on(s, () => shutdown(s)));
setTimeout(() => process.exit(1), 10_000).unref();   // hard deadline (register inside shutdown)
```

## Verify
Throw in a handler -> 500 generic body + logged stack with the same `requestId`; kill -TERM during a request -> request completes; `/readyz` fails when the DB is down while `/healthz` stays 200.

## Pitfalls
- Logging whole request bodies or headers (secrets, PII).
- Swallowing errors in `catch {}`.
- Health check that hits the database on every probe at high frequency.

## Related
`backend-api-design-validation`, `security-secrets-logging`, `devops-docker-nginx`, `devops-render-deploy`.
