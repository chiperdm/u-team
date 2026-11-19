---
name: docs-adr-handoff
description: "Write ADRs, handoff notes, changelogs, READMEs and runbooks that future maintainers and AI agents can use. Use when finishing a task, making an architectural decision, onboarding someone, releasing, or when the project has no docs or stale docs."
domain: docs
---

# Docs that get used

**ADR** (`docs/adr/NNNN-title.md`): Status, Context (forces/constraints), Decision, Alternatives considered, Consequences (good/bad), Revisit-when.
**Handoff note:** what was done, what is half-done, how to run/test, files touched, decisions + why, known issues, next step.
**Changelog:** Keep-a-Changelog style (Added/Changed/Fixed/Security), user-facing language.
**README minimum:** what it is, prerequisites, run, test, build, env vars (names only), architecture sketch, where to ask.
Rules: write what is true now, link instead of copying, date decisions, keep examples runnable, delete stale docs.

## ADR template
```
# NNNN. Title
Status: proposed | accepted | superseded by NNNN
Date: YYYY-MM-DD
## Context  (forces, constraints, what we know)
## Decision (one paragraph, active voice)
## Alternatives considered (and why not)
## Consequences (positive, negative, follow-ups)
## Revisit when (trigger)
```

## Handoff note template
`Done / Half-done / Not started / How to run + test / Files touched / Decisions and why / Known issues / Next step / Secrets or access needed (names only)`.

## Runbook skeleton
Symptom -> quick check command -> likely cause -> fix -> escalation; keep each under one screen.

## Verify
A new teammate (or fresh agent) can run the project from the README in <= 15 minutes; links work; commands are copy-pasteable and were actually run.

## Pitfalls
Docs that describe wishes instead of reality; duplicating code comments in prose; never deleting outdated docs.

## Related
`release-checklist-rollback`, `templates/agent-task.md`, `refactoring-characterization`.
