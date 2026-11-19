---
name: kotlin-compose-foundations
description: "Write and review Jetpack Compose UI correctly: state hoisting, remember/rememberSaveable, collectAsStateWithLifecycle, recomposition and stability, derivedStateOf, lazy list keys, side effects, Material 3 theming, adaptive layouts, edge-to-edge, semantics, previews and tests. Use for any Compose screen, component, performance or recomposition problem in Kotlin Android apps."
domain: android
---

# Jetpack Compose foundations

Follow the project's existing architecture (`rules/01-preserve-project.md`). No new libraries for a local task.

## State
- **Hoist state:** a composable takes `value` + `onValueChange`/events, owns no business state. Stateless leaf composables are previewable and testable.
- `remember` survives recomposition; `rememberSaveable` survives config change and process death (use for text fields, scroll, selected tab). Anything larger lives in a `ViewModel`.
- UI state = one immutable `data class` (or sealed interface) exposed as `StateFlow`; collect with `collectAsStateWithLifecycle()` (lifecycle-runtime-compose), not `collectAsState()`.
- One-off events (navigate, show snackbar): model them as state that the UI consumes and acknowledges, or a `Channel` collected in `LaunchedEffect`; avoid `SharedFlow` replay=0 events that get lost on rotation.
```kotlin
@Composable
fun ChatRoute(vm: ChatViewModel = hiltViewModel()) {
    val ui by vm.ui.collectAsStateWithLifecycle()
    ChatScreen(ui, onSend = vm::send, onRetry = vm::retry)
}
@Composable
fun ChatScreen(ui: ChatUiState, onSend: (String) -> Unit, onRetry: (MessageId) -> Unit) { /* stateless */ }
```

## Recomposition and performance
- Compose skips a composable when its inputs are stable and unchanged. With Kotlin 2.0.20+ strong skipping is on by default, but still prefer immutable data, `ImmutableList`/`kotlinx.collections.immutable` or wrapper classes for list params, and avoid passing unstable lambdas capturing changing values (use `remember` or method references).
- **Defer state reads** to the phase that needs them: `Modifier.offset { IntOffset(x.value, 0) }`, `graphicsLayer { alpha = a.value }`, `drawBehind { }` instead of reading in composition.
- `derivedStateOf` when a value changes less often than its inputs (`val showFab by remember { derivedStateOf { listState.firstVisibleItemIndex > 3 } }`).
- Lazy lists: always `key = { it.id }` and `contentType = { it.type }`; no heavy work in item composables; no nested scrolling in the same direction; don't put `LazyColumn` inside `verticalScroll`.
- Don't allocate in composition (new `Brush`, `Shape`, lists): `remember` them.
- Measure: Layout Inspector recomposition counts, Compose compiler metrics/reports (`reportsDestination`), Macrobenchmark + **Baseline Profiles** for startup/scroll, R8 on in release.

## Effects
- `LaunchedEffect(key)` for suspend work tied to a key; `rememberUpdatedState` for callbacks used inside long effects; `DisposableEffect` for register/unregister; `SideEffect` for publishing to non-Compose code; `produceState` to adapt callbacks.
- Never launch from composition body; never `GlobalScope`.

## Material 3 and theming
- `MaterialTheme(colorScheme, typography, shapes)` at the root; read colors from `MaterialTheme.colorScheme`, not hardcoded hex. Dynamic color (`dynamicLightColorScheme`) on API 31+ with a static fallback.
- Custom tokens (glass, spacing, brand) in a `CompositionLocal` (`staticCompositionLocalOf`) so `design-system-tokens` stay central.
- Typography: `sp`; layout: `dp`; respect font scale up to 200%.

## Adaptive layout and system UI
- `enableEdgeToEdge()` in the activity; apply `WindowInsets` (`Modifier.safeDrawingPadding()`, `imePadding()`, `navigationBarsPadding()`); `Scaffold` handles most with `innerPadding`.
- `currentWindowAdaptiveInfo()` / `WindowSizeClass` for phone vs foldable vs tablet: list-detail with `NavigableListDetailPaneScaffold` when the library is already used.
- Predictive back: `android:enableOnBackInvokedCallback="true"` and `BackHandler`/`PredictiveBackHandler`.

## Accessibility
`contentDescription` for images/icons-only buttons (null for decorative), `Modifier.semantics { }` and `mergeDescendants = true` for grouped rows, `clearAndSetSemantics`, `Role.Button`, minimum touch target 48 dp (`minimumInteractiveComponentSize`), test with TalkBack and font scale 2.0 (`ui-accessibility`).

## Testing
```kotlin
@get:Rule val rule = createComposeRule()
@Test fun sendButtonDisabledWhenEmpty() {
    rule.setContent { Composer(text = "", onSend = {}) }
    rule.onNodeWithContentDescription("Send").assertIsNotEnabled()
}
```
Use `onNodeWithTag` sparingly (stable tags for lists), `waitUntil` over sleeps; screenshot tests with Paparazzi/Roborazzi for stable UI (not for RenderEffect/AGSL, see `kotlin-compose-liquid-glass`).

## Previews
`@Preview` with light/dark, font scale 1.0/2.0, a long-text and an empty-state variant; use `@PreviewParameter` for states (loading/data/error/empty).

## Verify
`./gradlew :app:lintDebug :app:testDebugUnitTest`, `./gradlew :app:connectedDebugAndroidTest` when a device is available; check Layout Inspector for runaway recomposition on the changed screen; report commands and results.

## Pitfalls
- State read too high in the tree recomposes everything below.
- `remember` without keys when inputs change (stale value).
- Modifier order matters (`padding` before/after `background` changes the result).
- Passing `ViewModel` into deep composables (hard to preview/test): pass state and callbacks.
