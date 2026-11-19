# Parallel Agent Coordination
- The orchestrator assigns bounded tasks and exclusive file ownership.
- Prefer parallel read-only investigation first; parallel code edits only when file ownership is disjoint.
- Do not let multiple agents edit the same file or shared generated output.
- Use isolated branches/worktrees when supported; inspect `git status` before creating, switching, or merging.
- Limit active workers to actual tool/model/account concurrency. Agent profiles are not concurrent model instances.
- Every worker reports files inspected/changed, commands run, results, assumptions, and risks.
- A reviewer who did not author the change must inspect high-risk diffs.
