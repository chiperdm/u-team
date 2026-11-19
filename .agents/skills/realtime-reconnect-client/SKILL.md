---
name: realtime-reconnect-client
description: "Implement or debug client-side WebSocket reconnect and resync (Flutter/Dart, Kotlin, JS): exponential backoff with jitter, auth failure handling, single-connection guard, missed-message resync, lifecycle and connectivity handling. Use for reconnect loops, duplicate sockets, 'messages missing after offline', or battery drain from reconnect storms."
domain: realtime
---

# Reconnect and resync

## Rules
- **Exponential backoff with jitter**, 1 s up to 30 s cap. Reset the attempt counter only after the connection stayed healthy (e.g. 10 s), otherwise a flapping server causes a tight loop.
- **Single connection guard:** one `connecting`/`connected` state machine; ignore a new connect while one is in flight. Duplicate sockets are the #1 cause of duplicated messages.
- **Do not blindly retry auth failures** (close code 4401/403): refresh the token once, then reconnect; if refresh fails, go to logged-out state.
- **Resync, don't assume.** After reconnect ask the server for everything after `lastSeenSeq` (or cursor) per chat. Never rely on the socket having delivered everything.
- **Dedupe by message id** on the client; merge server data over optimistic local items.
- Listen to connectivity and app lifecycle: pause timers in background, reconnect on resume; treat "has network" as a hint, not proof of reachability.
- Cancel the timer and close the socket in `dispose()`.

## Dart sketch
```dart
Duration _delay(int attempt) {
  final cap = min(30000, 1000 << min(attempt, 5)); // 1s,2s,4s,8s,16s,30s
  return Duration(milliseconds: cap ~/ 2 + Random().nextInt(cap ~/ 2 + 1));
}
Future<void> _connect() async {
  if (_state != ConnState.idle) return;              // single-connection guard
  _state = ConnState.connecting;
  try {
    _ch = IOWebSocketChannel.connect(uri, headers: {'Authorization': 'Bearer $token'});
    await _ch!.ready;
    _state = ConnState.connected;
    _stableTimer = Timer(const Duration(seconds: 10), () => _attempt = 0);
    await _resync();
  } catch (_) { _scheduleReconnect(); }
}
```

## Debug recipe for loops
Log: attempt number, close code/reason, time connected. Typical findings: server closes with 4401 each time (stale token), proxy idle timeout shorter than heartbeat, two connect() callers, timer not cancelled on logout.

## Kotlin and JS equivalents
```kotlin
// Kotlin: wrap in a Flow with retryWhen (see kotlin-coroutines-flow)
fun events() = connect().retryWhen { cause, attempt ->
    if (cause is AuthException) { refreshTokenOrThrow(); true } else { delay(backoffWithJitter(attempt)); true } }
```
```js
// JS: one state machine, reconnect on close except 4401 after refresh failure
let attempt = 0, timer = null, ws = null;
function connect() { if (ws && ws.readyState <= 1) return; ws = new WebSocket(url);
  ws.onopen = () => { /* auth + resync(lastSeq) */ setTimeout(() => attempt = 0, 10_000); };
  ws.onclose = (e) => { if (e.code === 4401 && !refreshed) return logout(); timer = setTimeout(connect, backoff(attempt++)); }; }
document.addEventListener('visibilitychange', () => { if (!document.hidden) connect(); });
```

## Verify
Kill the server, wait, restart: clients reconnect without a tight loop (log delays); toggle airplane mode; expire the token mid-session; background/foreground the app; confirm no gaps/duplicates after resync (`testing-realtime`).

## Pitfalls
Resetting the attempt counter on `onopen` (flapping server); not clearing timers on logout; relying on `onclose` being fired promptly on mobile (add heartbeat timeout on the client too).

## Related
`backend-node-websocket`, `supabase-realtime-storage`, `flutter-offline-first`, `kotlin-coroutines-flow`.
