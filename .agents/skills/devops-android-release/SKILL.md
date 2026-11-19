---
name: devops-android-release
description: "Build, sign and ship Android releases safely: Play App Signing, upload keystore handling, AAB, versionCode/versionName, R8 mapping and symbols, staged rollout, rollback, OTA/APK distribution via GitHub releases. Use for any release build, signing error, Play Console upload, 'APK not installing', or shipping updates outside Play."
domain: devops
---

# Android release

- Use Play App Signing: you hold an **upload key**; Google holds the app signing key. Keystore + passwords never in git; locally `key.properties` (gitignored); in CI inject as base64 secret and decode at build time.
- Build an AAB for Play: `flutter build appbundle --release` (or `./gradlew bundleRelease`). Obfuscated Flutter: add `--obfuscate --split-debug-info=build/symbols` and archive the symbols.
- `versionCode` strictly increases; `versionName` human readable. Automate it from CI run number or a tag.
- Upload R8 `mapping.txt` / native symbols to the crash reporter.
- Verify the artifact: signature (`apksigner verify --print-certs`), package id, version, permissions (`aapt2 dump badging`), target SDK meets current Play requirements (check the Play policy page).
- Release to internal -> closed -> production with **staged rollout** (e.g. 5% -> 20% -> 50% -> 100%) while watching crash-free rate/ANR.
- Rollback = halt the rollout and ship a fix with a HIGHER versionCode (Play cannot downgrade installed users). Keep server APIs compatible with the previous app version.
- Publishing/uploading requires explicit human approval.

## Sideloaded / OTA APK distribution (GitHub Releases or own server)
- Sign every release with the **same key** forever (installed apps only update if the signature matches); back the keystore up offline, encrypted.
- Provide one APK per ABI (`--split-per-abi`) or a universal one; publish SHA-256 next to the file; `apksigner verify --print-certs app.apk`.
- In-app updater: fetch a version manifest (`versionCode`, URL, sha256), verify the hash and signature before install, use `PackageInstaller`/`ACTION_VIEW` with `REQUEST_INSTALL_PACKAGES` and FileProvider; never download over plain HTTP.
- Play policy restricts self-updating outside Play for store-distributed apps: use this only for sideloaded distributions.

## Verify
Install the release artifact on a clean device and on a device with the previous version (upgrade path, data migration), check `versionCode`, signature, permissions, minify/shrink effects (crash on startup = missing keep rules), deep links, push.

## Pitfalls
- Losing the upload/signing key (enroll in Play App Signing).
- Forgetting to bump `versionCode`.
- Shipping a debug-signed or unobfuscated build.

## Related
`release-checklist-rollback`, `devops-ci-flutter-node`, `debugging-android-crash-anr`, `security-secrets-logging`.
