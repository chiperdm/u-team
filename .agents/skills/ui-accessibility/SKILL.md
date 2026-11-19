---
name: ui-accessibility
description: "Check and fix accessibility for mobile and web UI (Flutter, Compose, HTML): semantics and labels, contrast, touch targets, text scaling, focus and keyboard, reduced motion/transparency, screen readers (TalkBack/VoiceOver), forms and live regions. Use for any UI review, WCAG questions, 'is it accessible?', glass/blur contrast, or before shipping screens."
domain: ui
---

# Accessibility

- Touch targets >= 48x48 dp (Android) / 44x44 pt (iOS); spacing between adjacent targets.
- Contrast: text 4.5:1 (3:1 for large text and UI icons/borders). Never rely on color alone (add icon/text for status).
- Every interactive/image element has a label (`Semantics(label:)`, `contentDescription`, `alt`). Decorative items are excluded from semantics.
- Support text scale up to 200%: no fixed-height text containers, test layout overflow.
- Respect reduce-motion / disable-animations; no autoplay motion that cannot be paused.
- Logical focus/traversal order; visible focus state; full keyboard operation on web/desktop.
- Announce important dynamic changes (new message, error) via live regions / `SemanticsService.announce`, without spamming.
- Test with TalkBack / VoiceOver on a real device, large text, and dark/light themes.

## Platform snippets
```dart
// Flutter
Semantics(label: 'Send message', button: true, child: IconButton(icon: const Icon(Icons.send), onPressed: send));
ExcludeSemantics(child: decorativeImage);
SemanticsService.announce('New message from Aigerim', TextDirection.ltr);
```
```kotlin
// Compose
Icon(Icons.Default.Send, contentDescription = "Send message")
Row(Modifier.semantics(mergeDescendants = true) { }) { /* grouped row read as one item */ }
Modifier.minimumInteractiveComponentSize()
```
```html
<!-- Web -->
<button aria-label="Send message"><svg aria-hidden="true">...</svg></button>
<div role="status" aria-live="polite" id="live"></div>
<style>@media (prefers-reduced-motion: reduce){*{animation:none!important;transition:none!important}}</style>
```

## Glass and transparency
Provide an opaque or high-contrast alternative when the user enables reduce transparency/high contrast (CSS `prefers-reduced-transparency`/`prefers-contrast`, Flutter `MediaQuery.highContrastOf`, your own setting on Android); text over blurred imagery needs tint/scrim to hold 4.5:1.

## Automated checks
Flutter `meetsGuideline(...)` (`flutter-testing`); Android Accessibility Scanner and Espresso/Compose accessibility checks; Lighthouse/axe DevTools for web. Then manually test with TalkBack/VoiceOver, keyboard only, 200% text, grayscale.

## Pitfalls
Placeholder text as the only label; color-only error states; focus traps in dialogs; tiny close buttons on glass overlays; auto-advancing carousels.

## Verify
Automated guideline checks pass; TalkBack/VoiceOver walkthrough of the main flow completed; keyboard-only run on web; 200% text and high-contrast screenshots attached; any item not run is listed as "not run".

## Related
`ui-design-review`, `ui-glassmorphism`, `kotlin-compose-foundations`, `html-site-builder`, `localization-flutter`.
