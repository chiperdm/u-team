---
name: release-checklist-rollback
description: "Final pre-release verification and rollback planning for app and backend changes: GO/NO-GO checklist, evidence list, staged rollout, rollback steps, post-release monitoring. Use before any release, deploy, store submission, OTA update or when asked 'is this ready to ship?'."
domain: process
---

# Release readiness

- [ ] Scope and changelog written; version bumped.
- [ ] CI green on the release commit; commands and results recorded (not assumed).
- [ ] DB migrations are backward compatible with the previous app/server version; backup/restore path known.
- [ ] Feature flags/kill-switch for risky features.
- [ ] Security review for auth/storage/crypto changes; no secrets in the diff.
- [ ] Manual smoke test on real devices: install, login, send/receive, offline resend, push, update-from-previous-version.
- [ ] Monitoring/alerts ready (crash rate, error rate, latency); owner on call.
- [ ] Rollout plan (staged) and explicit **rollback steps** with who/when/how.
- [ ] Human approval recorded before publish/deploy.
Output: GO / NO-GO with blockers, evidence list, residual risks.

## Post-release watch (first 24-72 h)
Crash-free users/sessions, ANR rate, error rate, p95 latency, WebSocket connection count/reconnects, auth failures, support reports. Define thresholds that trigger rollback in advance (for example crash-free < 99%, error rate 2x baseline).

## Output template
```
Decision: GO | NO-GO | GO with conditions
Evidence:  <commands + results>   Blockers: <list>   Residual risks: <list>
Rollout:   <stages, owner, time>  Rollback: <exact steps, owner, max time>
Approvals: <who approved publish/deploy, when>
```

## Verify
Rollback was rehearsed or at least dry-run read by a second person; backups verified; feature flags default safe.

## Pitfalls
Releasing on Friday evening without an owner; irreversible migrations bundled with the app release; no way to disable a broken feature remotely.

## Related
`devops-android-release`, `devops-render-deploy`, `devops-docker-nginx`, `database-migrations`, `final-verifier` agent.
