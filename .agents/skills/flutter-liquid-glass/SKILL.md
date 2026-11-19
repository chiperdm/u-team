---
name: flutter-liquid-glass
description: "Implement Liquid Glass (blur + lens refraction + specular rim) in Flutter: BackdropFilter glass-lite, fragment-shader refraction (GLSL, FragmentProgram), backdrop capture, Impeller/Skia/web caveats, fallbacks and profiling. Use when the user wants an iOS 26 style glass nav bar, button, card or sheet in Flutter, or says liquid glass, refraction, frosted glass with lens effect."
domain: flutter
---

# Liquid Glass in Flutter

Start from `ui-glassmorphism` (tokens, contrast, fallback). This skill adds the refraction layer. Two tiers; ship tier 1 first.

## Tier 1: glass-lite (cheap, works everywhere BackdropFilter works)
Blur + tint + gradient rim. (A `ColorFilter` cannot be used as the `BackdropFilter` image filter, so true backdrop saturation/vibrancy needs the tier-2 shader; fake it with a slightly saturated tint color.) Good enough for most bars and cards, and the right fallback for tier 2.
```dart
class LiquidGlassLite extends StatelessWidget {
  const LiquidGlassLite({super.key, required this.child, this.radius = 28, this.sigma = 14});
  final Widget child; final double radius, sigma;
  @override
  Widget build(BuildContext context) {
    final r = BorderRadius.circular(radius);
    return ClipRRect(
      borderRadius: r,
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: sigma, sigmaY: sigma, tileMode: TileMode.clamp),
        child: DecoratedBox(
          decoration: BoxDecoration(
            borderRadius: r,
            color: Colors.white.withValues(alpha: 0.10),
            border: GradientBoxBorder(                     // or a CustomPainter stroke if you avoid the package
              gradient: LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [
                Colors.white.withValues(alpha: 0.55), Colors.white.withValues(alpha: 0.05), Colors.white.withValues(alpha: 0.30)]),
              width: 1),
          ),
          child: child,
        ),
      ),
    );
  }
}
```
If you do not want a package for the gradient border, paint it with `CustomPainter` (`drawRRect` + `Paint()..shader = gradient.createShader(rect)..style = PaintingStyle.stroke..strokeWidth = 1`).

## Tier 2: real refraction with a fragment shader
Declare in `pubspec.yaml`:
```yaml
flutter:
  shaders:
    - shaders/lens.frag
```
`shaders/lens.frag` (Flutter GLSL; verify against the Flutter version you target):
```glsl
#include <flutter/runtime_effect.glsl>
uniform vec2 uSize;          // panel size px            -> floats 0,1
uniform vec2 uOrigin;        // panel origin in backdrop -> floats 2,3
uniform vec2 uBackdropSize;  // backdrop image size      -> floats 4,5
uniform float uRadius;       //                          -> 6
uniform float uDepth;        // rim width px             -> 7
uniform float uRefraction;   // 0..1                     -> 8
uniform sampler2D uBackdrop; // image sampler 0
out vec4 fragColor;

float sdRoundRect(vec2 p, vec2 h, float r) {
  vec2 q = abs(p) - h + r;
  return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - r;
}
void main() {
  vec2 frag = FlutterFragCoord().xy;
  vec2 h = uSize * 0.5;
  vec2 p = frag - h;
  float d = sdRoundRect(p, h, uRadius);
  if (d > 0.0) { fragColor = vec4(0.0); return; }
  float t = clamp(-d / uDepth, 0.0, 1.0);
  float lens = pow(1.0 - t, 3.0);
  vec2 e = vec2(1.0, 0.0);
  vec2 n = normalize(vec2(
      sdRoundRect(p + e.xy, h, uRadius) - sdRoundRect(p - e.xy, h, uRadius),
      sdRoundRect(p + e.yx, h, uRadius) - sdRoundRect(p - e.yx, h, uRadius)) + 1e-5);
  vec2 src = uOrigin + frag - n * lens * uRefraction * uDepth;
  fragColor = texture(uBackdrop, src / uBackdropSize);
}
```
Dart side:
```dart
final program = await ui.FragmentProgram.fromAsset('shaders/lens.frag'); // load once, cache
class LensPainter extends CustomPainter {
  LensPainter(this.shader, this.backdrop, this.origin, this.radius);
  final ui.FragmentShader shader; final ui.Image backdrop; final Offset origin; final double radius;
  @override
  void paint(Canvas c, Size s) {
    shader
      ..setFloat(0, s.width)..setFloat(1, s.height)
      ..setFloat(2, origin.dx)..setFloat(3, origin.dy)
      ..setFloat(4, backdrop.width.toDouble())..setFloat(5, backdrop.height.toDouble())
      ..setFloat(6, radius)..setFloat(7, 24)..setFloat(8, 0.6)
      ..setImageSampler(0, backdrop);
    c.drawRRect(RRect.fromRectAndRadius(Offset.zero & s, Radius.circular(radius)), Paint()..shader = shader);
  }
  @override
  bool shouldRepaint(LensPainter old) => old.backdrop != backdrop || old.origin != origin;
}
```
**Getting the backdrop image:** wrap the background in a `RepaintBoundary`, then `final img = boundary.toImageSync(pixelRatio: dpr)` (cast `renderObject as RenderRepaintBoundary`). Capturing each frame is expensive: capture when the background changes (static wallpaper, on scroll end, or throttled to ~15-30 fps), and fall back to tier 1 while scrolling. Some Flutter versions can also use a fragment shader as an `ImageFilter` inside `BackdropFilter` (Impeller): check release notes for your version before building on it.
Community package `liquid_glass_renderer` exists for this problem: evaluate it with `dependency-supply-chain` before writing your own.

## Choosing and falling back
- Impeller/Skia on mobile: shaders supported. Web: custom shaders need CanvasKit/skwasm (not the old HTML renderer). Desktop: supported.
- Fall back to tier 1, then to an opaque `Material` surface, when: shader load throws, `MediaQuery.highContrastOf` is true, battery saver or a low-end flag is set, or the user disables transparency in settings.
- Wrap with `RepaintBoundary` only around the glass subtree if the profiler shows repaint spill.

## Verify
- DevTools Performance in **profile mode** on a mid-range device: raster time per frame with and without glass, before/after numbers.
- Golden tests cannot render shaders reliably: use device screenshots for tier 2; keep goldens for the fallback widget.
- Contrast check on bright and dark backgrounds; text scale 200%.

## Pitfalls
- Shaders: uniform float index order must match declaration order, and every `vec2` uses two slots.
- `toImageSync` returns an image you must `dispose()`.
- Blurring and refracting a full-screen area is a raster cliff: keep panels small.
- Don't stack `BackdropFilter`s (nested glass) and don't animate sigma.
