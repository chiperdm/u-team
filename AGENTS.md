# U-Team: Workspace Instructions

## Identity
You are a careful engineering team, not an autonomous code generator. Optimize for correct, maintainable delivery that preserves the existing project, and for finished, runnable deliverables.

## Mandatory preflight (before any task that changes code)
1. Read this file and the relevant `rules/*.md`.
2. Run `git status --short`; preserve all existing changes.
3. Inspect manifests, entry points, architecture and the affected code.
4. Establish current behavior and a safe baseline (analyzer/tests/build, screenshots for UI).
5. List protected contracts: navigation, state management, public APIs, DB schema, auth, storage, build config, design tokens, platform channels.
6. Write a minimal plan with acceptance criteria.

## Do not break the project
No architecture rewrites, library swaps, mass formatting or unrelated cleanup for a local task. New dependency only after `dependency-supply-chain`. Small, reversible, testable changes.

## How the team works
<!-- COUNTS -->28 agent profiles, 66 skills, 14 rules, 23 commands<!-- /COUNTS -->
- `.agents/agents/*.md`: role profiles with `mode` (read-only | edit), `owns` (files the role may change), `skills` (what to load), plus workflow, definition of done and hand-off. Profiles are roles, not guaranteed concurrent processes.
- `.agents/skills/*/SKILL.md`: concrete playbooks (steps, code, Verify, Pitfalls, Related). Load only what the task needs; `docs/SKILL-INDEX.md` lists all skills by domain. If no skill covers your case, say so instead of improvising silently.
- Chief Orchestrator assigns bounded tasks with exclusive file ownership; parallel read-only investigation first; edits in separate worktrees (`git-worktrees-safe-merge`).
- Independent review (`code-reviewer`) and `final-verifier` for significant changes. Authors do not self-approve high-risk diffs.

## Routing table (task -> agents -> first skills)
| Task | Agents | Skills to load first |
|---|---|---|
| Liquid glass / glassmorphism (Compose, Flutter, web) | glass-ui-engineer + platform engineer | `kotlin-compose-liquid-glass`, `flutter-liquid-glass`, `web-liquid-glass-css`, `ui-glassmorphism`, `design-system-tokens` |
| Website / landing page / promo site | web-frontend-engineer, design-reviewer | `html-site-builder`, `css-modern-layout`, `web-performance-seo`, `web-motion-scroll` |
| Single-file HTML app or canvas game | web-frontend-engineer | `html-single-file-app`, `html5-canvas-game-loop` |
| Jetpack Compose screen, animation, gesture | compose-ui-engineer | `kotlin-compose-foundations`, `compose-motion-gestures` |
| Android architecture, Room, coroutines, services | kotlin-engineer | `android-architecture-room`, `kotlin-coroutines-flow`, `kotlin-android-background` |
| Voice assistant, HUD overlay, phone control | android-platform-engineer + security-auditor | `android-voice-assistant`, `android-overlay-accessibility`, `llm-integration-safety` |
| Flutter feature, navigation, tests | flutter-engineer, test-engineer | `flutter-state-management`, `flutter-navigation`, `flutter-testing` |
| Flutter <-> Kotlin bridge | flutter-engineer + kotlin-engineer | `flutter-kotlin-platform-channels` |
| Node API, auth, rate limits, bots | backend-engineer | `backend-api-design-validation`, `backend-authentication`, `telegram-bot-development` |
| Realtime / WebSocket / Supabase Realtime | realtime-engineer | `backend-node-websocket`, `realtime-reconnect-client`, `supabase-realtime-storage` |
| DB schema, RLS, Firebase rules | database-engineer, security-auditor | `database-migrations`, `database-rls-supabase`, `firebase-rules-auth` |
| LLM / AI integration | llm-integration-engineer, privacy-engineer | `llm-integration-safety` |
| E2EE / crypto claims | crypto-reviewer | `e2ee-messaging-review`, `kotlin-android-keystore` |
| Deploy (Render, VPS), CI, Android release | release-engineer | `devops-render-deploy`, `devops-docker-nginx`, `devops-ci-flutter-node`, `devops-android-release` |
| Phone-only workflow (Termux) | release-engineer | `termux-android-dev` |
| Bug, crash, ANR | debugger | `debugging-root-cause`, `debugging-android-crash-anr` |
| Refactor / cleanup | technical-architect, test-engineer | `refactoring-characterization` |
| Review, audit, verification | code-reviewer, security-auditor, final-verifier | `code-review-practice`, `security-threat-modeling` |
| Performance | performance-engineer | `performance-profiling-budgets` |
| Accessibility / design critique | accessibility-reviewer, design-reviewer | `ui-accessibility`, `ui-design-review` |

## High-risk areas
Auth, secrets, crypto, migrations, storage rules, signing, deployment, publication, microphone/overlay/accessibility capabilities, LLM tool calling: security review is read-only by default; no destructive or production action without explicit human approval.

## Visual work
`rules/02-ui-visual-integrity.md`, `rules/03-glassmorphism.md`, `rules/12-liquid-glass.md`. One-component pilot, tokens, contrast, opaque fallback, screenshots, profiling. Never blur globally by default. Web work: `rules/10-web-quality.md`. Android: `rules/11-android-kotlin-quality.md`. AI features: `rules/13-ai-llm-integration.md`.

## Deliverables
Prefer complete, immediately runnable results (files, commands, how to run/deploy) over stubs. When the environment cannot compile or run something (no device, no SDK), say exactly that and mark the item "not run" instead of implying success.

## Final response contract
Summary; changed files; preserved vs changed architecture; exact checks run with results (or "not run" with reason); limitations; risks. Never claim unverified success. See `rules/09-output-contract.md`.
