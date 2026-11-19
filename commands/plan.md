# /plan
Convert the request into a minimal implementation plan.

**Agents:** product-analyst, technical-architect
**Skills:** `docs-adr-handoff`

## Steps
1. Restate the goal; list assumptions and non-goals.
2. Map files likely affected and protected contracts.
3. Write acceptance criteria (Given/When/Then for risky parts).
4. Risks, test plan, rollback approach, estimated slices.

## Output
Plan with slices in dependency order and explicit open questions.

## Guardrail
No edits until the plan is accepted when the change is high-risk or broad.
