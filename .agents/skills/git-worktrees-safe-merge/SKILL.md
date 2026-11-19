---
name: git-worktrees-safe-merge
description: "Use Git branches, worktrees, commits and merges safely, especially with several AI agents editing in parallel; conflict resolution, recovery with reflog, safe force-push alternatives. Use at the start of any code change, before merging agent branches, when conflicts or lost work appear, or when someone asks to reset/clean a repo."
domain: process
---

# Git safety

- Start: `git status --short`, `git branch --show-current`. Never overwrite uncommitted work; stash or commit it first with the owner's consent.
- One agent = one branch = one worktree:
```bash
git worktree add ../wt-chat-ui -b feat/chat-ui
# ... work, commit small ...
git worktree remove ../wt-chat-ui   # after merge
```
- Assign disjoint file ownership; shared files (lockfiles, generated code, routes) are edited only by the integrator.
- Integrate: review `git diff --stat main...feat/x`, run tests, merge/rebase, resolve conflicts by understanding both sides, re-run tests.
- Forbidden without explicit approval: `git reset --hard`, `git clean -fd`, force-push, `checkout --` on files with changes, history rewrite on shared branches.
- Small commits with meaningful messages; no secrets, no build output.

## Recovery cookbook
```bash
git reflog                       # find the lost commit
git branch rescue <sha>          # keep it safe before anything else
git restore --staged --worktree <file>   # discard changes to ONE file (destructive: needs approval)
git stash push -u -m "wip before pull"   # safe temporary shelf
git merge --abort / git rebase --abort   # back out of a messy integration
git push --force-with-lease      # only on your own branch, with approval; never plain --force
```

## Commit hygiene
Conventional-style messages (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`), one logical change per commit, no generated/build files, run `hooks/pre-commit-secret-scan.sh` before committing.

## Verify
After integration: `git log --oneline --graph -n 15`, `git diff --stat <base>...HEAD` equals the plan, tests green on the merge result (not only on each branch).

## Pitfalls
- Two agents editing the same file in different worktrees.
- Resolving conflicts by taking "ours" everywhere.
- Rebasing a shared branch.

## Related
`code-review-practice`, `refactoring-characterization`, `release-checklist-rollback`, `termux-android-dev`.
