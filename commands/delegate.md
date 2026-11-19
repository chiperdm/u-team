# /delegate
Split the request into bounded tasks and assign specialist profiles.

**Agents:** chief-orchestrator
**Skills:** `git-worktrees-safe-merge`

## Steps
1. Run `/init-project` if no project map exists.
2. Create task cards with `templates/agent-task.md` (owner, owned files, mode, skills, acceptance criteria).
3. Run read-only investigations in parallel first.
4. Allow parallel edits only on disjoint files in separate worktrees.
5. Integrate, run checks, send to `code-reviewer` and `final-verifier`.

## Output
Task table + integration order + final report per `rules/09-output-contract.md`.

## Guardrail
Never exceed real concurrency; profiles are not parallel processes.
