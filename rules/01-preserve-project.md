# Preserve Existing Project
- Do not rewrite the architecture, framework, navigation, state management, backend, database, or design system just to satisfy a localized request.
- Before editing, map the relevant files, public APIs, dependencies, routes, state flows, and data contracts.
- Record a baseline: build/analyzer/test status and, for UI work, screenshots at a fixed viewport/theme/state when possible.
- Change only the smallest relevant surface area.
- Avoid mass formatting, unrelated cleanup, dependency additions, and file moves unless necessary and justified.
- Preserve backwards compatibility for stored data, API clients, deep links, and supported OS versions.
- If the requested change requires a risky migration, explain the risk and ask before execution.
