# 🚀 U-Team (v1.0.0)

> **Autonomous multi-agent engineering team for Antigravity, Claude Code, Cursor, and agentic workflows.**  
> A structured software development pack providing role-based agents, playbooks, guardrails, and automated verification.

---

## 📊 Overview

<!-- COUNTS -->
| Part | Count |
|---|---|
| agents | 28 |
| skills | 66 |
| rules | 14 |
| commands | 23 |
| hooks | 3 |
| workflows | 7 |
| templates | 8 |
<!-- /COUNTS -->

---

## 🎯 Engineering Philosophy

Most AI code assistants behave as isolated code generators. **U-Team** organizes agents as a coordinated engineering team with strict operational discipline:

1. **Mandatory Preflight**: Inspect working tree state, manifests, dependencies, and architectural contracts before writing any code.
2. **Preserve Existing Architecture**: Zero arbitrary refactors, library swaps, or mass reformatting. Modifications stay minimal, focused, and testable.
3. **Exclusive File Ownership**: Parallel agents investigate concurrently in read-only mode, while file modifications are strictly isolated across disjoint files or dedicated worktrees.
4. **Independent Peer Review & Verification**: Code authors never self-approve critical diffs. Independent reviewers (`code-reviewer`, `security-auditor`, `final-verifier`) validate acceptance criteria.
5. **Evidence-Based Results**: No unverified claims. Every completion report details executed commands, concrete outputs, known limitations, and fallback behavior.

---

## 🛠️ Technology Domains

```
                      ┌─────────────────────────────────────────┐
                      │          Chief Orchestrator             │
                      └────────────────────┬────────────────────┘
                                           │
         ┌───────────────────┬─────────────┴───────┬────────────────────┐
         ▼                   ▼                     ▼                    ▼
┌──────────────────┐┌──────────────────┐┌──────────────────┐┌──────────────────┐
│ Native & Mobile  ││  Web & Creative  ││ Backend & Realtime││Security & Quality│
│ • Kotlin/Android ││ • Modern CSS/HTML││ • Node.js APIs   ││ • E2EE & Keystore│
│ • Jetpack Compose││ • Canvas Engines ││ • WebSockets (ws) ││ • STRIDE Threats │
│ • Flutter / Dart ││ • Liquid Glass UI││ • Supabase / RTDB ││ • Test Engineers │
│ • Voice & System ││ • Design Tokens  ││ • Telegram Bots   ││ • Final Verifiers│
└──────────────────┘└──────────────────┘└──────────────────┘└──────────────────┘
```

The team spans **13 core domains**:
- **Android & Kotlin**: Coroutines, Flow, Room migrations, Foreground Services, System Overlays, Accessibility Services, Voice Assistants.
- **Flutter**: Declarative routing (`go_router`), state management patterns, unit/widget/integration testing, platform channels.
- **Liquid Glass & UI**: Restrained glassmorphic design systems, AGSL runtime shaders, Flutter fragment shaders, CSS displacement maps.
- **Web & Performance**: Semantic HTML5, container queries, fluid layouts, canvas animation loops, Core Web Vitals, SEO optimization.
- **Backend & APIs**: REST design with Zod validation, idempotent mutations, rate limiting, structured observability, Telegram bots.
- **Data & Realtime**: PostgreSQL indexing, keyset pagination, Supabase Realtime & RLS, Firebase security rules.
- **AI & LLM Integration**: Server-side credential isolation, structured output validation, streaming pipelines, prompt-injection defense.
- **Security & Privacy**: Zero-secret exposure, platform cryptographic primitives, dependency supply-chain auditing, threat modeling.
- **DevOps & Releases**: Multi-stage Docker containers, Nginx reverse proxy, Render deployments, Google Play signing, Termux workflows.

---

## 👥 The 28 Agent Personas

| Agent | Mode | Ownership Scope | Mission |
|---|---|---|---|
| `chief-orchestrator` | Edit | Docs, plans, tasks | Decomposes complex tasks, establishes file boundaries, coordinates subagents, drives final delivery. |
| `technical-architect` | Read-only | Architecture & ADRs | Inspects dependencies, formulates minimal-diff technical designs, documents architecture decision records. |
| `product-analyst` | Read-only | Requirements & specs | Transforms ambiguous briefs into clear acceptance criteria, functional requirements, and edge-case lists. |
| `android-platform-engineer`| Edit | Native Android services | Develops system overlays, AccessibilityServices, and native voice assistant pipelines. |
| `kotlin-engineer` | Edit | Kotlin & Android code | Builds robust native Android logic, Room repositories, coroutines, and background workers. |
| `compose-ui-engineer` | Edit | Jetpack Compose UI | Builds fluid Compose UI screens, spring physics, gesture handling, and AGSL glass effects. |
| `flutter-engineer` | Edit | Flutter application code | Builds reactive Flutter screens, state management logic, platform bridges, and offline caches. |
| `web-frontend-engineer` | Edit | Web & Canvas code | Develops accessible HTML/CSS sites, single-file interactive tools, and HTML5 canvas engines. |
| `glass-ui-engineer` | Edit | Visual surfaces & shaders | Implements balanced glassmorphic and liquid-glass surfaces across Web, Compose, and Flutter. |
| `ui-ux-designer` | Read-only | Design specifications | Designs visual layouts, typography hierarchies, component states, and responsive patterns. |
| `backend-engineer` | Edit | Server & API code | Builds resilient Node.js APIs, input validation boundaries, rate limiters, and Telegram bots. |
| `realtime-engineer` | Edit | WebSockets & realtime | Implements robust WebSocket servers, reconnection algorithms, message ordering, and state sync. |
| `database-engineer` | Edit | SQL & schema migrations | Designs normalized schemas, lock-safe migrations, composite indexes, and row-level security rules. |
| `llm-integration-engineer` | Edit | AI integration code | Connects LLM endpoints safely with streaming, structured output validation, and quota guards. |
| `security-auditor` | Read-only | Security audit logs | Performs STRIDE threat modeling, checks input sanitization, and verifies authorization boundaries. |
| `crypto-reviewer` | Read-only | Cryptography reviews | Inspects end-to-end encryption protocols, key storage, and double-ratchet implementations. |
| `privacy-engineer` | Read-only | Privacy assessments | Validates data minimization, ensures local-first storage hygiene, and verifies compliance. |
| `dependency-auditor` | Read-only | Dependency analysis | Scans package manifests for vulnerabilities, maintenance status, licenses, and typosquatting. |
| `code-reviewer` | Read-only | Code review findings | Delivers structured, objective reviews focusing on correctness, maintainability, and contracts. |
| `debugger` | Read-only | Root cause analysis | Systematically reproduces anomalies, isolates regressions, and establishes verified root causes. |
| `performance-engineer` | Edit | Profiling & benchmarks | Measures bottlenecks, eliminates layout jank, optimizes database query plans, and cuts bundle size. |
| `accessibility-reviewer` | Read-only | Accessibility audits | Evaluates contrast, screen reader compatibility, touch targets, and reduced-motion fallbacks. |
| `design-reviewer` | Read-only | Visual critiques | Reviews visual balance, rhythm, typography, theme consistency, and eliminates generic UI artifacts. |
| `test-engineer` | Edit | Test suites & fixtures | Writes deterministic unit, widget, integration, and contract tests matching acceptance criteria. |
| `final-verifier` | Read-only | Acceptance validation | Executes independent end-to-end checks against initial acceptance criteria before signing off. |
| `git-integrator` | Edit | Branches & worktrees | Manages isolated worktrees, branch hygiene, merge conflict resolution, and history safety. |
| `release-engineer` | Edit | Release & deployment | Handles CI pipelines, Docker builds, signing configurations, release rollouts, and rollback plans. |
| `documentation-writer` | Edit | Docs & user guides | Authors concise user guides, API docs, changelogs, and operations runbooks. |

---

## ⚡ Slash Commands

| Command | Primary Agent | Primary Skills | Description |
|---|---|---|---|
| `/init-project` | `chief-orchestrator` | `docs-adr-handoff` | Inspect the repository in read-only mode and establish baseline documentation. |
| `/plan` | `chief-orchestrator` | `docs-adr-handoff` | Analyze user requirements and formulate an actionable implementation plan. |
| `/implement-safe` | `chief-orchestrator` | `testing-strategy` | Execute a planned feature step-by-step with continuous regression testing. |
| `/compose-screen` | `compose-ui-engineer` | `kotlin-compose-foundations` | Build a Jetpack Compose screen with state hoisting and edge-to-edge support. |
| `/android-assistant`| `android-platform-engineer`| `android-voice-assistant` | Implement voice assistant or floating HUD overlay with proper system permissions. |
| `/liquid-glass` | `glass-ui-engineer` | `ui-glassmorphism` | Apply measured Liquid Glass effects with contrast checks and opaque fallbacks. |
| `/build-site` | `web-frontend-engineer` | `html-site-builder` | Create a responsive, accessible website with dark mode and zero unnecessary runtime dependencies. |
| `/html-app` | `web-frontend-engineer` | `html-single-file-app` | Build a self-contained single-file HTML/JS tool with local persistence. |
| `/telegram-bot` | `backend-engineer` | `telegram-bot-development` | Scaffold a resilient Telegram bot with state handling and flood control. |
| `/llm-integrate` | `llm-integration-engineer` | `llm-integration-safety` | Integrate LLM API calls with server-side keys, schema validation, and guardrails. |
| `/debug` | `debugger` | `debugging-root-cause` | Systematically diagnose and identify the root cause of an issue. |
| `/review` | `code-reviewer` | `code-review-practice` | Perform an independent code review of working tree changes. |
| `/security-audit` | `security-auditor` | `security-threat-modeling`| Run a security assessment covering input validation, authorization, and data leaks. |
| `/perf-audit` | `performance-engineer` | `performance-profiling-budgets`| Benchmark application performance and identify rendering or query bottlenecks. |
| `/a11y-audit` | `accessibility-reviewer` | `ui-accessibility` | Evaluate user interface for WCAG compliance, screen readers, and touch targets. |
| `/design-review` | `design-reviewer` | `ui-design-review` | Critique interface visual design, rhythm, typography, and contrast. |
| `/refactor-safe` | `technical-architect` | `refactoring-characterization` | Refactor code under characterization tests without altering runtime behavior. |
| `/test-feature` | `test-engineer` | `testing-strategy` | Generate deterministic test suites derived directly from acceptance criteria. |
| `/deploy-prep` | `release-engineer` | `devops-docker-nginx` | Prepare production deployment configurations (Docker, Nginx, or Render). |
| `/release-check` | `release-engineer` | `release-checklist-rollback` | Perform final pre-release readiness checks and verify rollback plans. |
| `/final-verify` | `final-verifier` | `testing-evidence` | Run end-to-end verification against original acceptance criteria. |
| `/delegate` | `chief-orchestrator` | `docs-adr-handoff` | Hand off a specific task slice to a specialized agent persona. |
| `/glass-ui` | `glass-ui-engineer` | `ui-glassmorphism` | Review or style translucent glass surfaces with measured performance budgets. |

---

## 🔒 Mandatory Safety Rules

Every action performed by the team is governed by 14 explicit rules:
1. **Core Safety (`00-core-safety.md`)**: No destructive Git commands, no overwriting uncommitted user work, and no fabrication of test results.
2. **Preserve Project (`01-preserve-project.md`)**: Existing architecture, routing, and coding conventions take precedence.
3. **UI Visual Integrity (`02-ui-visual-integrity.md`)**: Support dark/light themes, keyboard navigation, safe areas, and all UI states.
4. **Glassmorphism Quality Standard (`03-glassmorphism.md`)**: Translucent surfaces must maintain readable contrast ratios and provide opaque fallbacks.
5. **Parallel Agent Coordination (`04-parallel-agents.md`)**: Disjoint file ownership prevents write conflicts between agents.
6. **Testing & Evidence (`05-testing-evidence.md`)**: Every claim must be backed by real command output; untested items must be labeled "not run".
7. **Security & Privacy (`06-security-privacy.md`)**: Enforce server-side authorization boundaries, protect user secrets, and sanitize inputs.
8. **Git Worktree Safety (`07-git-and-worktrees.md`)**: Isolated branches or worktrees ensure changes can be safely rolled back.
9. **Release & Deploy Approval (`08-release-and-deploy.md`)**: Production releases and external publication require human approval.
10. **Output Contract (`09-output-contract.md`)**: Structured reports detailing inspected files, changes made, checks executed, and remaining risks.
11. **Web Quality Standard (`10-web-quality.md`)**: Semantic HTML, zero horizontal scroll, responsive clamp scaling, and fast Core Web Vitals.
12. **Android & Kotlin Quality (`11-android-kotlin-quality.md`)**: Structured concurrency, lifecycle-aware collections, and secure Keystore integration.
13. **Liquid Glass Standard (`12-liquid-glass.md`)**: Tiered shader implementations with fallbacks for low-end hardware and battery saver modes.
14. **AI & LLM Integration (`13-ai-llm-integration.md`)**: Strict validation of model inputs/outputs, rate limits, and quota management.

---

## 🚀 Installation & Setup

### Option 1: Install as an Antigravity Plugin

Clone or copy the pack directly into your Antigravity plugins directory:

```bash
mkdir -p ~/.gemini/config/plugins/u-team
cp -r . ~/.gemini/config/plugins/u-team/
```

Antigravity will automatically discover the bundle through `plugin.json`.

---

### Option 2: Project-Level Installation

Inject the skills, agents, rules, and commands into your project repository in non-destructive merge mode:

```bash
# Preview what would be copied
bash scripts/install-project.sh /path/to/your/project --dry-run

# Perform installation (never overwrites existing files)
bash scripts/install-project.sh /path/to/your/project

# Install skills only
bash scripts/install-project.sh /path/to/your/project --skills-only
```

---

### Option 3: Global Installation

Install agents and skills to your user configuration directory:

```bash
bash scripts/install-global.sh
```

---

### Option 4: Use with Claude Code, Cursor, Windsurf, or Gemini CLI

All skills and agent profiles use standard Markdown and YAML frontmatter. You can point your assistant to the `.agents/skills/` directory or incorporate `AGENTS.md` into your system instructions.

---

## 🧪 Pack Validation & Tooling

The pack includes built-in verification scripts to maintain quality and prevent bit rot:

```bash
# Validate entire pack structure, cross-references, and code syntax
python3 scripts/validate-pack.py

# Scaffold a new validated skill playbook
python3 scripts/new-skill.py my-new-skill backend "Use when building custom backend services."

# Generate design tokens with automated contrast checking
python3 .agents/skills/design-system-tokens/scripts/gen_tokens.py \
  .agents/skills/design-system-tokens/assets/tokens.example.json \
  --css styles/tokens.css
```

---

## 📄 License

Distributed under the MIT License. Built for high-efficiency engineering teams and AI-augmented software development.
