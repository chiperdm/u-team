# Workflow: Android Feature Delivery (Kotlin)
1. `product-analyst`: stories and criteria (include permission and background constraints).
2. `technical-architect`: layer map (UI/ViewModel/Repository/Room), threat model if sensitive.
3. `kotlin-engineer`: data layer, coroutines/flows, services, migrations (`android-architecture-room`, `kotlin-coroutines-flow`).
4. `compose-ui-engineer`: screens, motion, accessibility (`kotlin-compose-foundations`, `compose-motion-gestures`).
5. `android-platform-engineer` (if voice/overlay/accessibility): state machine, confirmations, OEM tests.
6. `test-engineer`: unit (runTest/Turbine), Compose tests, migration tests.
7. `security-auditor`: permissions, exported components, storage, logs.
8. `code-reviewer` -> `final-verifier` -> `release-engineer` for build/signing.
