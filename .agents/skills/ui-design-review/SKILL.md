---
name: ui-design-review
description: "Critique and improve the visual quality of a UI (web, Android, Flutter): hierarchy, spacing rhythm, typography, color, states, density, consistency, motion, plus a checklist of 'generic AI look' tells. Produces a prioritized findings table with concrete fixes. Use when the user says it looks ugly, boring, cheap, generic, messy, asks for a design review, redesign advice, or before shipping any new screen or landing page."
domain: ui
---

# UI design review

Read-only by default: output findings and proposed token/spacing/type changes; implementation goes to `glass-ui-engineer`, `compose-ui-engineer`, `flutter-engineer` or `web-frontend-engineer`. Never propose a full redesign for a local complaint (`rules/01-preserve-project.md`): fix the highest-impact issues first.

## Procedure
1. **See it:** screenshots at the real viewports/themes (phone 360-412 px, tablet, desktop; light+dark; large text). If you cannot render it, say the review is from code only.
2. **State the intent:** who uses this screen, the single primary action, the emotional tone.
3. **Walk the checklist** below; record each finding with location, evidence, severity, fix.
4. **Rank by impact/effort**; propose a 1-component pilot for the top item.
5. **Output** the table + "keep as is" list (what works) + a small before/after plan.

## Checklist
**Hierarchy and focus:** one clear primary action per view; reading order matches importance; size/weight/contrast carry hierarchy (not borders everywhere); the eye lands on the content, not on chrome.
**Spacing and layout:** consistent scale (4/8-pt); related items closer than unrelated (proximity); aligned edges/baselines; consistent gutters; enough whitespace; no cramped touch targets; content width sane (45-75 characters for reading text).
**Typography:** <= 2 families, 3-5 sizes in use, clear scale; body >= 16 px/16 sp; line-height 1.4-1.6; no all-caps paragraphs; weights used purposefully; Cyrillic/Kazakh glyph coverage; truncation rules for long names.
**Color and contrast:** neutral base + one accent; semantic colors only for states; 4.5:1 text contrast (3:1 large/UI); colors not the only signal; dark theme designed, not inverted; saturation restraint on large areas.
**Components and states:** every interactive element has default/hover/focus/pressed/disabled/loading/error; empty, error and offline states designed; forms have visible labels, helper and error text; consistent corner radii, icon style/stroke, elevation.
**Density and rhythm:** list rows scannable, card grids not monotonous, visual variety with intent (a hero, a break, an emphasis).
**Motion:** purposeful, fast (150-300 ms), consistent easing, respects reduced motion; no motion that hides the state change.
**Content:** realistic copy (no lorem ipsum), specific labels ("Send message" not "Submit"), real numbers, no fake testimonials; localization expansion (ru +30%).
**Accessibility:** touch >= 48 dp/44 pt, focus order, labels, text scale 200%, screen-reader names (`ui-accessibility`).

## "Generic AI look" tells (fix by making real choices)
Purple-to-blue gradient hero; identical rounded cards in 3 columns with emoji icons; everything centered; glass on everything; neon glow; stock gradient blobs; Inter/Roboto-only with no typographic idea; fake dashboards with random numbers; "revolutionize/seamless/cutting-edge" copy; same shadow on every element. Remedy: pick a direction (editorial, brutalist-lite, playful, technical), commit to one accent and one distinctive type/layout idea, remove 30% of decoration, show the real product.

## Glass-specific review (with `ui-glassmorphism`)
Is the glass over something worth blurring? text contrast over worst background; max 2-3 surfaces; rim highlight subtle; no glass-on-glass; fallback exists; performance measured.

## Output format
| # | Where | Finding (evidence) | Severity (blocker/major/minor/nit) | Fix (specific values) | Effort |
|---|---|---|---|---|---|
Then: "What works (keep)", "Top 3 changes", "Token changes" (exact values), "Not reviewed".
Severity: blocker = unusable/unreadable/inaccessible; major = confusing or clearly unprofessional; minor = polish; nit = taste.

## Pitfalls
- Reviewing taste instead of problems: tie every finding to a user effect.
- Prescribing new fonts/colors without checking the brand and existing tokens.
- Suggesting effects that cost frames on mid-range phones without a budget.

## Verify
Each finding is reproducible from the cited screenshot/viewport; proposed values (spacing, sizes, colors) were checked against tokens and contrast math; at least one finding is a "keep as is" to avoid churn.
