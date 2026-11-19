---
name: flutter-chat-ui
description: "Build or review a chat message screen in Flutter: reversed list, cursor pagination, optimistic send states, scroll behavior, keyboard/composer, receipts, typing indicators, bubble layout, attachments and voice-message UI. Use for any chat screen work, scroll jumps when messages arrive, duplicated bubbles, or keyboard overlap issues."
domain: flutter
---

# Chat UI

- `ListView.builder(reverse: true)` so the newest message is at the bottom and keyboard/insets behave. Newest-first data order.
- **Pagination:** load older messages by cursor when scrolled near the end (e.g. 5 items left); keep scroll position when prepending; show a loading row, not a full-screen spinner.
- **Message state machine:** `sending -> sent -> delivered -> read`, plus `failed` with a retry button. Create the message locally with `clientMsgId`, render immediately, reconcile with the server echo by that id (never duplicate).
- Auto-scroll to bottom only if the user is already near the bottom; otherwise show a "new messages" chip.
- Group consecutive messages from one sender; date separators; consistent bubble max width (~75-80%) that survives large text scale.
- Typing indicator: throttle sending (e.g. once per 3 s) and auto-expire on the receiver.
- Read receipts: batch ("read up to message X") instead of one event per message.
- Keyboard: `resizeToAvoidBottomInset`, `MediaQuery.viewInsetsOf`; test with long text, RTL, emoji, links, very long single words.
- Accessibility: Semantics per bubble (sender, text, time, status).

## Composer and attachments
- Composer: `TextField` with `maxLines: null` capped by `ConstrainedBox`, `textInputAction: newline`, `keyboardType: TextInputType.multiline`, `enableSuggestions` per locale; send button disabled when empty/whitespace; trim before send.
- Draft persistence per chat (local DB) so rotation/kill does not lose text.
- Attachments: show a local preview immediately with upload progress and cancel/retry; keep the message in `sending` until the media upload and the message record are both confirmed (`api-idempotency`).
- Voice messages: hold-to-record with slide-to-cancel, min length (~0.5-1 s), waveform from amplitude samples, max duration, playback speed, one player at a time, release the recorder on dispose.
- Replies/quotes, reactions, edit, delete: keep the state machine and ids stable (`edited_at`, tombstones for deletes so other devices converge).

## Verify
Widget tests for: send success/failure/retry; paginate older; incoming message while scrolled up shows the chip; duplicate server echo does not duplicate the bubble (`flutter-testing`). Manual: very long message, RTL text, emoji/ZWJ sequences, large font scale, landscape, slow network.

## Pitfalls
- Using `shrinkWrap: true` for the message list.
- Rebuilding the whole list on every typing tick (scope the composer state).
- Scrolling to bottom after images load (layout shifts): reserve image aspect ratios.

## Related
`flutter-state-management`, `flutter-offline-first`, `realtime-reconnect-client`, `flutter-performance-jank`, `ui-accessibility`, `flutter-liquid-glass`.
