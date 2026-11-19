# /test-feature
Derive and run a focused test matrix for a feature.

**Agents:** test-engineer
**Skills:** `testing-strategy`, `flutter-testing`, `testing-realtime`

## Steps
1. List criteria and risks; build the matrix (happy, boundary, invalid input, permission denied, offline/reconnect, retries, duplicates, regression).
2. Implement tests within scope; run them.
3. Separate executed from proposed tests.

## Output
Matrix with status (passed/failed/skipped/not run + reason) and commands.

## Guardrail
Do not edit production code.
