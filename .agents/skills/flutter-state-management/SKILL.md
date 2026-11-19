---
name: flutter-state-management
description: "Work inside an existing Flutter state-management approach (Provider, Bloc/Cubit, Riverpod, setState) without replacing it; fix rebuild storms, lifecycle leaks, async state handling. Use for state bugs, UI not updating, unnecessary rebuilds, memory leaks from listeners, or when adding a feature to a stateful screen."
domain: flutter
---

# Flutter state

1. **Identify** what the project already uses (pubspec + a few files) and follow it. Do not introduce a second state library for a local task.
2. One source of truth per piece of state; UI derives from it. Immutable state objects (copyWith / freezed if already used).
3. No business logic or I/O in `build()`; side effects in handlers/notifiers/blocs; navigation from listeners, not from build.
4. Limit rebuilds: `Selector`/`context.select`/`BlocSelector`/`buildWhen`; split large widgets; `const` constructors.
5. Dispose everything: `StreamSubscription.cancel`, controllers, timers, `ChangeNotifier.dispose`. Check `mounted` after `await` before using `context`/`setState`.
6. Async state is a union: loading / data / error / empty. Show all four.
```dart
// Provider: rebuild only when unread count changes
final unread = context.select<ChatsNotifier, int>((n) => n.unreadCount);
```
7. Tests: unit-test the notifier/bloc with fakes; widget-test the 4 async states.

## Per-library cheat sheet
- **Provider:** `ChangeNotifierProvider` creates and disposes; `context.read` for events, `context.watch/select` in build; avoid `Provider.of(listen: true)` in callbacks.
- **Bloc/Cubit:** events in, immutable states out; `buildWhen/listenWhen`; side effects (navigation, snackbars) in `BlocListener`; close streams in `close()`.
- **Riverpod:** `ref.watch` in build, `ref.read` in handlers, `ref.listen` for side effects, `autoDispose` for screen-scoped state, `family` for per-id state.
- **setState:** fine for local ephemeral UI state (animation toggles, text focus), not for shared data.

## Verify
`flutter test` for the notifier/bloc; widget tests for loading/data/error/empty (`flutter-testing`); DevTools "Rebuild stats" / `debugPrintRebuildDirtyWidgets` shows only the intended subtree rebuilding; no `setState() called after dispose()` in logs.

## Pitfalls
- Mutating state objects in place (no change notification).
- Creating a controller/notifier inside `build`.
- Two sources of truth (local widget state mirroring bloc state).

## Related
`flutter-chat-ui`, `flutter-navigation`, `flutter-testing`, `flutter-performance-jank`.
