---
name: firebase-rules-auth
description: "Secure Firebase backends for apps: Auth setup, Firestore and Realtime Database security rules (ownership, membership, field validation), custom claims, App Check, rules unit tests with the emulator, FCM token and message handling, Admin SDK key hygiene, and cost-aware data modeling. Use when writing or reviewing Firestore/RTDB rules, fixing permission-denied, designing chat data in Firebase, or when a Firebase app is open to the public."
domain: security
---

# Firebase rules, Auth, App Check

If the project stores files elsewhere (e.g. Supabase Storage), keep Firebase for Auth/Firestore/FCM only and do not add Firebase Storage without a reason. Rules are the **only** server-side authorization for client SDK access: treat them like an API.

## Principles
- Default deny. Never ship `allow read, write: if true;` or time-boxed test rules (`request.time < ...`) to production.
- Authenticate (`request.auth != null`), then authorize by ownership or membership, then **validate data shape**.
- Rules are not filters: a query must itself satisfy the rule (queries that could return unauthorized docs are rejected). Design collections so allowed queries are expressible (`where('members', 'array-contains', uid)`).
- Admin SDK / service account JSON bypasses rules: server only, never in the app or repo (`security-secrets-logging`).

## Firestore rules patterns
```
rules_version = '2';
service cloud.firestore {
  match /databases/{db}/documents {
    function signedIn() { return request.auth != null; }
    function isOwner(uid) { return signedIn() && request.auth.uid == uid; }
    function isMember(chatId) { return signedIn() && exists(/databases/$(db)/documents/chats/$(chatId)/members/$(request.auth.uid)); }
    function onlyKeys(keys) { return request.resource.data.keys().hasOnly(keys); }

    match /users/{uid} {
      allow read: if signedIn();
      allow create, update: if isOwner(uid) && onlyKeys(['displayName','photoPath','updatedAt'])
                         && request.resource.data.displayName is string && request.resource.data.displayName.size() <= 50;
      allow delete: if false;
    }
    match /chats/{chatId} {
      allow read: if isMember(chatId);
      allow create: if signedIn() && request.resource.data.createdBy == request.auth.uid;
      match /members/{uid} { allow read: if isMember(chatId); allow write: if false; }   // membership managed by trusted backend
      match /messages/{msgId} {
        allow read: if isMember(chatId);
        allow create: if isMember(chatId)
          && request.resource.data.senderId == request.auth.uid
          && onlyKeys(['senderId','body','createdAt','clientMsgId'])
          && request.resource.data.body is string && request.resource.data.body.size() <= 4000
          && request.resource.data.createdAt == request.time;
        allow update, delete: if false;            // immutable from client
      }
    }
  }
}
```
Notes: `exists/get` calls count as billable reads and are limited per request (10 for single-document requests, 20 for multi-document, verify current docs); denormalize or use custom claims for hot paths; use the document ID = `clientMsgId` for idempotent sends (`api-idempotency`); server timestamps via `FieldValue.serverTimestamp()` matched by `request.time`.

## Realtime Database rules
`.read/.write` cascade downward (a grant at a parent cannot be revoked below): keep them at leaf paths; use `.validate` for shape; index with `.indexOn` for queried fields; structure chats flat and denormalized.

## Auth and claims
Providers: email link/OTP, phone (SMS costs, abuse risk: enable App Check, rate limits), Google. Custom claims (`admin`, `role`) set via Admin SDK on the server and read in rules as `request.auth.token.role`; claims propagate on token refresh (force refresh after change). Revoke sessions on compromise (`revokeRefreshTokens`). Never trust client-supplied roles.

## App Check
Enforce App Check (Play Integrity on Android, DeviceCheck/App Attest on iOS, reCAPTCHA on web) for Firestore/RTDB/Functions to cut abuse from copied clients; roll out in "monitor" mode first. It complements, does not replace, rules.

## FCM
- Token lifecycle: get on login, send to your backend with the user id, refresh on `onTokenRefresh`, delete on logout; remove invalid tokens when the send API reports `UNREGISTERED`.
- Use **data messages** with high priority for chat wake-ups and build the notification on device (privacy, E2EE: no content in payload, see `e2ee-messaging-review`); `notification` messages are displayed by the system when the app is in background and give you less control.
- Android 13+: runtime `POST_NOTIFICATIONS`; channels; handle background isolates in Flutter (`kotlin-android-background`, `flutter-kotlin-platform-channels`).
- Send from a trusted backend (Admin SDK) with the user's authorization checks, not from clients.

## Data modeling and cost
Billing is per read/write: avoid listening to large collections; paginate with `limit` + `startAfter`; store counters in the parent doc carefully (write contention ~1/s per doc: shard); denormalize chat list summaries (last message, unread count) updated by trusted code; TTL policies for ephemeral data; composite indexes declared in `firestore.indexes.json`.

## Test rules with the emulator
```bash
npm i -D @firebase/rules-unit-testing firebase-tools
firebase emulators:exec --only firestore "npm test"
```
```js
const env = await initializeTestEnvironment({ projectId: 'demo-test', firestore: { rules: fs.readFileSync('firestore.rules', 'utf8') } });
const alice = env.authenticatedContext('alice').firestore();
await assertFails(alice.doc('chats/c1/messages/m1').set({ senderId: 'alice', body: 'x', createdAt: serverTimestamp(), clientMsgId: 'm1' })); // not a member
```
Cases: anonymous denied; member reads; non-member denied; spoofed `senderId` denied; extra field denied; oversize body denied; update/delete denied; privilege escalation via `members` denied. Run in CI (`devops-ci-flutter-node`).

## Verify
Rules deployed from the repo (not edited in the console), emulator tests green, Rules Playground spot checks, no test-mode rules in the project (console warns), App Check metrics reviewed, no service-account JSON in the repo (`hooks/pre-commit-secret-scan.sh --all .`).

## Pitfalls
- Trusting `request.resource.data.senderId` without comparing to `request.auth.uid`.
- Membership list writable by clients (anyone can add themselves).
- Cascading RTDB rules granting too much at the root.
- Listening to a whole collection for a badge count (cost explosion).
- Leaving "test mode" open for weeks.
