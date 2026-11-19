#!/usr/bin/env python3
"""Generate CSS / Kotlin (Compose) / Dart (Flutter) token files from tokens.json and check contrast.

Usage: gen_tokens.py tokens.json [--css out.css] [--kotlin Tokens.kt] [--dart tokens.dart] [--package com.example.ui]
Exit code 1 if a required contrast pair fails.
"""
import argparse, json, re, sys
from pathlib import Path

HEADER = "GENERATED FROM tokens.json by gen_tokens.py. DO NOT EDIT."
# (foreground, background, minimum ratio)
PAIRS = [("text", "bg", 4.5), ("text", "surface", 4.5), ("onAccent", "accent", 4.5),
         ("muted", "bg", 4.5), ("muted", "surface", 4.5)]

def parse_hex(h):
    h = h.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    if len(h) == 6: h += "ff"
    if not re.fullmatch(r"[0-9a-fA-F]{8}", h): raise ValueError(f"bad color {h!r}")
    r, g, b, a = (int(h[i:i + 2], 16) for i in (0, 2, 4, 6))
    return r, g, b, a

def lum(rgb):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(x) for x in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def blend(fg, bg):  # fg with alpha over opaque bg
    a = fg[3] / 255
    return tuple(round(fg[i] * a + bg[i] * (1 - a)) for i in range(3)) + (255,)

def ratio(fg, bg):
    fg = blend(fg, bg)
    l1, l2 = sorted((lum(fg), lum(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)

def css_color(h):
    r, g, b, a = parse_hex(h)
    return f"#{r:02x}{g:02x}{b:02x}" if a == 255 else f"rgb({r} {g} {b} / {a / 255:.2f})"

def kt_color(h):
    r, g, b, a = parse_hex(h); return f"Color(0x{a:02X}{r:02X}{g:02X}{b:02X})"

def dart_color(h):
    r, g, b, a = parse_hex(h); return f"Color(0x{a:02X}{r:02X}{g:02X}{b:02X})"

def camel(s): return s[:1].lower() + s[1:]
def pascal(s): return s[:1].upper() + s[1:]

def check(tokens):
    bad = []
    for scheme, colors in tokens["color"].items():
        for fg, bg, need in PAIRS:
            if fg in colors and bg in colors:
                r = ratio(parse_hex(colors[fg]), parse_hex(colors[bg]))
                status = "ok " if r >= need else "FAIL"
                print(f"  [{status}] {scheme:5} {fg:9} on {bg:8} {r:5.2f}:1 (min {need})")
                if r < need: bad.append((scheme, fg, bg, r))
    return bad

def gen_css(t):
    L = [f"/* {HEADER} */", ":root {", "  color-scheme: light dark;"]
    def block(colors, indent):
        return [f"{indent}--{k}: {css_color(v)};" for k, v in colors.items()]
    L += block(t["color"]["light"], "  ")
    for k, v in t.get("space", {}).items(): L.append(f"  --space-{k}: {v / 16:g}rem;")
    for k, v in t.get("radius", {}).items(): L.append(f"  --radius-{k}: {v}px;")
    for k, v in t.get("duration", {}).items(): L.append(f"  --duration-{k}: {v}ms;")
    g = t.get("glass", {})
    if g:
        L += [f"  --glass-sigma: {g['sigma']}px;", f"  --glass-border-alpha: {g['borderAlpha']};",
              f"  --glass-tint: rgb(255 255 255 / {g['tintAlphaLight']});",
              f"  --glass-fallback: {css_color(g['fallbackLight'])};"]
    L += ["}", "@media (prefers-color-scheme: dark) {", "  :root {"]
    L += block(t["color"]["dark"], "    ")
    if g:
        L += [f"    --glass-tint: rgb(255 255 255 / {g['tintAlphaDark']});",
              f"    --glass-fallback: {css_color(g['fallbackDark'])};"]
    L += ["  }", "}", ':root[data-theme="light"] { color-scheme: light; }', ':root[data-theme="dark"] { color-scheme: dark; }', ""]
    return "\n".join(L)

def gen_kotlin(t, pkg):
    L = [f"// {HEADER}", f"package {pkg}", "", "import androidx.compose.ui.graphics.Color", "import androidx.compose.ui.unit.dp", "import androidx.compose.ui.unit.Dp", "",
         "object Tokens {"]
    for scheme in ("light", "dark"):
        L.append(f"    object {pascal(scheme)} {{")
        for k, v in t["color"][scheme].items(): L.append(f"        val {camel(k)} = {kt_color(v)}")
        L.append("    }")
    L.append("    object Space {")
    for k, v in t.get("space", {}).items(): L.append(f"        val s{k}: Dp = {v}.dp")
    L.append("    }")
    L.append("    object Radius {")
    for k, v in t.get("radius", {}).items(): L.append(f"        val {camel(k)}: Dp = {v}.dp")
    L.append("    }")
    L.append("    object Duration {")
    for k, v in t.get("duration", {}).items(): L.append(f"        const val {camel(k)}Ms = {v}")
    L.append("    }")
    g = t.get("glass")
    if g:
        L += ["    object Glass {", f"        const val sigma = {g['sigma']}f", f"        const val borderAlpha = {g['borderAlpha']}f",
              f"        const val tintAlphaDark = {g['tintAlphaDark']}f", f"        const val tintAlphaLight = {g['tintAlphaLight']}f",
              f"        const val refraction = {g.get('refraction', 0.6)}f", f"        const val depth = {g.get('depth', 24)}f",
              f"        val fallbackDark = {kt_color(g['fallbackDark'])}", f"        val fallbackLight = {kt_color(g['fallbackLight'])}", "    }"]
    L += ["}", ""]
    return "\n".join(L)

def gen_dart(t):
    L = [f"// {HEADER}", "import 'package:flutter/painting.dart';", "", "abstract final class Tokens {"]
    for scheme in ("light", "dark"):
        for k, v in t["color"][scheme].items(): L.append(f"  static const {scheme}{pascal(k)} = {dart_color(v)};")
    for k, v in t.get("space", {}).items(): L.append(f"  static const double space{k} = {v};")
    for k, v in t.get("radius", {}).items(): L.append(f"  static const double radius{pascal(k)} = {v};")
    for k, v in t.get("duration", {}).items(): L.append(f"  static const duration{pascal(k)} = Duration(milliseconds: {v});")
    g = t.get("glass")
    if g:
        L += [f"  static const double glassSigma = {g['sigma']};", f"  static const double glassBorderAlpha = {g['borderAlpha']};",
              f"  static const double glassTintAlphaDark = {g['tintAlphaDark']};", f"  static const double glassTintAlphaLight = {g['tintAlphaLight']};",
              f"  static const double glassRefraction = {g.get('refraction', 0.6)};", f"  static const double glassDepth = {g.get('depth', 24)};",
              f"  static const glassFallbackDark = {dart_color(g['fallbackDark'])};", f"  static const glassFallbackLight = {dart_color(g['fallbackLight'])};"]
    L += ["}", ""]
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tokens"); ap.add_argument("--css"); ap.add_argument("--kotlin"); ap.add_argument("--dart")
    ap.add_argument("--package", default="com.example.ui")
    a = ap.parse_args()
    t = json.loads(Path(a.tokens).read_text(encoding="utf-8"))
    print("Contrast check:")
    bad = check(t)
    for path, content in ((a.css, lambda: gen_css(t)), (a.kotlin, lambda: gen_kotlin(t, a.package)), (a.dart, lambda: gen_dart(t))):
        if path:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content(), encoding="utf-8"); print(f"wrote {path}")
    if bad:
        print(f"{len(bad)} contrast pair(s) failed"); sys.exit(1)
    print("Contrast: all required pairs pass")

if __name__ == "__main__":
    main()
