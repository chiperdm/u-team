# Workflow: Safe UI Redesign
1. Read project rules and inspect current screens/components.
2. Capture baseline screenshots for affected screens and states.
3. Map design tokens, theme variants, navigation, state, and component APIs.
4. Create a change plan with protected behavior and acceptance criteria.
5. Implement one component pilot, using existing abstractions.
6. Compare screenshots at identical viewport/theme/text scale.
7. Test interactions, accessibility, scrolling, keyboard, and responsive behavior.
8. Profile expensive effects on representative hardware.
9. Expand in small independent batches only after pilot acceptance.
10. Run tests/build and inspect diff. Keep rollback simple.
