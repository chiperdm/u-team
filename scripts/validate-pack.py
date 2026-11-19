#!/usr/bin/env python3
"""Validate structure AND quality of the pack, then regenerate derived docs.

Checks: frontmatter, unique/trigger-style descriptions, domains, minimum depth, code-fence balance,
Verify sections, near-duplicate skills, agent<->skill wiring and sections, command references,
cross-references in `Related` lines, eval file references, bash syntax of scripts.
Writes: docs/manifest.json, docs/SKILL-INDEX.md, and the COUNTS blocks in README.md / AGENTS.md.
Exit code 1 on any problem (derived docs are not written then).
"""
import json, re, subprocess, sys
from pathlib import Path

base = Path(__file__).resolve().parents[1]
bad, warn = [], []
DOMAINS = {"security", "backend", "database", "realtime", "flutter", "android", "ui", "web", "devops", "quality", "docs", "process", "ai"}

def split(path):
    t = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
    if not m:
        bad.append(f"{path.relative_to(base)}: missing frontmatter"); return {}, t
    d = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        d[k.strip()] = v.strip()
    return d, m.group(2)

def jstr(v):
    return json.loads(v) if v.startswith('"') else v

# ---------- skills ----------
skills, descs, domains = {}, {}, {}
for p in sorted((base / ".agents/skills").glob("*/SKILL.md")):
    d, body = split(p)
    n = p.parent.name
    if d.get("name") != n: bad.append(f"{n}: name != folder")
    try: desc = jstr(d.get("description", ""))
    except Exception: desc = ""; bad.append(f"{n}: description is not valid JSON string")
    if not 60 <= len(desc) <= 1024: bad.append(f"{n}: description length {len(desc)} (60..1024)")
    if not re.search(r"\b[Uu]se\b", desc): bad.append(f"{n}: description lacks a 'Use when ...' trigger")
    if desc in descs: bad.append(f"{n}: duplicate description of {descs[desc]}")
    descs[desc] = n
    dom = d.get("domain")
    if dom not in DOMAINS: bad.append(f"{n}: domain '{dom}' not in {sorted(DOMAINS)}")
    domains[n] = dom
    b = body.strip()
    if len(b) < 900: bad.append(f"{n}: body too thin ({len(b)} chars)")
    if b.count("```") % 2: bad.append(f"{n}: unbalanced code fences")
    if not re.search(r"^## .*Verify", b, re.M): bad.append(f"{n}: missing a '## Verify' section")
    if len(b.splitlines()) > 500: bad.append(f"{n}: over 500 lines (split into references/)")
    skills[n] = {"desc": desc, "lines": {l.strip() for l in b.splitlines() if len(l.strip()) > 25}, "body": b}
names = list(skills)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        u = skills[a]["lines"] | skills[b]["lines"]
        if u and len(skills[a]["lines"] & skills[b]["lines"]) / len(u) > 0.5: bad.append(f"near-duplicate skills: {a} / {b}")

# ---------- agents ----------
agents, agent_skills = {}, {}
REQ_SECTIONS = ["## Mission", "## You do", "## You never", "## Workflow", "## Definition of done", "## Hand off to", "## Operating rules"]
for p in sorted((base / ".agents/agents").glob("*.md")):
    d, body = split(p)
    n = p.stem
    if d.get("name") != n: bad.append(f"{p.name}: name != filename")
    if d.get("mode") not in ("read-only", "edit"): bad.append(f"{n}: mode must be read-only|edit")
    if not d.get("owns"): bad.append(f"{n}: missing owns")
    if d.get("mode") == "read-only" and d.get("owns", "").startswith('"(') is False and not re.search(r"docs/", d.get("owns", "")):
        warn.append(f"{n}: read-only agent owns paths (ok only for docs outputs)")
    try: sk = json.loads(d.get("skills", "[]"))
    except Exception: sk = []; bad.append(f"{n}: bad skills list")
    for s in sk:
        if s not in skills: bad.append(f"{n}: unknown skill '{s}'")
    if not sk: bad.append(f"{n}: no skills")
    if len(sk) != len(set(sk)): bad.append(f"{n}: duplicate skills in list")
    for sec in REQ_SECTIONS:
        if sec not in body: bad.append(f"{n}: missing section '{sec}'")
    agents[n] = d; agent_skills[n] = sk
used = {s for v in agent_skills.values() for s in v}
for s in skills:
    if s not in used: bad.append(f"skill '{s}' is not used by any agent")

# ---------- rules / commands / workflows / templates ----------
for d_ in ("rules", "commands", "workflows", "templates"):
    for p in (base / d_).glob("*.md"):
        if len(p.read_text(encoding="utf-8").strip()) < 80: bad.append(f"{p.relative_to(base)}: too short")
known = set(skills) | set(agents) | {p.stem for p in (base / "commands").glob("*.md")}
for p in (base / "commands").glob("*.md"):
    t = p.read_text(encoding="utf-8")
    m = re.search(r"\*\*Skills:\*\* (.*)", t)
    if m:
        for s in re.findall(r"`([^`]+)`", m.group(1)):
            if s not in skills: bad.append(f"commands/{p.name}: unknown skill '{s}'")
    for sec in ("## Steps", "## Output", "## Guardrail"):
        if sec not in t: bad.append(f"commands/{p.name}: missing '{sec}'")
for n, s in skills.items():
    for line in re.findall(r"^## Related\n(.*?)(?:\n\n|\Z)", s["body"], re.M | re.S):
        for tok in re.findall(r"`([a-z0-9][a-z0-9-]+)`", line):
            if "-" in tok and tok not in known and not tok.startswith(("rules", "hooks", "templates")):
                bad.append(f"{n}: Related reference '{tok}' not found")

# ---------- evals ----------
ev = base / "evals" / "skill-triggers.json"
if ev.exists():
    try:
        for e in json.loads(ev.read_text(encoding="utf-8")):
            if e["skill"] not in skills: bad.append(f"evals: unknown skill {e['skill']}")
            if len(e.get("should_trigger", [])) < 2 or not e.get("should_not_trigger"): bad.append(f"evals: {e['skill']} needs >=2 positive and >=1 negative")
    except Exception as ex: bad.append(f"evals: invalid JSON ({ex})")
else:
    warn.append("evals/skill-triggers.json missing")

# ---------- scripts ----------
for p in list((base / "hooks").glob("*.sh")) + list((base / "scripts").glob("*.sh")):
    if not p.read_text(encoding="utf-8").startswith("#!/usr/bin/env bash"): bad.append(f"{p.relative_to(base)}: missing shebang")
    if subprocess.run(["bash", "-n", str(p)]).returncode: bad.append(f"{p.relative_to(base)}: bash syntax error")
for p in base.rglob("*.py"):
    r = subprocess.run([sys.executable, "-m", "py_compile", str(p)], capture_output=True)
    if r.returncode: bad.append(f"{p.relative_to(base)}: python syntax error")

counts = dict(agents=len(agents), skills=len(skills),
              rules=len(list((base / "rules").glob("*.md"))), commands=len(list((base / "commands").glob("*.md"))),
              hooks=len(list((base / "hooks").glob("*.sh"))), workflows=len(list((base / "workflows").glob("*.md"))),
              templates=len(list((base / "templates").glob("*.md"))))
print(json.dumps(counts))
for w in warn: print("WARN:", w)
if bad:
    print("\n".join(bad)); sys.exit(1)

# ---------- derived docs ----------
(base / "docs" / "manifest.json").write_text(json.dumps({"name": "U-ORG AI Team v5", **counts}, indent=2) + "\n")
by_domain = {}
for n in sorted(skills): by_domain.setdefault(domains[n], []).append(n)
users = {}
for a, sk in agent_skills.items():
    for s in sk: users.setdefault(s, []).append(a)
lines = ["# Skill Index", "", f"_Generated by `scripts/validate-pack.py`: {counts['skills']} skills, {counts['agents']} agents. Do not edit by hand._", ""]
for dom in sorted(by_domain):
    lines += [f"## {dom}", "", "| Skill | Use it for | Agents |", "|---|---|---|"]
    for n in by_domain[dom]:
        first = re.split(r"(?<=[.!?])\s", skills[n]["desc"], 1)[0].replace("|", "/")
        if len(first) > 170: first = first[:167].rstrip() + "..."
        lines.append(f"| `{n}` | {first} | {', '.join(users.get(n, []))} |")
    lines.append("")
(base / "docs" / "SKILL-INDEX.md").write_text("\n".join(lines), encoding="utf-8")

def stamp(path, text):
    if not path.exists(): return
    t = path.read_text(encoding="utf-8")
    new = re.sub(r"<!-- COUNTS -->.*?<!-- /COUNTS -->", f"<!-- COUNTS -->{text}<!-- /COUNTS -->", t, flags=re.S)
    if new != t: path.write_text(new, encoding="utf-8")
stamp(base / "README.md", "\n| Part | Count |\n|---|---|\n" + "\n".join(f"| {k} | {v} |" for k, v in counts.items()) + "\n")
stamp(base / "AGENTS.md", f"{counts['agents']} agent profiles, {counts['skills']} skills, {counts['rules']} rules, {counts['commands']} commands")
print("Validation: PASS (docs/manifest.json, docs/SKILL-INDEX.md, README/AGENTS counts regenerated)")
