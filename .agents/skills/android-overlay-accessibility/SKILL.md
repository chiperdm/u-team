---
name: android-overlay-accessibility
description: "Implement Android system overlays (HUD, floating bubble, assistant orb) with SYSTEM_ALERT_WINDOW and WindowManager, Compose inside a service overlay (lifecycle/saved-state owners), touch-through rules, and AccessibilityService for cross-app actions: manifest and config, global actions, gestures, node actions, Play policy and security. Use for floating windows, always-on-top UI, auto-tap/phone-control features, or 'ViewTreeLifecycleOwner not found' crashes."
domain: android
---

# Overlays and AccessibilityService

High-risk, high-privilege features: security review (`security-auditor`) before release; minimal power; clear user consent.

## Overlay window (HUD / bubble)
Permission: `<uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>`; the user grants it in Settings.
```kotlin
fun Context.canOverlay() = Settings.canDrawOverlays(this)
fun Activity.requestOverlay() = startActivity(
    Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName")))

val lp = WindowManager.LayoutParams(
    WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT,
    WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,                 // API 26+
    WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
    WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN or
    WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
    PixelFormat.TRANSLUCENT).apply { gravity = Gravity.TOP or Gravity.START; x = 24; y = 200 }
wm.addView(view, lp)                      // must be removed: wm.removeView(view) in onDestroy
```
- Host the overlay in a **foreground service** (notification required) so it survives; remove the view in `onDestroy` and on permission loss.
- Flags: `FLAG_NOT_FOCUSABLE` lets the keyboard/back go to the app below; remove it only for a text input overlay (and then set `softInputMode`). `FLAG_NOT_TOUCHABLE` = purely visual HUD.
- Android 12+ limits touch pass-through for overlays covering other apps (untrusted touch rules: obscuring windows with high opacity block touches): keep click-through HUD windows semi-transparent (`lp.alpha` <= 0.8) and test on API 31+.
- Draggable bubble: update `lp.x/y` in a touch listener and call `wm.updateViewLayout(view, lp)`; snap to edges with `ValueAnimator`; respect cutouts/insets (`WindowMetrics`).
- Don't show over the lock screen or sensitive screens unless intended; some apps/OEMs hide overlays (banking apps use `setHideOverlayWindows`).

## Compose inside a service overlay
`ComposeView` needs lifecycle, saved-state and ViewModel store owners on its view tree, or it crashes with `ViewTreeLifecycleOwner not found`:
```kotlin
class OverlayOwner : LifecycleOwner, SavedStateRegistryOwner, ViewModelStoreOwner {
    private val reg = LifecycleRegistry(this)
    private val ssc = SavedStateRegistryController.create(this)
    override val lifecycle: Lifecycle get() = reg
    override val savedStateRegistry: SavedStateRegistry get() = ssc.savedStateRegistry
    override val viewModelStore = ViewModelStore()
    fun start() { ssc.performAttach(); ssc.performRestore(null); reg.currentState = Lifecycle.State.RESUMED }
    fun stop() { reg.currentState = Lifecycle.State.DESTROYED; viewModelStore.clear() }
}
val owner = OverlayOwner().also { it.start() }
val view = ComposeView(ctx).apply {
    setViewTreeLifecycleOwner(owner); setViewTreeSavedStateRegistryOwner(owner); setViewTreeViewModelStoreOwner(owner)
    setContent { HudContent(state) }
}
```
(Samples follow the documented shapes, not compiled here: compile and run on a device. `performAttach()` is needed on some lifecycle versions only.) Feed the HUD from a `StateFlow` held by the service; no Activity-scoped ViewModels. For glass HUDs see `kotlin-compose-liquid-glass` (note: backdrop of an overlay window is the other app, which you cannot read; use a tinted/opaque HUD or `FLAG_BLUR_BEHIND`-style window blur where supported).

## AccessibilityService (last resort for cross-app control)
Manifest:
```xml
<service android:name=".AssistA11yService" android:exported="true"
         android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
  <intent-filter><action android:name="android.accessibilityservice.AccessibilityService"/></intent-filter>
  <meta-data android:name="android.accessibilityservice" android:resource="@xml/a11y_config"/>
</service>
```
`res/xml/a11y_config.xml`:
```xml
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:canRetrieveWindowContent="true"
    android:canPerformGestures="true"
    android:notificationTimeout="100"
    android:description="@string/a11y_description"/>
```
Capabilities: `performGlobalAction(GLOBAL_ACTION_BACK | HOME | RECENTS | NOTIFICATIONS | QUICK_SETTINGS | LOCK_SCREEN | TAKE_SCREENSHOT)`; `rootInActiveWindow` -> `findAccessibilityNodeInfosByText/ViewId` -> `performAction(ACTION_CLICK / ACTION_SET_TEXT / ACTION_SCROLL_FORWARD)`; `dispatchGesture(GestureDescription, callback, null)` for taps/swipes at coordinates.
Practices:
- Prefer node actions (semantic) over coordinate gestures; wait for the expected window/content change (event-driven, with timeout) instead of fixed sleeps; recycle/handle stale nodes (`refresh()`).
- Process events off the main thread; filter by package; keep `notificationTimeout` sensible; don't hold references to nodes.
- **Never read or log password fields** (`node.isPassword`), OTP codes, banking or other sensitive app content; don't store screen text; don't send it off-device without explicit, informed consent.
- A cross-app action runner must have: allowlist of target apps/actions, explicit user confirmation for destructive/financial steps, a visible "stop" control, rate limits, and an audit trail without content.
- Users must enable the service manually in Settings. On Android 13+, apps installed outside a store show "restricted setting": the user must allow restricted settings in App info first; guide them with screenshots/text. Detect enablement with `Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES` and deep-link to `Settings.ACTION_ACCESSIBILITY_SETTINGS`.
- **Google Play policy:** the AccessibilityService API is intended for accessibility; non-accessibility use requires a Play Console declaration, prominent in-app disclosure and consent, and may be rejected. Read the current policy before planning Play distribution; sideloaded/OTA distribution has its own legal and security responsibilities.

## Alternatives that need less trust
Intents and public APIs (`android-voice-assistant` list), `NotificationListenerService` (read/dismiss notifications with user opt-in), `MediaSession`, `UsageStatsManager`, `Shizuku`-style ADB-level access (power users only; do not depend on it), device owner APIs for managed devices.

## Verify
Test: permission denied/revoked, service killed, screen off/locked, rotation, split-screen, different OEMs (MIUI/One UI/ColorOS kill overlay services), Android 12-14 touch behavior; leak check (view removed on destroy); security checklist: no sensitive text captured, confirmation gates present, exported component settings correct (`android:exported`, permission protections).

## Pitfalls
- Adding the same overlay view twice (crash `already added`): keep a nullable reference.
- Overlay without foreground service gets killed.
- Using coordinates from one device on another (use node bounds, density-independent logic).
- Exported service without the bind permission.
- Assuming the Accessibility service stays enabled after app updates/force stops.
