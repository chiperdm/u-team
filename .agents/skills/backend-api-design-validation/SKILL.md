---
name: backend-api-design-validation
description: "Design clean, consistent, safe Node.js HTTP APIs: resource naming, status codes, error format (problem+json), input validation with zod at the boundary, pagination/filtering, versioning, OpenAPI, ETag/conditional requests, request size and timeout limits, contract tests. Use when adding or reviewing endpoints, defining request/response shapes, or when clients complain about inconsistent errors and breaking changes."
domain: backend
---

# API design and validation

Auth: `backend-authentication`. Retries: `api-idempotency`. Throttling: `backend-rate-limiting`. Errors/logging: `backend-errors-observability`. Injection: `security-injection-xss`.

## Conventions
- Resources are nouns, plural: `GET /v1/chats`, `POST /v1/chats/{id}/messages`, `PATCH /v1/users/me`. Actions that are not CRUD: `POST /v1/chats/{id}/read` (verb as sub-resource).
- Methods: GET safe and cacheable; POST create/non-idempotent (use `Idempotency-Key`); PUT replace; PATCH partial; DELETE idempotent (404 vs 204 on repeat: pick 204).
- Status codes: 200/201 (+`Location`)/204, 400 malformed, 401 unauthenticated, 403 forbidden, 404 not found (also for resources the caller must not know exist), 409 conflict, 412 precondition failed, 413 too large, 422 validation, 429 rate limited, 5xx never carries internals.
- JSON naming consistent (camelCase), ISO-8601 UTC timestamps, ids as strings, money as integer minor units + currency, no nulls vs missing ambiguity documented.
- Version in the path (`/v1`); additive changes are non-breaking; removing/renaming = new version; keep old mobile clients working for months (`database-migrations` expand/contract).

## Validate at the boundary (zod)
```ts
import { z } from 'zod';
export const SendMessage = z.object({
  clientMsgId: z.string().uuid(),
  body: z.string().trim().min(1).max(4000),
  replyTo: z.string().uuid().optional(),
}).strict();                                         // reject unknown keys

export const validate = (schema: z.ZodTypeAny, part: 'body' | 'query' | 'params' = 'body') =>
  (req, res, next) => {
    const r = schema.safeParse(req[part]);
    if (!r.success) return next(new AppError(422, 'VALIDATION_FAILED', { issues: r.error.issues.map(i => ({ path: i.path.join('.'), code: i.code, message: i.message })) }));
    req[part] = r.data;                              // use parsed/coerced data only
    next();
  };
app.post('/v1/chats/:chatId/messages', authenticate, validate(ChatParams, 'params'), validate(SendMessage), handler);
```
- Validate params, query (coerce numbers: `z.coerce.number().int().min(1).max(100).default(50)`), headers when relevant, and **responses in tests**.
- Reject, don't "clean". Limit sizes: `express.json({ limit: '64kb' })`, multipart limits separately (`security-file-upload`), array lengths, string lengths, nesting depth.
- Authorization is separate from validation: after parsing, check the caller may touch THIS object (ownership/membership); never trust ids/roles from the body.

## Error format (RFC 9457 problem details)
```json
{ "type": "https://api.example.com/errors/validation", "title": "Validation failed", "status": 422,
  "code": "VALIDATION_FAILED", "detail": "body.body: too long", "requestId": "01J...", "errors": [{ "path": "body", "message": "..." }] }
```
Stable machine-readable `code`s that clients switch on; human `detail` safe to show; `Content-Type: application/problem+json`; always include `requestId`; 5xx body generic.

## Pagination, filtering, sorting
Cursor (keyset) pagination for lists that grow (`database-indexing-query-plans`): `GET /v1/chats/{id}/messages?limit=50&before=<cursor>` -> `{ "items": [...], "nextCursor": "..." | null }`. Cursors opaque (base64url of `(created_at,id)`), signed or validated. Allowlist sort fields/filters. Cap `limit`.

## Caching and concurrency
`ETag` + `If-None-Match` (304) on cacheable GETs; `If-Match`/version column for optimistic concurrency on PATCH (412 on mismatch); `Cache-Control: no-store` for private data; `Vary` correctly.

## Timeouts, headers, hygiene
`server.requestTimeout`/`headersTimeout`, per-route timeouts for slow work (queue it, return 202 + status URL), `helmet` defaults for HTML-serving apps (`security-cors` for CORS), `trust proxy` correct behind a proxy, rate-limit headers (`RateLimit-*`, `Retry-After`), gzip/br at the proxy, consistent request id propagation.

## Documentation and contracts
Generate OpenAPI from the zod schemas (`zod-to-openapi`/`fastify` schemas) or write it first; serve at `/docs` only in non-prod or behind auth; contract-test with the same schemas; changelog for API changes (`docs-adr-handoff`).

## Verify: endpoint test matrix
Per endpoint: happy path; 401 without/with expired token; 403/404 for another user's resource; 422 for each invalid field; unknown field rejected; oversize body -> 413; pagination boundaries (empty, exactly limit, cursor round trip); idempotent retry returns the same result; error body shape stable; rate limit -> 429.

## Pitfalls
- Returning DB rows directly (leaks internal columns): map to response DTOs.
- Using 200 with `{ ok: false }` for errors.
- Accepting `req.query` strings as numbers without coercion/limits.
- Different error shapes from middleware vs handlers: one central error handler.
- Breaking change slipped into `/v1` because "only one client uses it".
