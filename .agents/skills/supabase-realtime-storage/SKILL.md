---
name: supabase-realtime-storage
description: "Use Supabase Realtime and Storage correctly in chat/social apps: Postgres Changes vs Broadcast vs Presence, private channels and authorization, filters, reconnect/resync, storage buckets and policies, signed URLs, upload limits and MIME checks, client key handling, and a primary/reserve backend failover pattern. Use when building or debugging Supabase subscriptions, file/media upload, typing/presence, or multi-backend setups."
domain: database
---

# Supabase Realtime and Storage

RLS fundamentals: `database-rls-supabase`. Client reconnect and resync: `realtime-reconnect-client`. Verify API names against the `supabase-js` version in the project (v2 shapes below).

## Realtime: pick the right feature
| Feature | Use for | Notes |
|---|---|---|
| **Postgres Changes** | row inserts/updates visible to authorized users (new message, status change) | enable the table in the `supabase_realtime` publication; changes are checked against RLS; throughput/fan-out is limited, so heavy rooms should use Broadcast |
| **Broadcast** | ephemeral events: typing, cursors, ephemeral signals, low-latency fan-out | not persisted; use private channels + Realtime Authorization (RLS on `realtime.messages`) for protected rooms |
| **Presence** | who is online in a room | small rooms; state is per-connection, expires on disconnect |
```ts
const channel = supabase.channel(`chat:${chatId}`, { config: { private: true } })   // private => authorization enforced
  .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'messages', filter: `chat_id=eq.${chatId}` },
      (payload) => addMessage(payload.new))
  .on('broadcast', { event: 'typing' }, ({ payload }) => setTyping(payload.userId))
  .subscribe((status) => { if (status === 'SUBSCRIBED') resync(chatId); });          // resync after (re)connect
// typing: throttle to ~1 per 3 s
channel.send({ type: 'broadcast', event: 'typing', payload: { userId } });
// cleanup (important): supabase.removeChannel(channel)
```
Rules:
- **Never trust the stream as complete.** After every `SUBSCRIBED` (including reconnects) fetch messages `> lastSeen` by cursor and merge by id (`flutter-offline-first`, `api-idempotency`).
- One channel per room, removed on leave/dispose; don't create channels inside build/render loops.
- Filters are server-side but limited (single `eq`/simple filters): re-check membership in RLS, not only in the filter.
- Do not rely on `payload.old` for deletes unless the table has `REPLICA IDENTITY FULL`.
- Use the user's JWT (anon key + authenticated session). The `service_role` key bypasses RLS and must never be in a client.

## Storage
```ts
const path = `${chatId}/${crypto.randomUUID()}.jpg`;                  // server/random names, no user filename
const { error } = await supabase.storage.from('chat-media').upload(path, file, { contentType: file.type, upsert: false, cacheControl: '3600' });
const { data } = await supabase.storage.from('chat-media').createSignedUrl(path, 60);   // short-lived read link
```
- **Private bucket by default** for chat media; public buckets only for truly public assets (avatars of public profiles, site images).
- Bucket config: `file_size_limit`, `allowed_mime_types`; also validate on the client for UX and on a server/Edge Function when needed (`security-file-upload`: magic bytes, strip EXIF).
- Policies on `storage.objects` scoped by bucket and path prefix:
```sql
create policy chat_media_read on storage.objects for select to authenticated
using (bucket_id = 'chat-media' and exists (
  select 1 from public.chat_members m
  where m.chat_id::text = (storage.foldername(name))[1] and m.user_id = (select auth.uid())));
create policy chat_media_insert on storage.objects for insert to authenticated
with check (bucket_id = 'chat-media' and exists (
  select 1 from public.chat_members m
  where m.chat_id::text = (storage.foldername(name))[1] and m.user_id = (select auth.uid())));
```
- Store the object **path** in your DB (not a permanent URL); generate signed URLs on demand and cache until expiry minus margin.
- Cleanup: delete objects when messages/chats are deleted (database trigger -> queue/Edge Function or periodic job); quotas per user; image thumbnails/resizing via transformations or pre-upload resize.
- Uploads on flaky networks: use resumable (TUS) uploads for large files, show progress, retry with backoff, tie to an outbox entry (`flutter-offline-first`).

## Typical failures
| Symptom | Cause |
|---|---|
| Subscribed but no events | table not in publication; RLS denies; wrong filter syntax; channel not private/authorized; token expired (refresh and resubscribe) |
| Events stop after backgrounding | socket closed by OS; reconnect + resync on resume |
| `new row violates row-level security policy` on upload | missing insert policy or path prefix mismatch |
| 400/403 on signed URL | bucket private + wrong path, or policy missing for `select` |
| Duplicates in UI | no dedupe by id when merging stream + fetch |
| Works as owner, not as user | tested with `service_role` or the SQL editor (bypasses RLS): test as `authenticated` |

## Primary + reserve backend pattern (two Supabase projects)
Use only with a clear data rule, otherwise data diverges.
- Define roles: **primary** takes writes; **reserve** is a warm standby (kept in sync by your own replication/ETL or periodic export/import) or read-only fallback. Two independent writable projects without reconciliation create split-brain.
- Client config: ordered endpoint list `[primary, reserve]`, health check (`GET /rest/v1/` with short timeout) with exponential backoff, circuit breaker (after N failures switch for M minutes), visible "degraded mode" banner, queue writes in the local outbox and replay to the primary when it returns.
- Auth tokens are per project: users must exist on both, or the reserve serves public/read data only; document what works in degraded mode.
- Test failover by blocking the primary host (hosts file/proxy), not just by reading code.

## Verify
Two real clients: A sends, B receives (Postgres Changes and Broadcast); user not in the chat receives nothing and cannot read/upload; kill network, reconnect, confirm resync without gaps/duplicates; upload oversize/wrong MIME rejected; signed URL expires; policies tested as `authenticated` and `anon` (SQL snippet in `database-rls-supabase`).

## Pitfalls
- Public bucket "temporarily" holding private media.
- Using Postgres Changes for a 10k-member room.
- Subscribing before the session is ready (anonymous subscription).
- Forgetting `removeChannel` -> leaked sockets and duplicate callbacks.
