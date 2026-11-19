---
name: kotlin-compose-liquid-glass
description: "Build Liquid Glass (iOS 26 style: backdrop blur + lens refraction + specular rim + tint) in Jetpack Compose or Compose Multiplatform for Android: GraphicsLayer backdrop capture, AGSL RuntimeShader, Haze or backdrop libraries, API-level fallbacks, performance. Use whenever the user mentions liquid glass, glass navigation bar, glass button, frosted or refractive UI, blur behind a panel, or Material 3 with a glass look in Kotlin."
domain: android
---

# Liquid Glass in Jetpack Compose

Liquid Glass is Apple's iOS 26 design language. SwiftUI has it natively (`glassEffect`); **Android has no system equivalent, so you assemble it from layers.** Build it as a token-driven surface (see `rules/03-glassmorphism.md`, `rules/12-liquid-glass.md`), pilot ONE component first, keep an opaque fallback.

## The five layers (what makes it "liquid" and not just frosted)
1. **Backdrop capture:** the pixels behind the element.
2. **Blur + saturation:** weak-to-moderate blur (radius ~4-16 dp) plus ~120-180% saturation (vibrancy).
3. **Refraction (the key difference):** backdrop samples near the rim are displaced like light through a lens; ~0 in the middle, strong in the outer 16-28 px. Optional chromatic dispersion (R/G/B offset slightly differently).
4. **Tint + rim:** 6-14% white (dark UI) or 40-60% (light UI) fill, a 1 dp gradient stroke (bright top-left, faint middle, medium bottom-right = specular highlight), inner shadow, soft outer shadow.
5. **Interaction:** press = slight scale-up + brighter rim, spring animation, shape morph between states.

## Choose the path by API level
| Device API | What works | Result |
|---|---|---|
| 33+ | `RuntimeShader` (AGSL) + `RenderEffect` | full refraction |
| 31-32 | `RenderEffect` blur only (`BlurEffect`, `Modifier.blur`) | blur + tint + rim, no refraction |
| < 31 | no real-time blur | opaque tonal surface (`surfaceContainer`, alpha ~0.92) + rim |
Also force the opaque fallback for: battery saver (`PowerManager.isPowerSaveMode`), a user "reduce transparency" setting you expose, low-RAM devices (`ActivityManager.isLowRamDevice`), and failed frame budget.

## Path A: library (fastest for production)
- **Haze** (chrisbanes/haze): blur, tint, progressive blur, works with Compose Multiplatform.
- **Kyant0 backdrop / AndroidLiquidGlass** style libraries: refraction on top of backdrop capture.
- Before adopting run `dependency-supply-chain` (maintenance, license, min API). **Library APIs changed between versions** (Haze 0.x `haze/hazeChild` vs 1.x `hazeSource/hazeEffect`): read the README of the version you pin, do not write from memory.
```kotlin
// Haze 1.x shape of the API (verify against the pinned version)
val hazeState = remember { HazeState() }
Box(Modifier.fillMaxSize()) {
    Content(Modifier.fillMaxSize().hazeSource(hazeState))
    GlassBar(Modifier.align(Alignment.BottomCenter).hazeEffect(hazeState) {
        blurRadius = 20.dp
        tint = HazeTint(Color.White.copy(alpha = 0.10f))
    })
}
```

## Path B: own implementation (full control, no dependency)
Needs Compose UI 1.7+ (`GraphicsLayer`). Samples below follow the documented API shapes but were **not compiled here**: compile and screenshot on a real API 33+ device.

**1. Record the background into a layer**
```kotlin
@Composable
fun GlassHost(content: @Composable (backdrop: GraphicsLayer, hostOrigin: () -> Offset) -> Unit) {
    val backdrop = rememberGraphicsLayer()
    var origin by remember { mutableStateOf(Offset.Zero) }
    Box(Modifier.fillMaxSize().onGloballyPositioned { origin = it.positionInRoot() }) {
        content(backdrop) { origin }
    }
}
// background composable:
Modifier.fillMaxSize().drawWithContent {
    backdrop.record { this@drawWithContent.drawContent() }
    drawLayer(backdrop)
}
```

**2. Glass panel draws the layer behind itself, offset, clipped, with an effect**
```kotlin
@Composable
fun GlassPanel(
    backdrop: GraphicsLayer, hostOrigin: () -> Offset, modifier: Modifier = Modifier,
    shape: Shape = RoundedCornerShape(28.dp), tint: Color = Color.White.copy(alpha = 0.10f),
    content: @Composable BoxScope.() -> Unit,
) {
    var panelOrigin by remember { mutableStateOf(Offset.Zero) }
    val effectLayer = rememberGraphicsLayer()
    val cornerPx = with(LocalDensity.current) { 28.dp.toPx() }
    Box(
        modifier
            .onGloballyPositioned { panelOrigin = it.positionInRoot() }
            .clip(shape)
            .drawBehind {
                val rel = panelOrigin - hostOrigin()                       // panel position inside the host
                effectLayer.renderEffect = glassEffect(size, cornerPx)     // null => no effect
                effectLayer.record { translate(-rel.x, -rel.y) { drawLayer(backdrop) } }
                drawLayer(effectLayer)
                drawRect(tint)
            }
            .glassRim(shape),
        content = content,
    )
}
```

**3. Effect factory with API gates**
```kotlin
fun glassEffect(size: Size, cornerPx: Float): RenderEffect? = when {
    Build.VERSION.SDK_INT >= 33 -> LensShader.effect(size, cornerPx)           // refraction + light blur
    Build.VERSION.SDK_INT >= 31 -> BlurEffect(24f, 24f, TileMode.Clamp)        // blur only
    else -> null                                                               // caller draws opaque fallback
}
```

**4. AGSL refraction (API 33+)**
```kotlin
@RequiresApi(33)
object LensShader {
    private const val SRC = """
uniform shader content;
uniform float2 size;
uniform float radius;
uniform float depth;        // rim width in px (e.g. 24)
uniform float refraction;   // 0..1 (e.g. 0.6)
uniform float dispersion;   // 0..1 chromatic split

float sdRoundRect(float2 p, float2 halfSize, float r) {
    float2 q = abs(p) - halfSize + r;
    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - r;
}
half4 main(float2 coord) {
    float2 hs = size * 0.5;                              // note: `half` is a reserved AGSL type name
    float2 p = coord - hs;
    float d = sdRoundRect(p, hs, radius);              // < 0 inside the shape
    float t = clamp(-d / depth, 0.0, 1.0);               // 0 at the rim, 1 deeper than `depth`
    float lens = pow(1.0 - t, 3.0);                      // strong only at the rim
    float2 e = float2(1.0, 0.0);
    float2 n = normalize(float2(
        sdRoundRect(p + e.xy, hs, radius) - sdRoundRect(p - e.xy, hs, radius),
        sdRoundRect(p + e.yx, hs, radius) - sdRoundRect(p - e.yx, hs, radius)) + 1e-5);
    float2 off = -n * lens * refraction * depth;         // flip the sign for the opposite lens look
    half4 c;
    c.r = content.eval(coord + off * (1.0 + 0.15 * dispersion)).r;
    c.g = content.eval(coord + off).g;
    c.b = content.eval(coord + off * (1.0 - 0.15 * dispersion)).b;
    c.a = 1.0;
    return c;
}"""
    fun effect(size: Size, cornerPx: Float): RenderEffect {
        val shader = RuntimeShader(SRC).apply {
            setFloatUniform("size", size.width, size.height)
            setFloatUniform("radius", cornerPx)
            setFloatUniform("depth", 24f)
            setFloatUniform("refraction", 0.6f)
            setFloatUniform("dispersion", 0.5f)
        }
        val lens = android.graphics.RenderEffect.createRuntimeShaderEffect(shader, "content")
        val soften = android.graphics.RenderEffect.createBlurEffect(6f, 6f, Shader.TileMode.CLAMP)
        return android.graphics.RenderEffect.createChainEffect(soften, lens).asComposeRenderEffect() // lens first, then blur
    }
}
```
Allocate the `RuntimeShader`/effect once per size change (`remember(size)`), not every frame.

**5. Rim highlight + press feel**
```kotlin
fun Modifier.glassRim(shape: Shape, width: Dp = 1.dp) = drawWithContent {
    drawContent()
    drawOutline(
        outline = shape.createOutline(size, layoutDirection, this),
        brush = Brush.linearGradient(
            0f to Color.White.copy(0.55f), 0.5f to Color.White.copy(0.05f), 1f to Color.White.copy(0.30f),
            start = Offset.Zero, end = Offset(size.width, size.height)),
        style = Stroke(width.toPx()),
    )
}
// press: animateFloatAsState(if (pressed) 1.04f else 1f, spring(dampingRatio = 0.6f, stiffness = 400f)) -> Modifier.graphicsLayer { scaleX = s; scaleY = s }
```

## Layout recipes
- **Floating bottom bar:** pill shape, 16 dp side margins, `navigationBarsPadding()`, content scrolls under it (`contentPadding` bottom = bar height + insets), `enableEdgeToEdge()`. Selected-tab indicator is a second small glass "lens" that slides with a spring.
- **Top app bar / sheet:** progressive blur (strongest at the edge) via the library path; keep text on a tint or scrim.
- **Dialogs/sheets over wallpaper:** `Window.setBackgroundBlurRadius` (API 31+) needs a translucent window theme and a check of `WindowManager.isCrossWindowBlurEnabled`; fall back to a scrim.

## Budget and accessibility
- Max 2-3 glass surfaces visible at once, each small. Scrolling content behind glass forces re-recording every frame: measure it.
- Contrast >= 4.5:1 for text over the WORST backdrop (bright wallpaper and dark photo). Add tint or a scrim; use `contentColorFor`.
- Honor reduce-motion (`Settings.Global.ANIMATOR_DURATION_SCALE == 0f` -> no press spring) and the opaque fallback triggers above. Keep `contentDescription`/semantics unchanged.
- No animated blur radius, no nested glass-on-glass.

## Verify
1. Compiles; runs on API 33+, API 31, and API 29 devices (all three branches).
2. Perfetto or `adb shell dumpsys gfxinfo <pkg> framestats`; Macrobenchmark `FrameTimingMetric` on a mid-range device while scrolling behind the glass; record p95 frame time before/after.
3. Screenshots on light and dark backdrops, large font scale. Note: Paparazzi/layoutlib does **not** render `RenderEffect`/AGSL: use device or emulator screenshots.
4. Toggle battery saver and confirm the opaque fallback appears without layout shift.

## Pitfalls
- `Modifier.blur` is a no-op below API 31; never rely on it alone.
- Sampling `content.eval` outside the layer bounds returns transparent or clamped pixels: keep `depth` smaller than half of the panel's short side.
- Forgetting `clip(shape)` makes the effect bleed past the rounded corners.
- Recreating `RuntimeShader` in `drawBehind` every frame allocates and janks.
- Glass over a flat solid background looks like nothing: it needs texture or color variety behind it.
