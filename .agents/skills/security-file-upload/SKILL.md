---
name: security-file-upload
description: "Implement or audit file/image/voice upload and download in a backend: size limits, magic-byte type detection, random names, private storage, signed URLs, EXIF stripping, quotas, cleanup. Use for avatars, chat media, document sharing, or any multipart/binary endpoint."
domain: security
---

# File upload

- Enforce limits at proxy AND app: max size, max count, request timeout.
- Detect type by **magic bytes** (e.g. `file-type`), not extension or client `Content-Type`; allowlist types.
- Generate server-side random names (uuid); never use the user filename in a path (path traversal); keep original name only as metadata.
- Store in object storage/private bucket, not in a web-served directory. Serve via **short-lived signed URLs** after an authorization check (user belongs to that chat).
- Serve user files with `Content-Disposition: attachment` unless it is a verified image; never serve user SVG/HTML inline from your origin.
- Strip EXIF/GPS from images; re-encode images server side when feasible (also kills many polyglots).
- Quotas per user, cleanup of orphans and of deleted chats' media; antivirus scan if files are shared widely.
- Tests: oversize, wrong magic bytes, `../` filename, zero-byte, concurrent uploads, expired signed URL, other user's file id.

## Snippet (Node, magic bytes + random name)
```js
import { fileTypeFromBuffer } from 'file-type';
const ALLOWED = new Map([['image/jpeg', 'jpg'], ['image/png', 'png'], ['image/webp', 'webp']]);
const ft = await fileTypeFromBuffer(buf);
if (!ft || !ALLOWED.has(ft.mime)) throw new AppError(415, 'UNSUPPORTED_TYPE');
const key = `${chatId}/${crypto.randomUUID()}.${ALLOWED.get(ft.mime)}`;
```

## Verify
Tests listed above plus: SVG/HTML upload is not rendered inline from your origin; image bomb (huge dimensions) rejected before decode; deleting a chat removes its media.

## Related
`supabase-realtime-storage`, `e2ee-messaging-review` (encrypted media), `backend-api-design-validation`, `html-single-file-app` (client-side validation).
