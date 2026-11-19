---
name: kotlin-android-background
description: "Choose and implement Android background work correctly: WorkManager, foreground services and their types, FCM, notifications and channels, Doze/App Standby, exact alarms, permission rules for Android 12-14. Use for sync, uploads, reminders, push handling, services killed in background, or 'notifications not showing' bugs."
domain: android
---

# Android background work

- **Deferrable + guaranteed** (sync, upload retry): WorkManager with constraints (network), `BackoffPolicy.EXPONENTIAL`, unique work (`enqueueUniqueWork(name, KEEP/REPLACE, req)`). Expedited work is quota-limited.
- **User-visible ongoing** (call, location, active upload): foreground service. Android 14+ requires a declared `foregroundServiceType` in the manifest plus the matching permission; also check start restrictions from background.
- **Incoming chat message while app is closed:** FCM high-priority message; handle in `FirebaseMessagingService`, keep work short, hand off to WorkManager for heavy parts. Do not keep your own always-on socket in the background.
- Exact alarms are restricted on recent Android versions; prefer inexact/WorkManager unless it is a true alarm/calendar feature.
- Notifications: create channels (importance per channel), request `POST_NOTIFICATIONS` at runtime on Android 13+ at a sensible moment, group by chat, don't expose message content on the lock screen for private chats.
- Doze/App Standby delay non-FCM work; test with `adb shell dumpsys deviceidle force-idle`.
- Battery: batch work, avoid wake locks, check Android Vitals.
- Test on real devices of several vendors (aggressive OEM battery managers kill background apps).

## Foreground service types (Android 14+)
Declare `android:foregroundServiceType` per service and the matching `FOREGROUND_SERVICE_<TYPE>` permission (`dataSync`, `mediaPlayback`, `microphone`, `location`, `phoneCall`, `specialUse`, ...). Start from a user-visible context; `startForeground()` within ~5 s of `startForegroundService()`. Microphone/camera types cannot be started from the background in most cases (`android-voice-assistant`).

## Notification essentials
```kotlin
val ch = NotificationChannel("messages", "Messages", NotificationManager.IMPORTANCE_HIGH)
getSystemService(NotificationManager::class.java).createNotificationChannel(ch)
// Android 13+: request POST_NOTIFICATIONS at a sensible moment; handle denial gracefully
```
Group per chat (`setGroup`, summary notification), `MessagingStyle` for chat, direct reply action with `RemoteInput`, mark-read action, hide content on the lock screen for private chats (`setVisibility(VISIBILITY_PRIVATE)`).

## Verify
```bash
adb shell dumpsys deviceidle force-idle      # Doze
adb shell am set-standby-bucket <pkg> rare   # App Standby bucket
adb shell dumpsys jobscheduler | grep <pkg>  # WorkManager jobs
```
Test: app swiped away, device idle overnight, battery saver, per-vendor battery managers, notification permission denied.

## Pitfalls
- Own always-on socket in the background (battery drain, killed by OEMs): use FCM + fetch.
- `SCHEDULE_EXACT_ALARM` for non-alarm features.
- Long work inside `FirebaseMessagingService.onMessageReceived` (hand off to WorkManager).

## Related
`android-voice-assistant`, `android-overlay-accessibility`, `kotlin-coroutines-flow`, `firebase-rules-auth` (FCM), `android-architecture-room`.
