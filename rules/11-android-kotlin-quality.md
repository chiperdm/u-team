# Android / Kotlin Quality Standard
- Structured concurrency only: no `GlobalScope`, no `runBlocking` on the main thread, injected dispatchers, cancellation respected.
- Lifecycle-aware collection (`collectAsStateWithLifecycle`, `repeatOnLifecycle`).
- State hoisting in Compose; one immutable UiState per screen; business logic outside composables.
- Manifest hygiene: minimal permissions, `android:exported` explicit, foreground service types declared (Android 14+), backup rules decided.
- Dangerous capabilities (microphone, overlay, accessibility, call/SMS) require a written capability list, consent UI, kill switch and confirmation gates.
- Room: exported schemas, migrations tested from every released version, no destructive fallback for user data.
- Sensitive data: Keystore-wrapped keys, no secrets in logs, `FLAG_SECURE` where appropriate.
- R8/minify on in release; keep rules tested; crash reporting symbols uploaded.
- Compose/AGSL/GraphicsLayer samples must be compiled and run on a device before being reported as working.
