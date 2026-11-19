#!/usr/bin/env python3
"""Scaffold a new skill that already satisfies validate-pack.py's structure.

Usage: new-skill.py <skill-name> <domain> "<description with a Use when... trigger>"
Then: fill the sections, add the skill to at least one agent's `skills` list, add a case to evals/skill-triggers.json,
and run scripts/validate-pack.py.
"""
import json, re, sys
from pathlib import Path

if len(sys.argv) != 4:
    sys.exit(__doc__)
name, domain, desc = sys.argv[1:]
if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)+", name):
    sys.exit("skill name must be kebab-case with at least two parts")
root = Path(__file__).resolve().parents[1]
d = root / ".agents" / "skills" / name
if d.exists():
    sys.exit(f"{d} already exists")
d.mkdir(parents=True)
(d / "SKILL.md").write_text(f"""---
name: {name}
description: {json.dumps(desc)}
domain: {domain}
---

# {name.replace('-', ' ').title()}

## When this applies
(One paragraph: situations, inputs, what good output looks like.)

## Procedure
1. ...

## Patterns and snippets
```text
(Concrete, copy-pasteable, tested examples. Mark anything not compiled/run.)
```

## Verify
(Exact commands or observations that prove it works.)

## Pitfalls
- ...

## Related
`testing-strategy`
""", encoding="utf-8")
print(f"created {d}/SKILL.md")
