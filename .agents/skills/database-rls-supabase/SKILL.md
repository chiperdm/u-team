---
name: database-rls-supabase
description: "Design, write and test Postgres/Supabase Row Level Security and storage policies for multi-user apps such as chats; security definer pitfalls; testing as a real user. Use for any table reachable from a client, 'permission denied' or 'new row violates row-level security' errors, or data leaking between users."
domain: database
---

# Row Level Security (Supabase/Postgres)

## Rules
- `enable row level security` on EVERY table in an exposed schema. RLS on + no policy = deny all (safe default).
- One policy per operation (select/insert/update/delete); `using` filters existing rows, `with check` validates new/changed rows. Update usually needs both.
- Wrap auth calls: `(select auth.uid())` instead of bare `auth.uid()` so Postgres evaluates it once per query, not per row.
- Index columns used in policies (`chat_members(user_id, chat_id)`).
- The `service_role` key bypasses RLS: server only, never in the app, never in git.
- `security definer` functions: set `search_path = ''` (or a fixed schema), schema-qualify names, restrict `execute` grants.
- Storage buckets need their own policies on `storage.objects`; do not make private-chat media buckets public.
- Views bypass RLS of underlying tables unless created with `security_invoker = true` (Postgres 15+).

## Chat example
```sql
alter table public.messages enable row level security;

create policy messages_select on public.messages for select to authenticated
using (exists (select 1 from public.chat_members m
               where m.chat_id = messages.chat_id and m.user_id = (select auth.uid())));

create policy messages_insert on public.messages for insert to authenticated
with check (sender_id = (select auth.uid())
  and exists (select 1 from public.chat_members m
              where m.chat_id = messages.chat_id and m.user_id = (select auth.uid())));
-- no update/delete policy = nobody can edit/delete from the client
```

## Test as a real user (inside a transaction)
```sql
begin;
set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"<user-uuid>"}', true);
select count(*) from public.messages;           -- only own chats
insert into public.messages(chat_id, sender_id, body) values ('<foreign-chat>', '<user-uuid>', 'x'); -- must fail
rollback;
```
Also test: anonymous role sees nothing; user A cannot read/insert in B's chat; user cannot spoof `sender_id`.

## Verify checklist
- Every exposed table: `select relrowsecurity from pg_class where relname = '<t>'` is true.
- Run the "Test as a real user" block for each role: `anon`, `authenticated` (owner), `authenticated` (stranger).
- Supabase advisors/linter (dashboard Security Advisor) clean; no policy uses `using (true)` on private data; `service_role` absent from client code (`grep -R service_role`).

## Pitfalls
- Testing in the SQL editor (runs as a privileged role and bypasses RLS).
- Policy subqueries that read a table which itself has a recursive policy (infinite recursion): use a `security definer` helper with a fixed `search_path`.
- Forgetting `with check` on update so users can reassign rows to others.
- Public storage buckets for private media.

## Related
`supabase-realtime-storage`, `firebase-rules-auth` (same ideas for Firebase), `database-indexing-query-plans`, `security-threat-modeling`.
