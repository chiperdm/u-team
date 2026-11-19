---
name: flutter-kotlin-platform-channels
description: "Bridge Flutter and native Android (Kotlin) safely: MethodChannel, EventChannel, Pigeon type-safe APIs, threading, error contracts, plugin vs app-level code, ActivityAware lifecycle, background isolates, versioned channel names and tests on both sides. Use when adding native features to a Flutter app (biometrics, services, notifications, sensors, overlays) or debugging MissingPluginException and channel crashes."
domain: flutter
---

# Flutter <-> Kotlin platform channels

Keep channel contracts stable (`kotlin-engineer` owns the Kotlin side, `flutter-engineer` the Dart side; agree the contract first).

## Choose the mechanism
| Need | Use |
|---|---|
| Request/response call | `MethodChannel` |
| Continuous stream (sensor, connection state, download progress) | `EventChannel` |
| Many typed calls, long-lived API | **Pigeon** (generates Dart + Kotlin, compile-time checked) |
| Reusable across apps | a federated plugin package |
| Heavy native library calls | consider FFI/JNI binding generators if the project already uses them |

## Contract first (write it down in the ADR or PR)
- Channel name: `com.company.app/feature` (versioned if breaking: `.../feature.v2`).
- Methods: name, argument map (types, nullability), result type, error codes.
- Errors: `result.error("CODE", "message", details)` -> `PlatformException(code, message, details)`; codes are stable strings (`PERMISSION_DENIED`, `UNAVAILABLE`), never raw stack traces.

## Kotlin side
```kotlin
class MainActivity : FlutterActivity() {         // FlutterFragmentActivity if you need BiometricPrompt / fragments
    override fun configureFlutterEngine(engine: FlutterEngine) {
        super.configureFlutterEngine(engine)
        val ch = MethodChannel(engine.dartExecutor.binaryMessenger, "com.example.app/device")
        ch.setMethodCallHandler { call, result ->
            when (call.method) {
                "batteryLevel" -> result.success(readBattery())
                "startHud" -> {
                    val opacity = call.argument<Double>("opacity") ?: run { result.error("BAD_ARGS", "opacity missing", null); return@setMethodCallHandler }
                    scope.launch { runCatching { hud.start(opacity) }
                        .onSuccess { result.success(null) }
                        .onFailure { result.error("UNAVAILABLE", it.message, null) } }
                }
                else -> result.notImplemented()
            }
        }
    }
}
```
- Handlers run on the **main thread**: do I/O and CPU work on a background dispatcher, then call `result.success/error` **exactly once** (a second call crashes), from any thread is allowed for `MethodChannel.Result` in current Flutter, but keep it simple and reply once.
- Never block waiting for Dart from the main thread.
- Large payloads: pass file paths or use `ByteArray` (`Uint8List` on Dart), never big base64 strings.

## EventChannel
```kotlin
EventChannel(messenger, "com.example.app/connection").setStreamHandler(object : EventChannel.StreamHandler {
    private var job: Job? = null
    override fun onListen(args: Any?, sink: EventChannel.EventSink) {
        job = scope.launch { connectionFlow.collect { withContext(Dispatchers.Main) { sink.success(it.name) } } }
    }
    override fun onCancel(args: Any?) { job?.cancel() }       // always clean up
})
```
Dart: `const EventChannel('...').receiveBroadcastStream().listen(...)`; cancel the subscription in `dispose()`.

## Dart side
```dart
class DeviceApi {
  static const _ch = MethodChannel('com.example.app/device');
  Future<int?> batteryLevel() async {
    try { return await _ch.invokeMethod<int>('batteryLevel'); }
    on PlatformException catch (e) { throw DeviceException(e.code, e.message); }
    on MissingPluginException { return null; }                 // web/desktop/tests: degrade gracefully
  }
}
```
Wrap channels in a small typed Dart class; UI never calls `invokeMethod` directly. Guard with `defaultTargetPlatform == TargetPlatform.android` where relevant.

## Pigeon (recommended for > 3 methods)
Define `pigeons/device_api.dart` with `@HostApi()` / `@FlutterApi()` abstract classes and data classes, run `dart run pigeon --input pigeons/device_api.dart`, implement the generated Kotlin interface. Commit generated files; re-generate in CI to detect drift.

## Lifecycle and background
- App-level code: `configureFlutterEngine`. Plugins: implement `FlutterPlugin` (+ `ActivityAware` to get the `Activity`, `ActivityResultListener` for `onActivityResult`/permissions).
- Background services (`kotlin-android-background`) that call into Dart need their own `FlutterEngine`/isolate; in background isolates call `BackgroundIsolateBinaryMessenger.ensureInitialized(token)` before using plugins. Prefer doing background work natively and syncing state through storage.
- Permissions: request from the Activity (`ActivityCompat.requestPermissions`/Activity Result API), map results to error codes; don't assume granted.

## Tests
- Dart: `TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger.setMockMethodCallHandler(channel, (call) async => ...)`.
- Kotlin: unit-test the handler logic by extracting it into a class that takes plain args/returns results; instrumented tests for real integration.
- Contract test: a list of method names/args kept in one doc, checked in both test suites.

## Debug recipes
- `MissingPluginException`: channel name typo, handler registered after the call, handler not registered in the engine used (background engine!), hot-restart vs full rebuild after native change, plugin not in `pubspec`/ not registered (`GeneratedPluginRegistrant`).
- `Reply already submitted`: `result` called twice.
- `PlatformException(null-error)`: Kotlin exception thrown inside the handler without catching; wrap and map.
- Works in debug, crashes in release: R8 stripped a class used by reflection: add keep rules.

## Verify
Run on a real device: call every method happy path + permission denied + native exception; `flutter analyze`, `flutter test`, `./gradlew :app:assembleDebug` (from `android/`); check logcat for channel errors.

## Pitfalls
- Passing non-standard types (custom classes) without codec support.
- Long synchronous native work on main thread -> ANR (`debugging-android-crash-anr`).
- Leaking the `Activity` in a static/singleton handler.
- Changing a channel's arguments without versioning (older Dart code in cached hot-restart state or older app version talking to new native).
