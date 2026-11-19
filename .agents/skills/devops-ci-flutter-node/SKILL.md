---
name: devops-ci-flutter-node
description: "Create or review CI (GitHub Actions) for Flutter apps, Android builds and Node backends: caching, least-privilege tokens, safe secrets, matrix, artifacts, APK build jobs for phone-only workflows. Use when setting up CI/CD, a pipeline is slow or flaky, secrets leak risk, or APKs must be built in the cloud."
domain: devops
---

# CI

```yaml
name: ci
on: { pull_request: {}, push: { branches: [main] } }
permissions: { contents: read }          # least privilege by default
concurrency: { group: ci-${{ github.ref }}, cancel-in-progress: true }
jobs:
  backend:
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: server } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version-file: .nvmrc, cache: npm, cache-dependency-path: server/package-lock.json }
      - run: npm ci
      - run: npm run lint --if-present
      - run: npm test
  app:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { channel: stable, cache: true }
      - run: flutter pub get
      - run: flutter analyze
      - run: flutter test
```
- Pin third-party actions to a full commit SHA for sensitive repos; keep versions current (check latest majors).
- Never run untrusted PR code with secrets (`pull_request_target` + checkout of the PR head is dangerous).
- Secrets only via the secret store, masked in logs; separate environments with approval for deploy.
- Use `npm ci` / lockfiles for reproducible builds; upload test reports/artifacts; fail on analyzer errors.

## Android APK build job (works from a phone-only workflow)
```yaml
  apk:
    runs-on: ubuntu-latest
    needs: [app]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '17' }
      - uses: subosito/flutter-action@v2
        with: { channel: stable, cache: true }
      - run: flutter pub get
      - name: Restore keystore
        run: echo "$KEYSTORE_B64" | base64 -d > android/app/upload.jks
        env: { KEYSTORE_B64: "${{ secrets.KEYSTORE_B64 }}" }
      - run: flutter build apk --release --split-per-abi
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
      - uses: actions/upload-artifact@v4
        with: { name: apk, path: build/app/outputs/flutter-apk/*.apk }
```
Gradle projects: `./gradlew assembleRelease` with `gradle/actions/setup-gradle` for caching. Action versions above are examples: check the current major of each action before copying.

## Verify
Open a PR with a deliberate failing test and confirm CI blocks; confirm secrets are not echoed (`set +x`), fork PRs do not receive secrets, artifacts retention is sensible, cache hit rate improves run time.

## Pitfalls
- `pull_request_target` with checkout of PR code.
- Writing the keystore into the repo workspace and uploading it as an artifact.
- Unpinned third-party actions in sensitive repos.

## Related
`devops-android-release`, `dependency-supply-chain`, `security-secrets-logging`, `termux-android-dev`, `devops-render-deploy`.
