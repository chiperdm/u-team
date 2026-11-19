---
name: backend-node-websocket
description: "Build or review a Node `ws` WebSocket server for chat or realtime features: handshake auth, Origin checks, heartbeat, payload limits, backpressure, per-message authorization, ack/dedupe, multi-instance fan-out, graceful shutdown. Use for any socket server code, dropped connections, memory growth, or duplicate/missing realtime messages."
domain: realtime
---

# Node WebSocket server

## Checklist
1. **Auth at handshake.** Native clients: `Authorization` header on upgrade. Browsers cannot set headers: authenticate with a first message `{type:'auth', token}` within 5 s or close with 4401. Avoid tokens in the query string (they land in logs/proxies).
2. **Check `Origin`** for browser clients against an allowlist (see security-cors).
3. **Limits:** `maxPayload` (e.g. 64 KB), per-connection message rate limit, max connections per user, max subscriptions per connection.
4. **Heartbeat:** ping every 30 s, terminate sockets that did not pong.
5. **Envelope:** every message `{v, type, id, ts, payload}`; reject unknown `type` / `v`; validate payload with a schema (zod/ajv).
6. **Authorize every message**, not only on connect: "is this user a member of `chatId`?" must be re-checked server side.
7. **Ack + dedupe:** server acks `id`; client resends until ack; server dedupes by `(sender, clientMsgId)` (see api-idempotency).
8. **Backpressure:** before sending, if `ws.bufferedAmount` is above a threshold (e.g. 1 MB) drop/close slow consumers instead of growing memory.
9. **Multi-instance:** keep rooms in memory per instance and fan out between instances via Redis pub/sub (or similar). Sticky sessions alone do not solve cross-instance delivery.
10. **Shutdown:** on SIGTERM stop accepting upgrades, send close code 1001, wait briefly, then exit.

## Skeleton
```js
import { WebSocketServer } from 'ws';
const wss = new WebSocketServer({ noServer: true, maxPayload: 64 * 1024 });

server.on('upgrade', (req, socket, head) => {
  const origin = req.headers.origin;
  if (origin && !allowedOrigins.has(origin)) { socket.destroy(); return; }
  wss.handleUpgrade(req, socket, head, ws => wss.emit('connection', ws, req));
});

wss.on('connection', ws => {
  ws.isAlive = true;
  ws.on('pong', () => { ws.isAlive = true; });
  const authTimer = setTimeout(() => ws.close(4401, 'auth timeout'), 5000);
  ws.on('message', raw => { /* parse -> validate -> authorize -> handle */ });
  ws.on('close', () => clearTimeout(authTimer));
});

setInterval(() => wss.clients.forEach(ws => {
  if (!ws.isAlive) return ws.terminate();
  ws.isAlive = false; ws.ping();
}), 30_000);
```

## Pitfalls
- Unhandled `error` event on a socket crashes the process: always attach `ws.on('error', ...)`.
- JSON.parse of untrusted data needs try/catch and a size limit.
- Never trust `userId` sent by the client; take it from the verified token.

## Verify
Use `testing-realtime` (auth, membership, dedupe, resync, slow consumer, shutdown). Load-test with k6/artillery/autocannon-ws: watch event-loop lag, RSS, `bufferedAmount`, p95 delivery latency against a stated budget.

## Behind a proxy
Proxy must forward `Upgrade`/`Connection` headers and use a read timeout above your ping interval (`devops-docker-nginx`); on Render-like platforms expect restarts on deploy and sleeps on free plans (`devops-render-deploy`).

## Related
`realtime-reconnect-client`, `api-idempotency`, `security-cors`, `backend-rate-limiting`, `supabase-realtime-storage`.
