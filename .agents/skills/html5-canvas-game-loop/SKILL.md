---
name: html5-canvas-game-loop
description: "Build or fix HTML5 canvas games (arcade, maze, platformer, Tomb of the Mask style runners): fixed-timestep game loop, input for keyboard/touch/swipe, tile maps and collision, sprites and animation, DPR-correct rendering, audio unlock, game state machine, save data, performance and mobile controls. Use when the user wants a browser game, a canvas animation, or a game feels janky, laggy or breaks on mobile."
domain: web
---

# HTML5 canvas game loop

## Core loop: fixed update, variable render
```js
const STEP = 1000 / 60; let last = performance.now(), acc = 0, rafId = 0;
function frame(now) {
  acc += Math.min(now - last, 250);          // clamp after tab was hidden
  last = now;
  while (acc >= STEP) { update(STEP / 1000); acc -= STEP; }   // deterministic physics
  render(acc / STEP);                         // alpha for interpolation
  rafId = requestAnimationFrame(frame);
}
document.addEventListener('visibilitychange', () => { if (document.hidden) { cancelAnimationFrame(rafId); } else { last = performance.now(); rafId = requestAnimationFrame(frame); } });
rafId = requestAnimationFrame(frame);
```
Never tie game speed to frame rate (60/120/144 Hz screens), never use `setInterval` for rendering.

## Crisp canvas on every screen
```js
function fit(canvas, logicalW, logicalH) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);          // cap to protect fill rate
  const scale = Math.min(innerWidth / logicalW, innerHeight / logicalH);
  canvas.style.width = logicalW * scale + 'px'; canvas.style.height = logicalH * scale + 'px';
  canvas.width = Math.round(logicalW * scale * dpr); canvas.height = Math.round(logicalH * scale * dpr);
  ctx.setTransform(scale * dpr, 0, 0, scale * dpr, 0, 0);          // draw in logical units
  ctx.imageSmoothingEnabled = false;                              // pixel art
}
addEventListener('resize', () => fit(canvas, 360, 640));
```

## State machine
`boot -> menu -> playing <-> paused -> gameover -> menu`. One `switch(state)` in update and render; transitions only through `setScene(name)` that resets what it owns. Pause on `visibilitychange`/`blur`.

## Input (unify keyboard, touch, gamepad)
- Keyboard: store a `keys` Set on `keydown/keyup`; use `e.code` (layout independent); `preventDefault` for arrows/space; clear on `blur`.
- Swipe controls (grid/maze games): on `touchstart` store x,y; on `touchend` compute dx,dy; direction = dominant axis if distance > ~24 px. Add `touch-action: none` on the canvas to stop scrolling/zoom.
- Pointer Events (`pointerdown/move/up`) cover mouse + touch + pen in one code path.
- On-screen buttons for mobile: >= 56 px, placed in thumb zones, `user-select: none`.
- Buffer input (remember the last swipe for ~100 ms) so the game feels responsive.

## Tile maps and collision
```js
const T = 32, map = [ '#########', '#...o...#', '#.##.##.#', '#########' ];   // # wall, . floor, o coin
const solid = (cx, cy) => map[cy]?.[cx] === '#';
// Grid movement (Tomb of the Mask style): slide until the next tile is solid
function slide(p, dx, dy) { while (!solid(p.cx + dx, p.cy + dy)) { p.cx += dx; p.cy += dy; collect(p); } }
// Free movement: move axis by axis and resolve each separately to avoid tunneling and sticking
function moveX(e, dx) { e.x += dx; if (hitsWall(e)) e.x -= dx; }
function moveY(e, dy) { e.y += dy; if (hitsWall(e)) e.y -= dy; }
```
AABB overlap: `a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y`. Use a spatial grid or tile lookup when entities > ~200.

## Rendering and assets
- Preload images (`Promise.all` of `img.decode()`), show a progress bar; sprite sheets + `drawImage(sheet, sx, sy, sw, sh, dx, dy, dw, dh)`; round draw positions for pixel art.
- Draw order by layers; cache static backgrounds in an offscreen canvas (`OffscreenCanvas` or a hidden canvas) and blit it.
- Particles/effects: object pools, no allocation per frame; cap counts.
- Text: draw with a loaded font (`document.fonts.load`) and cache measurements.

## Audio
Create/resume one `AudioContext` on the first user gesture; short SFX via `AudioBufferSourceNode`, music via `<audio>` or a looped buffer; mute toggle persisted; lower volume on `visibilitychange`.

## Save data
`localStorage` for best score/settings with try/catch (see `html-single-file-app`); store a version number; never trust it (clamp values).

## Difficulty and feel (cheap wins)
Screen shake on impact (decaying offset), coyote time and input buffering for jumps, easing for UI, consistent 60 fps before adding effects, a restart in <= 1 second, deterministic seeds for level generation (`mulberry32(seed)`) so bugs are reproducible.

## Verify
Chrome Performance panel: frame time stable, no GC spikes (flat heap sawtooth); test at 30/60/144 Hz (DevTools FPS throttle or `STEP` experiments), mobile Safari and Chrome Android, rotate device, background/foreground the tab, blocked audio autoplay, resize mid-game.

## Pitfalls
- Using `Date.now()` deltas without clamping (huge jump after tab switch teleports the player).
- Forgetting to remove listeners on scene change (double input).
- Scaling the canvas with CSS only (blurry) or ignoring DPR (blurry) or using full 3x DPR (slow).
- Collision after moving both axes at once (corner sticking).
