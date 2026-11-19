---
name: api-idempotency
description: "Make writes safe to retry (message send, payments, uploads, bot actions) with client-generated ids, unique constraints and Idempotency-Key. Use whenever a client may retry, the network is flaky, duplicates appear, or an endpoint creates records or triggers side effects."
domain: backend
---

# Idempotency

- Client generates `clientMsgId` (UUID v4/v7) before the first attempt and reuses it on every retry.
- The database, not application code, enforces it:
```sql
create unique index messages_dedupe on messages (sender_id, client_msg_id);
insert into messages (...) values (...)
on conflict (sender_id, client_msg_id) do nothing
returning *;
-- no row returned => select the existing row and return it with 200 (same result as the first call)
```
- HTTP APIs for non-natural-key operations: `Idempotency-Key` header, store `(key, request hash, response)` with TTL; same key + different body = 422.
- Side effects (push, email) must be triggered from the "inserted" branch only, or be idempotent themselves.
- Test: send the same request 5x concurrently, expect exactly one row and one notification.

## Verify
Concurrency test: fire the same request 5-20x in parallel (`Promise.all`) and assert exactly one row, one side effect, identical responses; repeat after a server restart; repeat with a different body and the same key (expect 422).

## Pitfalls
- Checking "exists?" in code before insert (race): rely on the unique index.
- Idempotency key stored without TTL/cleanup, or without binding to the user (cross-user replay).
- Returning 409 on a duplicate instead of the original result: clients cannot tell success from failure.

## Related
`backend-api-design-validation`, `realtime-reconnect-client`, `flutter-offline-first`, `database-migrations`.
