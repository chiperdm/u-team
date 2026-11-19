# /android-assistant
Add or harden voice assistant, HUD overlay or phone-control features on Android.

**Agents:** android-platform-engineer, llm-integration-engineer, security-auditor
**Skills:** `android-voice-assistant`, `android-overlay-accessibility`, `llm-integration-safety`, `security-threat-modeling`

## Steps
1. Threat-model the capability list; ask approval for new dangerous permissions.
2. Design the state machine and confirmation gates.
3. Implement with least-power APIs first; add kill switch and visible indicator.
4. Test on real devices (locked, idle, headset, battery saver).
5. Document Play policy risks.

## Output
Capabilities/permissions table, state machine diagram (text), test matrix, risks.

## Guardrail
Confirm before irreversible actions; never capture sensitive screen content.
