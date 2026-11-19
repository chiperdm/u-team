---
name: database-migrations
description: "Plan and write safe schema migrations for Postgres, Supabase and mobile SQLite (Room/drift): expand-contract, lock-aware DDL, batched backfills, rollback notes, tested upgrade paths. Use for any ALTER/CREATE/DROP, data backfill, column rename, or when old app versions must keep working."
domain: database
---

# Safe migrations

- Forward-only, versioned, reviewed. Take a backup / confirm a restore path before anything destructive; ask for approval on production.
- **Expand then contract:** release N adds (nullable column/new table), code writes both, backfill, release N+1 reads new, release N+2 drops old. Old app versions must keep working (mobile clients linger for months).
- Postgres lock awareness:
```sql
alter table messages add column edited_at timestamptz;                 -- nullable: fast
create index concurrently idx_messages_chat_created
  on messages (chat_id, created_at desc);                              -- cannot run inside a transaction
alter table messages add constraint messages_body_len
  check (char_length(body) <= 4000) not valid;                         -- no full scan lock
alter table messages validate constraint messages_body_len;            -- scans, weaker lock
```
- Backfill in batches (e.g. 5-10k rows, commit each, sleep), never one giant UPDATE.
- Set `lock_timeout` / `statement_timeout` for DDL so a blocked migration fails instead of freezing the app.
- Local SQLite (drift/Room): every schema bump needs a tested migration from EVERY released version; keep migration tests with old DB fixtures.
- Always write the rollback note ("revert = ..."), or state clearly that it is irreversible.

## Verify
Apply the migration to a copy of production-sized data and time it; check `pg_locks` while running; test the new server against the old client and the old server against the migrated schema; for mobile, run migration tests from every released schema version (Room `MigrationTestHelper`, drift `SchemaVerifier`).

## Pitfalls
- `ALTER TABLE ... ADD COLUMN ... DEFAULT <volatile>` or `NOT NULL` on a huge table in one step.
- Renaming a column in one release (breaks old clients): add new, dual-write, backfill, switch reads, drop later.
- Running destructive migrations automatically on deploy without a backup and approval.

## Related
`android-architecture-room`, `database-indexing-query-plans`, `release-checklist-rollback`, `devops-docker-nginx` (backups).
