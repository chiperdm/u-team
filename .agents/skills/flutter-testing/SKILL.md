---
name: flutter-testing
description: "Write reliable Flutter tests: unit tests with fakes/mocktail, widget tests (pump, finders, async states), golden tests with stable fonts, integration_test on device, Bloc/Riverpod/Provider test patterns, accessibility guideline checks, fake time, coverage. Use when adding or fixing tests in a Flutter project, when widget tests are flaky, or when a feature needs a regression test."
domain: flutter
---

# Flutter testing

Strategy and test pyramid: `testing-strategy`. Realtime specifics: `testing-realtime`. Use the project's existing libraries (mocktail vs mockito, bloc_test, etc.).

## Unit tests
- Pure Dart: no Flutter imports; inject clock/ids/random/network via constructors; fakes beat mocks for repositories.
```dart
test('retries with backoff and stops after max attempts', () {
  fakeAsync((async) {
    final api = FakeApi(failTimes: 3);
    final out = Outbox(api, clock: async.getClock(DateTime(2026)));
    unawaited(out.flush());
    async.elapse(const Duration(seconds: 31));
    expect(api.calls, 4);
  });
});
```
- Streams: `expectLater(stream, emitsInOrder([...]))`; close controllers in `tearDown`.

## Widget tests
```dart
testWidgets('shows retry on failed message', (tester) async {
  await tester.pumpWidget(MaterialApp(home: ChatScreen(repo: FakeRepo(failSend: true))));
  await tester.enterText(find.byKey(const Key('composer')), 'hi');
  await tester.tap(find.byTooltip('Send'));
  await tester.pump();                              // one frame
  await tester.pump(const Duration(milliseconds: 300));
  expect(find.text('Retry'), findsOneWidget);
});
```
- `pump()` = one frame; `pump(Duration)` advances time; `pumpAndSettle()` waits for animations to end and **hangs on infinite animations** (spinners, `repeat()`): pump fixed durations instead.
- Wrap in the same `MaterialApp` + theme + localization delegates as production; test `Locale('ru')`, `textScaleFactor` 2.0 (`MediaQuery` override), RTL (`Directionality`), dark theme.
- Prefer `find.byKey`/`find.bySemanticsLabel`/`find.text` over `find.byType` internals.
- All four async states: loading, data, error, empty (`flutter-state-management`).
- Accessibility: 
```dart
final handle = tester.ensureSemantics();
await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
await expectLater(tester, meetsGuideline(textContrastGuideline));
await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
handle.dispose();
```

## State management
- Bloc: `blocTest<ChatBloc, ChatState>('...', build: ..., act: (b) => b.add(Send('x')), expect: () => [...])`.
- Riverpod: `ProviderContainer(overrides: [...])`, `container.listen`, dispose container.
- Provider/ChangeNotifier: unit-test the notifier; widget-test via `ChangeNotifierProvider.value`.

## Golden tests
Only for stable, visual components. Pin viewport (`tester.view.physicalSize`/`devicePixelRatio`), theme, locale, text scale, and load real fonts (`loadAppFonts()` from a golden helper) because the default test font is blocky. Generate on one OS in CI (rendering differs by platform): `flutter test --update-goldens` locally for review only; review image diffs, never bulk-accept. Don't golden-test shader/blur effects (`flutter-liquid-glass`): test the fallback widget.

## Integration tests (`integration_test/`)
`IntegrationTestWidgetsFlutterBinding.ensureInitialized();` run with `flutter test integration_test -d <device>`. Cover critical flows only: login, send/receive, offline resend, restart-with-pending-outbox. Use a test backend or local server fake; seed/reset data per test; no real third-party calls.

## Platform channels
Mock with `TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger.setMockMethodCallHandler(channel, handler)` (`flutter-kotlin-platform-channels`).

## Flakiness checklist
Real timers (`Future.delayed`) -> use `fakeAsync`/`pump`; shared singletons -> reset in `setUp`; animations -> fixed pumps; network -> fakes; ordering assumptions -> sort/await explicitly; random -> seed.

## Commands and reporting
```bash
flutter test test/features/chat/        # narrowest first
flutter test --coverage && genhtml coverage/lcov.info -o coverage/html   # if lcov is installed
flutter analyze
```
Report exact command, counts (passed/failed/skipped), and what could not be run.

## Pitfalls
- `pumpAndSettle` timeouts from spinners.
- Tests that pass only with the default 800x600 surface: set the size explicitly.
- Asserting private widget structure instead of user-visible behavior.
- Forgetting `addTearDown(controller.dispose)`.

## Verify
`flutter analyze` and the narrow `flutter test <path>` run green three times in a row; new tests fail when the feature is deliberately broken; goldens (if any) were regenerated on the CI platform and reviewed visually.
