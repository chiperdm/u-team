# Git and Worktree Safety
- Start with `git status --short` and inspect the current branch.
- Never run `git reset --hard`, `git clean -fd`, force-push, or destructive checkout commands without explicit approval.
- Never overwrite uncommitted user changes.
- Use worktrees only when the repository and Antigravity runtime support them.
- Assign one worktree/branch per independent coding agent.
- Before integration, inspect diff, status, conflicts, tests, and generated files.
