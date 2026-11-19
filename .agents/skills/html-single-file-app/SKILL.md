---
name: html-single-file-app
description: "Build or fix self-contained single-file HTML apps (messenger prototypes, marketplaces, calculators, trackers, tools) with vanilla JS: state and render pattern, localStorage/IndexedDB persistence with safe fallbacks, Web Audio unlock, MediaRecorder voice, PWA manifest/service worker, import/export, security and size discipline. Use when the user wants one .html file that runs by double-click, a quick app or prototype, or to improve an existing single-file project."
domain: web
---

# Single-file HTML apps

One `.html`, no build, no server needed (unless a backend is the point). Fast to ship and share; discipline keeps it from becoming spaghetti.

## File layout (top to bottom)
1. `<head>`: meta, `<style>` with tokens (`design-system-tokens`), base, components.
2. `<body>`: static shell and templates (`<template id="msg-tpl">`).
3. `<script>`: `// config` -> `// state` -> `// storage` -> `// actions (pure-ish)` -> `// render` -> `// events` -> `// init`. Use `"use strict"` and a single namespace/IIFE; no globals leaking.

## State + render pattern (no framework)
```js
const state = { chats: [], activeId: null, draft: '' };
const listeners = new Set();
function setState(patch) { Object.assign(state, patch); save(); queueRender(); }
let raf = 0; const queueRender = () => raf || (raf = requestAnimationFrame(() => { raf = 0; render(); }));
function render() { /* update DOM from state; keyed updates for lists, never innerHTML with user text */ }
// event delegation: one listener per container
list.addEventListener('click', (e) => { const li = e.target.closest('[data-id]'); if (li) openChat(li.dataset.id); });
```
Safe text: `el.textContent = userText`. If HTML is unavoidable, build nodes with `createElement`; never `innerHTML` with user data (XSS, see `security-injection-xss`).

## Persistence
- `localStorage` for small settings (<~5 MB total). Always guard: private mode or quota can throw.
```js
const store = { get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch { return d; } },
                set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch { return false; } } };
```
- Versioned schema: `{ v: 3, ... }` plus a `migrate(data)` function; never crash on old data.
- Bigger data (messages, media, files): IndexedDB (wrap with a tiny promise helper or the `idb` library). Debounce writes (300-500 ms).
- Provide Export/Import JSON buttons and a "reset data" action; tell the user where data lives (this browser only).
- Never store passwords/tokens in plain localStorage if the file talks to a real backend: prefer httpOnly cookies from the server, or at least short-lived tokens.

## Browser features that need care
- **Web Audio / sounds:** an `AudioContext` starts suspended; create/resume it inside the first user gesture (`click`/`touchend`). Preload short sounds with `decodeAudioData`; keep a mute setting.
- **Voice messages (MediaRecorder):** requires HTTPS or `localhost` plus mic permission. Choose a supported mime: `MediaRecorder.isTypeSupported('audio/webm;codecs=opus')`, else `audio/mp4` (Safari). Stop all tracks (`stream.getTracks().forEach(t => t.stop())`) when done; handle permission denial with a clear message.
- **Clipboard, share, notifications:** feature-detect (`navigator.share`, `Notification`), degrade gracefully.
- **Files:** `<input type=file accept=...>` + `FileReader`/`URL.createObjectURL` (revoke URLs); validate size/type.
- **Dynamic Island / Material You styling:** pure CSS (`env(safe-area-inset-*)`, rounded pills, spring transitions); keep it optional.

## Backend-connected apps (e.g. Supabase)
Keep config in one `CONFIG` object at the top; public anon keys only (RLS protects data, see `database-rls-supabase`); never embed `service_role`. Handle offline/failed requests with visible state and retry. A reserve backend = ordered list of endpoints with health-check failover (`supabase-realtime-storage`).

## PWA (installable, offline shell)
```html
<link rel="manifest" href="manifest.webmanifest">  <!-- needs a real file + icons 192/512; a service worker needs HTTPS or localhost -->
```
A true single file cannot register a service worker from `file://`; say so. For a hosted app: `manifest.webmanifest`, `sw.js` (cache-first for the shell, network-first for API), `display: standalone`, `theme_color`.

## Size and quality discipline
- Past ~1500 lines, split sections with clear banners or move to `index.html + app.js + styles.css`; still no build step needed.
- No dead code, no duplicate functions; consistent naming; comments for why, not what.
- Accessibility: real `<button>`, labels, focus states, `aria-live="polite"` for new messages, contrast, reduced motion.
- Mobile first: `viewport-fit=cover`, 44 px targets, `100dvh` layouts, keyboard-safe composer (`visualViewport` resize handling).

## Verify
Open from disk and from a local server (`python3 -m http.server`); test with storage cleared, with storage blocked, offline, at 360 px width, in Chrome and Safari; check the console is empty; run the file through `node --check` on the extracted script if there is no browser.

## Pitfalls
- Inline `onclick="..."` strings quickly break with quotes and CSP; use `addEventListener`.
- Forgetting `autocomplete`/`inputmode`, so mobile keyboards are wrong.
- `Date.now()` as an id collides; use `crypto.randomUUID()`.
- Silent `catch {}` hides real failures: log in dev and show a user-facing error.
