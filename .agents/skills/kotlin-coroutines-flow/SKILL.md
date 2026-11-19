---
name: kotlin-coroutines-flow
description: "Use Kotlin coroutines and Flow correctly in Android and backend code: structured concurrency, scopes, dispatchers, cancellation, exception handling, StateFlow vs SharedFlow vs Channel, stateIn/WhileSubscribed, callbackFlow, backpressure operators, and testing with runTest and Turbine. Use for lag, leaks, lost events, crashes in launch, flow collection bugs, or when wrapping callbacks and sockets."
domain: android
---

# Coroutines and Flow

## Scopes and structure
- Every coroutine has an owner: `viewModelScope`, `lifecycleScope`, a service scope you cancel in `onDestroy`, or an injected `CoroutineScope`. No `GlobalScope`. No `runBlocking` on the main thread.
- Inject dispatchers (`class Repo(private val io: CoroutineDispatcher = Dispatchers.IO)`) so tests can replace them. Switch with `withContext(io)` at the data boundary; suspend functions should be main-safe.
- `CancellationException` must propagate: when catching `Exception` re-throw it (`catch (e: CancellationException) { throw e }`) or catch narrower types. `runCatching` swallows cancellation; avoid it around suspend calls.
- `launch` failures propagate to the parent scope (can crash); `async` failures surface on `await`. Use `supervisorScope`/`SupervisorJob` when siblings should survive each other; add a `CoroutineExceptionHandler` only at the root for logging.
- Cancellation is cooperative: long loops call `ensureActive()`/`yield()`; blocking APIs (`Thread.sleep`, file IO) need `withContext(Dispatchers.IO)` and are not cancelled by themselves.
- `withTimeout`/`withTimeoutOrNull` for network calls.

## Flow choices
| Need | Use |
|---|---|
| Current UI state (always has a value) | `StateFlow` (`MutableStateFlow`), conflated, equality-based |
| Events to many collectors | `SharedFlow(replay = 0, extraBufferCapacity = 64, onBufferOverflow = DROP_OLDEST)` |
| One-time event to a single consumer | `Channel(Channel.BUFFERED)` + `receiveAsFlow()` (or model as state) |
| Cold sequence (DB query, request) | `flow { }` |
```kotlin
val ui: StateFlow<ChatUiState> = combine(repo.messages(chatId), draft, connection) { m, d, c -> ChatUiState(m, d, c) }
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), ChatUiState.Loading)
```
`WhileSubscribed(5_000)` keeps upstream alive across rotation and stops it when the UI is gone.

## Collecting on Android
Compose: `collectAsStateWithLifecycle()`. Views: `lifecycleScope.launch { repeatOnLifecycle(Lifecycle.State.STARTED) { flow.collect { } } }`. Plain `lifecycleScope.launch { flow.collect }` keeps collecting in the background (battery, crashes).

## Wrapping callbacks and sockets
```kotlin
fun WebSocketClient.events(): Flow<WsEvent> = callbackFlow {
    val listener = object : WsListener {
        override fun onMessage(m: String) { trySend(WsEvent.Message(m)) }
        override fun onClosed(code: Int) { trySend(WsEvent.Closed(code)); close() }
        override fun onError(t: Throwable) { close(t) }
    }
    addListener(listener)
    awaitClose { removeListener(listener) }        // mandatory: avoids leaks
}.buffer(Channel.BUFFERED)
```
Reconnect with `retryWhen { cause, attempt -> delay(backoff(attempt)); cause is IOException }` plus jitter (`realtime-reconnect-client`).

## Operators worth knowing
`debounce` (search box), `distinctUntilChanged`, `conflate`/`collectLatest` (cancel stale work), `flatMapLatest` (switch), `combine` vs `zip`, `flowOn` (upstream dispatcher only), `catch` (upstream errors only), `onEach`, `shareIn`, `chunked` via `buffer`/custom.

## Testing
```kotlin
@Test fun emitsLoadingThenData() = runTest {
    val repo = FakeRepo()
    val vm = ChatViewModel(repo, StandardTestDispatcher(testScheduler))
    vm.ui.test {                                   // Turbine
        assertEquals(ChatUiState.Loading, awaitItem())
        repo.emit(listOf(msg))
        assertEquals(ChatUiState.Data(listOf(msg)), awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```
Set `Dispatchers.setMain(testDispatcher)` in a rule; use virtual time (`advanceTimeBy`, `advanceUntilIdle`), never real `delay` in tests.

## Verify
StrictMode (`detectAll`) in debug; LeakCanary for leaked scopes; run the module's tests (`./gradlew testDebugUnitTest`); check no collection continues after the screen is stopped.

## Pitfalls
- `mutableStateOf`/StateFlow updated from many threads without `update { }` (lost updates): use `MutableStateFlow.update { it.copy(...) }`.
- Collecting multiple flows in one `launch` sequentially (the second never starts): launch each or `merge`.
- Exposing `MutableStateFlow` publicly.
- Catching exceptions inside `flow { }` builder with `try/emit` violating exception transparency: use `catch` operator.
