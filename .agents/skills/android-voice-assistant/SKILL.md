---
name: android-voice-assistant
description: "Design and build a native Android voice assistant: wake word / voice activation, speech recognition (SpeechRecognizer, on-device), microphone foreground service rules on Android 12-14, TTS and barge-in, audio focus, latency pipeline (ASR -> LLM -> TTS), phone-control actions via Intents, state machine, battery and privacy. Use for any 'assistant', 'voice command', 'say hey X', or hands-free feature in a Kotlin app."
domain: android
---

# Android voice assistant

Pair with `llm-integration-safety` (model calls, confirmations), `android-overlay-accessibility` (HUD, phone control), `kotlin-android-background` (services), `kotlin-coroutines-flow`.

## Architecture
```
Mic (AudioRecord) -> Wake word -> VAD/endpointing -> ASR -> Intent/LLM -> Action executor (confirm) -> TTS
        ^________________ audio focus + barge-in + state machine ________________|
```
State machine (single source of truth, `StateFlow`): `Idle -> WakeListening -> Listening -> Thinking -> Acting -> Speaking -> Idle` (+ `Error`). Every transition logged (without user content). Cancel everything on a new wake event or user tap.

## Voice activation options
- **Default assistant role** (`VoiceInteractionService` + `RoleManager.ROLE_ASSISTANT`): user sets the app as the digital assistant; launched by the assist gesture/button; best system integration, no always-on mic needed.
- **In-app/foreground-service wake word** with an on-device engine: commercial SDKs (e.g. Picovoice Porcupine: needs an AccessKey/licence, custom words), open models (openWakeWord/TFLite ports, Vosk keyword grammar). Evaluate licence, accuracy, CPU/battery, languages (Russian/Kazakh wake words need custom training), and false accept/reject rates on real audio.
- System always-on hotword APIs are privileged for OEM/system apps: don't plan around them.

## Microphone and foreground service rules (verify against current docs)
- `RECORD_AUDIO` runtime permission first; explain why before asking.
- Continuous listening needs a **foreground service** with `android:foregroundServiceType="microphone"` and, on Android 14+ (API 34), the `FOREGROUND_SERVICE_MICROPHONE` permission; start it while the app is visible/user-initiated. Since Android 11/12, **starting a microphone foreground service from the background is restricted** (exemptions are narrow): design the start flow around an explicit user action (tap, notification action, assistant role launch).
- Android 12+ shows a mic privacy indicator; it cannot be hidden. Show your own persistent notification with a "Stop listening" action.
- Doze/OEM battery managers kill services: guide users to exempt the app, handle `onTaskRemoved`, restart carefully (no infinite restart loops), and measure battery drain (Battery Historian / Android Vitals).

## Speech recognition
- `SpeechRecognizer.createSpeechRecognizer(ctx)` (Google service; may need network); `SpeechRecognizer.createOnDeviceSpeechRecognizer(ctx)` on API 33+ when `isOnDeviceRecognitionAvailable`. Use `RecognizerIntent.EXTRA_PARTIAL_RESULTS`, `EXTRA_LANGUAGE`, `EXTRA_PREFER_OFFLINE`. Handle `ERROR_NO_MATCH`, `ERROR_SPEECH_TIMEOUT`, `ERROR_RECOGNIZER_BUSY` (destroy + recreate, with delay), `ERROR_INSUFFICIENT_PERMISSIONS`.
- It must be created and called on the main thread. Recognizer start may play a beep on some devices.
- Offline/custom: Vosk or a Whisper-class model via a native runtime; mind model size (ship as an on-demand download), RAM and latency on mid-range phones.
- Own `AudioRecord` pipeline (when using your own ASR/wake engine): `AudioSource.VOICE_RECOGNITION` (or `VOICE_COMMUNICATION` for built-in AEC), 16 kHz mono PCM16, read on a dedicated thread, ring buffer, release in `finally`. Add `AcousticEchoCanceler`/`NoiseSuppressor` where available so the assistant does not hear itself.

## TTS and barge-in
- `TextToSpeech` with `UtteranceProgressListener`; `speak(text, QUEUE_FLUSH, params, utteranceId)`; check `isLanguageAvailable` (ru/kk voices vary by device/engine; fall back or prompt to install voice data).
- Barge-in: on wake word/VAD during `Speaking`, `tts.stop()` immediately and go to `Listening`.
- Stream LLM output sentence by sentence into TTS (split on punctuation) to cut time-to-first-audio.
- Audio focus: request with `AudioAttributes.USAGE_ASSISTANT` (`AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK` to speak over music); abandon focus when done; handle focus loss. Bluetooth headsets: SCO/communication device routing (`AudioManager.setCommunicationDevice` on API 31+).

## Latency budget (target, measure it)
wake word < 300 ms; end-of-speech detection 400-800 ms; ASR final < 500 ms; LLM first token < 1 s (stream); TTS first audio < 400 ms. Log per-stage timings; optimize the largest one first (`performance-profiling-budgets`).

## Phone-control actions (least power first)
1. **Intents:** `AlarmClock.ACTION_SET_ALARM`/`ACTION_SET_TIMER`, `Intent.ACTION_DIAL` (no permission) vs `ACTION_CALL` (needs `CALL_PHONE`; confirm first), `ACTION_SENDTO` with `smsto:` (opens compose, user sends), `ACTION_VIEW` for maps/web, media keys/`MediaSessionManager` for playback, `Settings` panels (`Settings.Panel.ACTION_INTERNET_CONNECTIVITY`, volume panel). Package visibility on Android 11+: declare `<queries>` for apps you resolve.
2. **APIs with explicit permission:** `CameraManager` torch, `AudioManager` volume/ringer (`ACCESS_NOTIFICATION_POLICY` for DND), `ContactsContract` (read permission), `NotificationListenerService` (user enables it).
3. **AccessibilityService** for cross-app UI actions only as a last resort, with disclosure and strong confirmation (`android-overlay-accessibility`).
Never auto-execute irreversible or costly actions (call, send message, delete, purchase, share location) from a transcript alone: read back and require a confirm (voice "yes" + on-screen button), and rate-limit. Treat audio from TV/other people as untrusted (a spoken command must not trigger a destructive action silently).

## Privacy and safety
- Process locally when possible; tell users what leaves the device (audio vs text) and keep it off by default for sensitive content. Don't store raw audio unless needed, with retention limits; never log transcripts at INFO.
- LLM tool calling: allowlisted tools, arguments validated, no raw model output into shell/Intents without validation (`llm-integration-safety`).
- Kids/accessibility/regional language support is a feature: test with accents, noise and short utterances.

## Verify
Real-device tests: quiet room, noisy room, Bluetooth headset, phone locked, screen off, battery saver, app swiped away, permission revoked mid-session, incoming call (release the mic), music playing. Measure wake false accepts/hour and per-stage latency. `./gradlew :app:lintDebug :app:testDebugUnitTest` for logic (state machine, intent parsing as pure functions).

## Pitfalls
- Re-creating `SpeechRecognizer` on every phrase without destroying the old one (leak, busy errors).
- Two components holding the mic (wake engine + recognizer): hand the mic over explicitly.
- Assuming Google speech services exist (Huawei, custom ROMs, emulators).
- Blocking the main thread with audio processing; unbounded queues of audio frames.
- Forgetting to stop everything in `onDestroy`/`onTaskRemoved`.
