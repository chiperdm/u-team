# /init-project
Inspect the repository read-only and produce a safe project map before any work.

**Agents:** technical-architect (read-only)

## Steps
1. Read `AGENTS.md`, `README`, project instructions and `rules/`.
2. Run `git status --short` and `git branch --show-current`.
3. Identify framework, language, build tools, entry points, architecture, routing, state management, data layer, auth, backend.
4. Find design system, themes, reusable components, localization setup.
5. Run only safe baseline checks (`flutter analyze`, `./gradlew lint`, `npm test`...) and record the real results.
6. List protected areas and risks.

## Output
Project map: stack, architecture, commands, baseline results, uncommitted work, risks, suggested pilot.

## Guardrail
Read-only. Do not edit, install or format anything.
