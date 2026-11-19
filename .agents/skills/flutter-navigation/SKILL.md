---
name: flutter-navigation
description: "Implement or fix Flutter navigation: go_router declarative routes, auth redirects, StatefulShellRoute for bottom tabs, deep links and Android App Links, typed routes, passing parameters, back handling (PopScope, predictive back), web URLs and testing. Use for routing bugs, redirect loops, lost tab state, deep link or notification-tap navigation, or when adding screens to a Flutter app."
domain: flutter
---

# Flutter navigation

**First detect what the project uses** (Navigator 1.0 `push/pop`, `go_router`, `auto_route`, Beamer...). Follow it; do not migrate routers for a local task. Below is go_router, the common default; check the package version's docs for API changes.

## go_router basics
```dart
final router = GoRouter(
  initialLocation: '/chats',
  refreshListenable: authNotifier,                 // re-run redirect when auth changes
  redirect: (context, state) {
    final loggedIn = authNotifier.isLoggedIn;
    final goingToLogin = state.matchedLocation == '/login';
    if (!loggedIn) return goingToLogin ? null : '/login?from=${Uri.encodeComponent(state.uri.toString())}';
    if (goingToLogin) return state.uri.queryParameters['from'] ?? '/chats';
    return null;                                    // no redirect
  },
  routes: [
    GoRoute(path: '/login', builder: (_, s) => const LoginScreen()),
    StatefulShellRoute.indexedStack(
      builder: (_, __, shell) => HomeScaffold(shell: shell),     // bottom bar uses shell.goBranch(i)
      branches: [
        StatefulShellBranch(routes: [GoRoute(path: '/chats', builder: (_, __) => const ChatsScreen(), routes: [
          GoRoute(path: ':chatId', builder: (_, s) => ChatScreen(chatId: s.pathParameters['chatId']!)),
        ])]),
        StatefulShellBranch(routes: [GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen())]),
      ],
    ),
  ],
  errorBuilder: (_, s) => NotFoundScreen(location: s.uri.toString()),
);
MaterialApp.router(routerConfig: router);
```
- `context.go('/chats/42')` replaces the stack to that location; `context.push` adds on top (returns a result); `context.pop()`; `go` between tabs keeps branch state with `StatefulShellRoute`.
- Pass **IDs in the path** (`:chatId`), small filters as query parameters, never large objects (`extra` is lost on web refresh and deep links). Re-load data in the destination from its ID.
- Validate parameters (`int.tryParse` -> redirect to not-found), never trust deep link input (`security-injection-xss`).
- Typed routes: `go_router_builder` with `@TypedGoRoute` generates `ChatRoute(chatId: ...).go(context)`; keep the generated file committed or generated in CI.

## Redirect pitfalls
- Loops: a redirect must return `null` when already at the target; never redirect based on state that the redirect itself changes.
- Redirect runs on every navigation; keep it synchronous and cheap; async auth state belongs in a `Listenable` the router refreshes on (`refreshListenable`), with a splash route while loading.
- Don't call `context.go` inside `build`; navigate from listeners/handlers (`flutter-state-management`).

## Deep links and notification taps
- Android App Links: `intent-filter` with `android:autoVerify="true"`, `<data android:scheme="https" android:host="example.com" android:pathPrefix="/chat"/>`, host `/.well-known/assetlinks.json` with the app's SHA-256 signing fingerprint (use the Play App Signing fingerprint for store builds). Custom schemes (`myapp://`) work without verification but anyone can claim them.
- Flutter handles deep links by default through the router; ensure routes exist for each link pattern and an unknown link gives a friendly not-found screen.
- Notification tap (FCM): put a route string/ID in the payload; on tap call `router.go(location)`; handle cold start via the initial message (`FirebaseMessaging.instance.getInitialMessage()`) after auth is ready.
- Links that perform actions (accept invite, delete) must show a confirmation screen, not act on open.

## Back handling
`PopScope(canPop: false, onPopInvokedWithResult: (didPop, result) { if (!didPop) showDiscardDialog(); })` for unsaved changes (older versions use `WillPopScope`). Android 14+ predictive back needs `android:enableOnBackInvokedCallback="true"` and `PopScope` (not the legacy callback). Root tab back should leave the app or go to the first tab, per your UX rule.

## Web
`usePathUrlStrategy()` for clean URLs plus server rewrites to `index.html`; test refresh on a deep URL; titles per route.

## Testing
```dart
testWidgets('unauthenticated user is redirected to login', (tester) async {
  final auth = FakeAuth(loggedIn: false);
  await tester.pumpWidget(MaterialApp.router(routerConfig: buildRouter(auth)));
  await tester.pumpAndSettle();
  expect(find.byType(LoginScreen), findsOneWidget);
});
```
Add tests for: deep link to a protected route -> login -> back to target; tab state preserved; unknown route; invalid ID.

## Verify
`flutter analyze`, `flutter test`, manual: cold-start from a link, warm start, notification tap with app killed, rotate, back button on every screen, `adb shell am start -a android.intent.action.VIEW -d "https://example.com/chat/42"`.

## Pitfalls
- Using `Navigator.push` and `GoRouter` mixed in the same flow (stack mismatch).
- Losing scroll position because the tab widget is rebuilt (use `StatefulShellRoute`/`AutomaticKeepAliveClientMixin`).
- Passing a `BuildContext` across async gaps without `mounted` checks.
- Hardcoded path strings everywhere: centralize route names/typed routes.
