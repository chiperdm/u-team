---
name: debugging-android-crash-anr
description: "Investigate Android and Flutter crashes and ANRs from logcat, stack traces, Play Vitals and Crashlytics; R8/Flutter symbol deobfuscation; main-thread blocking; lifecycle and process-death bugs. Use for 'app crashes', 'app not responding', crashes only in release builds, OOM, or after a new Android version."
domain: android
---

# Crashes and ANRs

- Get the evidence: `adb logcat -b crash`, full stack trace, device/OS, app version, steps. For release builds upload R8 `mapping.txt` (Play Console / Crashlytics) or deobfuscate with `retrace`; Flutter obfuscated builds need the `--split-debug-info` symbols and `flutter symbolize`.
- **ANR** = main thread blocked ~5 s (input) / broadcast 10 s. Read the thread dump: what is the main thread waiting on? Usual suspects: disk/DB/network on main, lock contention, binder calls, `runBlocking`, huge `onReceive`.
- Enable `StrictMode` in debug to catch disk/network on main.
- Frequent root causes: null from platform channel, lifecycle (using context after destroy), process death and lost state, OOM from large bitmaps, permission revoked at runtime, backgrounded service start restrictions.
- Check frequency and affected versions/devices before deciding severity; fix the root cause, add a test or guard, and verify in the next staged rollout.

## Commands
```bash
adb logcat -b crash -d | tail -80              # last crash buffer
adb shell dumpsys activity exit-info <pkg>     # why the process died (API 30+)
adb bugreport ./bugreport.zip                  # includes ANR traces
adb shell "dumpsys meminfo <pkg>" | head -40
retrace mapping.txt trace.txt                  # R8 deobfuscation
flutter symbolize -i trace.txt -d build/symbols
```

## Verify
Reproduce on a device/emulator with the same API level; confirm the fix with the exact steps; add a regression test or guard; watch crash-free rate during staged rollout (`devops-android-release`).

## Pitfalls
- Fixing the symptom (try/catch) instead of the cause.
- Debugging an obfuscated trace without the matching `mapping.txt`.
- Ignoring `Context` use after the Activity is destroyed and background-start restrictions (Android 12+ foreground service limits).

## Related
`debugging-root-cause`, `kotlin-coroutines-flow` (StrictMode, main-thread), `kotlin-android-background`, `flutter-kotlin-platform-channels`.
