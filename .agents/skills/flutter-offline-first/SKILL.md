---
name: flutter-offline-first
description: "Add or review offline support in Flutter apps: local DB as source of truth, outbox queue, sync cursors, conflict rules, retries, local schema migrations. Use when messages vanish offline, lists blank without network, sync duplicates data, or when designing local storage for a chat or tracker app."
domain: flutter
---

# Offline-first

- Local DB is the UI's source; network syncs it. Use what the project already has (drift/sqflite/Isar/Hive); don't add another.
- **Outbox table:** every pending write (`id, type, payload, attempts, nextAttemptAt, status`). A worker drains it with backoff; operations are idempotent (see api-idempotency).
- **Pull sync:** per-chat cursor (`lastSeq` or server timestamp); fetch `> cursor`, upsert in one transaction, then advance the cursor.
- **Conflicts:** pick an explicit rule (server wins / last-write-wins by server time / merge) and document it; messages are append-only so conflicts are rare, edits/deletes need versioning.
- Connectivity API says "has interface", not "server reachable": treat request failures as the truth.
- Local schema migrations tested from old versions; sensitive local data encrypted or stored under platform protection.
- Test: airplane mode send, kill app with pending outbox, duplicate delivery, clock skew, partial sync failure mid-transaction.

## Outbox sketch (drift/sqflite style)
```sql
create table outbox(id text primary key, type text not null, payload text not null, attempts int not null default 0,
                    next_attempt_at int not null, status text not null default 'pending', created_at int not null);
```
Worker loop: select due rows (`status='pending' and next_attempt_at <= now`) ordered by `created_at`, send with the row id as idempotency key, on success delete/mark done in the same transaction as the local state update, on failure `attempts+1` with `next_attempt_at = now + backoff(attempts)`; park as `failed` after N attempts and surface a retry action. Trigger the worker on connectivity change, app resume, and a timer.

## Verify
Airplane-mode send then reconnect -> exactly one server message; kill the app with pending outbox -> resumes; two devices edit the same item; local migration from every older schema (`database-migrations`); storage growth bounded (prune old synced rows/media cache).

## Pitfalls
- Treating "connected to Wi-Fi" as "server reachable".
- Applying server pages without a transaction (partial state on crash).
- No retry ceiling: a poison message blocks the whole queue.

## Related
`api-idempotency`, `realtime-reconnect-client`, `android-architecture-room`, `supabase-realtime-storage`.
