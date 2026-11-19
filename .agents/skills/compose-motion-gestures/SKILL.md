---
name: compose-motion-gestures
description: "Implement motion and gestures in Jetpack Compose: animate*AsState, springs, AnimatedVisibility/AnimatedContent, shared element transitions, Animatable with drag and fling, AnchoredDraggable swipe actions, predictive back, haptics, reduce-motion handling and animation performance. Use for pull/swipe interactions, morphing UI, sliding indicators, bottom sheets, onboarding or any 'make it feel alive' request in Kotlin."
domain: android
---

# Compose motion and gestures

Pair with `kotlin-compose-liquid-glass` for glass press/morph effects and `ui-accessibility` for reduce-motion.

## Pick the right API
| Need | API |
|---|---|
| One value follows state | `animateFloatAsState`, `animateColorAsState`, `animateDpAsState` |
| Several values, one state change | `updateTransition(target)` + `transition.animateX` |
| Appear/disappear | `AnimatedVisibility` (enter/exit), `Crossfade`, `AnimatedContent` (with `transitionSpec`) |
| Shared element between screens/states | `SharedTransitionLayout` + `Modifier.sharedElement/sharedBounds` (+ `AnimatedContent`/`NavHost` scope) |
| Imperative, interruptible, gesture-driven | `Animatable` in a coroutine |
| Swipe to dismiss/reveal, sheets | `AnchoredDraggable` (or `SwipeToDismissBox`, `ModalBottomSheet`) |
| Looping | `rememberInfiniteTransition` |
Shared element APIs matured recently: check the Compose version in the project.

## Specs
- `spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessMedium)` for interactive, interruptible motion (preferred default); `tween(300, easing = FastOutSlowInEasing)` for fixed-duration fades/slides.
- Durations: 100-150 ms micro feedback, 200-300 ms enter/exit, 300-500 ms large transitions.

## Draw-phase animation (no recomposition per frame)
```kotlin
val scale by animateFloatAsState(if (pressed) 1.04f else 1f, spring(0.6f, 400f), label = "press")
Box(Modifier.graphicsLayer { scaleX = scale; scaleY = scale })     // lambda form: read in draw phase
```

## Draggable with fling (interruptible)
```kotlin
val offsetX = remember { Animatable(0f) }
Modifier.pointerInput(Unit) {
    val decay = splineBasedDecay<Float>(this)
    coroutineScope {
        while (true) {
            val pointerId = awaitPointerEventScope { awaitFirstDown().id }
            offsetX.stop()
            val tracker = VelocityTracker()
            awaitPointerEventScope {
                horizontalDrag(pointerId) { change ->
                    launch { offsetX.snapTo(offsetX.value + change.positionChange().x) }
                    tracker.addPosition(change.uptimeMillis, change.position)
                    change.consume()
                }
            }
            val velocity = tracker.calculateVelocity().x
            val target = decay.calculateTargetValue(offsetX.value, velocity)
            launch { if (abs(target) > threshold) offsetX.animateDecay(velocity, decay) else offsetX.animateTo(0f, spring()) }
        }
    }
}.offset { IntOffset(offsetX.value.roundToInt(), 0) }
```
Prefer `Modifier.draggable`/`AnchoredDraggable` when anchors are enough; hand-rolled `pointerInput` for custom physics.

## Sliding indicator (bottom bar / tabs)
Measure tab positions with `onGloballyPositioned`, animate `indicatorX` and `indicatorWidth` with a spring, draw the indicator in `drawBehind`. Keep the indicator one composable so it can be a glass lens.

## Predictive back and system gestures
`android:enableOnBackInvokedCallback="true"`; `PredictiveBackHandler { progress -> ... }` to scale/translate the screen with back progress; navigation libraries provide default predictive transitions in recent versions. Don't block system edge-swipe zones (`systemGestureExclusionRects` only when truly needed).

## Haptics and feedback
`LocalHapticFeedback.current.performHapticFeedback(HapticFeedbackType.LongPress)` for long-press/selection; keep subtle, one per gesture; respect system haptics settings.

## Reduce motion
```kotlin
val reduce = remember { Settings.Global.getFloat(ctx.contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) == 0f }
val spec: AnimationSpec<Float> = if (reduce) snap() else spring()
```
Replace large movement with fades; keep state changes obvious without motion.

## Performance
Animate `graphicsLayer` properties (alpha, scale, translation, rotation) rather than layout (`size`, `padding`); keep animated subtrees small; avoid animating `Modifier.blur` radius; don't animate in a `LazyColumn` item without `Modifier.animateItem()`/stable keys; test with Perfetto/Macrobenchmark `FrameTimingMetric`.

## Verify
Interrupt every animation mid-flight (tap twice, back during transition); rotate the device mid-animation; set animator duration scale to 0 and 5 in Developer options; record p95 frame time.

## Pitfalls
- Launching a new animation on every recomposition (use keys / `LaunchedEffect`).
- `animateContentSize` with unbounded text causes jumpy layout.
- Gesture detectors consuming events that a parent scroll needs: check `consume()` usage and `nestedScroll`.
- Different spring per element making the UI feel incoherent: define motion tokens.
