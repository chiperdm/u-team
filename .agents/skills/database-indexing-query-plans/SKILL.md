---
name: database-indexing-query-plans
description: "Diagnose slow SQL and design indexes with EXPLAIN ANALYZE; keyset pagination for message lists; composite, partial and covering indexes. Use when a query or list endpoint is slow, CPU on the database is high, pagination skips or duplicates rows, or before adding any index."
domain: database
---

# Indexes and plans

1. Find the slow queries first (`pg_stat_statements`, slow log). Don't guess.
2. `EXPLAIN (ANALYZE, BUFFERS) <query>`: look for Seq Scan on big tables, big gap between estimated and actual rows, sorts spilling to disk, high `Buffers: read`.
3. Composite index order = equality columns first, then range/sort column: `(chat_id, created_at DESC, id DESC)`.
4. Partial indexes for hot subsets (`where deleted_at is null`). Covering (`include`) only when proven.
5. Every index slows writes and costs space: drop unused ones (`pg_stat_user_indexes.idx_scan = 0` over a long period).
6. After adding an index re-run EXPLAIN and compare numbers; record before/after.

## Keyset pagination (not OFFSET)
```sql
select * from messages
where chat_id = $1 and (created_at, id) < ($2, $3)
order by created_at desc, id desc
limit 50;
```
Return the last row's `(created_at, id)` as the cursor. OFFSET gets slower with depth and skips/duplicates rows when new messages arrive.

## Verify
Save `EXPLAIN (ANALYZE, BUFFERS)` before and after; compare actual time, rows, buffers; test with production-like data volume (a dev DB with 100 rows proves nothing); check write latency did not regress; run `ANALYZE` after bulk loads.

## Pitfalls
- Indexing every column "just in case".
- Functions on indexed columns in `WHERE` (`lower(email)` needs an expression index).
- `OFFSET` pagination on large tables.
- `SELECT *` on wide rows when two columns are needed.

## Related
`database-migrations` (`CREATE INDEX CONCURRENTLY`), `database-rls-supabase` (index policy columns), `performance-profiling-budgets`, `backend-api-design-validation`.
