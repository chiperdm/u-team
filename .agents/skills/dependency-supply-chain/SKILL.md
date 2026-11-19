---
name: dependency-supply-chain
description: "Add, update and audit dependencies (npm, pub, Gradle, pip) safely: necessity check, maintenance, license, vulnerabilities, lockfiles, typosquats, install scripts, native plugin permissions. Use before adding any package or library, when updating versions, when `npm audit` or Dependabot alerts appear, or when evaluating a community library."
domain: security
---

# Dependencies

Before adding: is it truly needed? Check last release, maintainers/open issues, license compatibility, size/transitive deps, platform support, and whether the platform/SDK already does it. Pin via lockfile; commit it.
- npm: `npm ci` in CI, `npm audit` (triage; don't blindly `--force`), consider `--ignore-scripts` for untrusted installs, watch for typosquats and sudden maintainer changes.
- Flutter: `flutter pub outdated`, `flutter pub deps`, review native plugin permissions they add to the manifest.
- Android: Gradle version catalog + dependency locking/verification where used.
- Update in small, grouped PRs (Renovate/Dependabot), run the full tests, read changelogs for breaking changes.
- Remove unused packages. Never add a dependency just to save a few lines.

## Evaluation card (fill before adding)
| Question | Answer |
|---|---|
| Does the platform/SDK already do this? | |
| Last release / commit, open critical issues | |
| Maintainers (bus factor), downloads/stars as a weak signal | |
| License compatible (MIT/Apache/BSD ok; GPL/AGPL implications) | |
| Size, transitive deps, native code, permissions added | |
| Min SDK / platform support / null-safety / Kotlin/Dart versions | |
| Security: advisories, install scripts, network calls | |
| Exit plan if abandoned | |

## Commands
```bash
npm audit --omit=dev && npm outdated && npm ls <pkg>     # Node
flutter pub outdated && flutter pub deps --style=compact # Flutter
./gradlew dependencies --configuration releaseRuntimeClasspath   # Android
pip list --outdated && pip-audit                                # Python (if installed)
```

## Pitfalls
- Adding a heavy library for one helper function.
- Blindly running `npm audit fix --force`.
- Pinning to `latest`/ranges in production apps.
- Copying install commands from AI answers without checking the exact package name (typosquats, hallucinated packages).

## Verify
Lockfile diff reviewed (only expected packages changed); build and tests pass from a clean install (`npm ci` / `flutter pub get` / clean Gradle build); app size and permissions diff checked; audit output attached or "not run".

## Related
`security-secrets-logging`, `devops-ci-flutter-node`, `kotlin-compose-liquid-glass` (library vs own implementation), `e2ee-messaging-review`.
