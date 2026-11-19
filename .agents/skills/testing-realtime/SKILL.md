---
name: testing-realtime
description: "Test WebSocket and realtime features: auth, authorization, ordering, duplicates, reconnect resume, slow consumers, heartbeat, shutdown and load. Use when writing tests for sockets, chat delivery, presence or sync logic."
domain: quality
---

# Realtime testing

Spin up the server in-process on a random port and drive it with 2+ real WebSocket clients.

Must-have cases:
1. Handshake without/with bad/expired token -> closed with 4401, no data leaked.
2. User A cannot subscribe to or send in a chat they are not a member of.
3. Same `clientMsgId` sent twice -> one stored message, one broadcast, both acks.
4. Message ordering per chat (seq monotonic); out-of-order and duplicate events handled by the client.
5. Disconnect mid-stream, reconnect, resync from `lastSeq`: no gaps, no duplicates.
6. Oversized payload, malformed JSON, unknown type -> rejected, connection policy respected.
7. Slow consumer: server does not grow memory unbounded.
8. Heartbeat: dead peer is terminated (use fake timers).
9. Graceful shutdown closes with 1001 and clients reconnect.
Load: ramp connections and messages/sec, watch event-loop lag, memory, p95 delivery latency; compare to a stated budget.

## Test harness sketch (Node, `node:test` + `ws`)
```js
import test from 'node:test'; import assert from 'node:assert/strict'; import WebSocket from 'ws';
const open = (url, headers) => new Promise((res, rej) => { const ws = new WebSocket(url, { headers }); ws.once('open', () => res(ws)); ws.once('error', rej); });
const next = (ws) => new Promise((res) => ws.once('message', (d) => res(JSON.parse(d))));
test('non-member cannot subscribe', async () => {
  const ws = await open(`ws://127.0.0.1:${port}`, { authorization: `Bearer ${tokenOfStranger}` });
  ws.send(JSON.stringify({ v: 1, type: 'subscribe', id: '1', payload: { chatId: 'c1' } }));
  const reply = await next(ws);
  assert.equal(reply.type, 'error'); assert.equal(reply.payload.code, 'FORBIDDEN');
});
```
Use fake timers for heartbeat tests and a seeded random for load patterns.

## Verify
Run the suite 3 times (no flakes); a deliberately broken server (skip the membership check, skip dedupe) makes the matching tests fail; CI runs it with a time limit.

## Related
`backend-node-websocket`, `realtime-reconnect-client`, `flutter-testing`, `supabase-realtime-storage`.
