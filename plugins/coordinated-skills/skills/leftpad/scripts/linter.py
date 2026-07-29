#!/usr/bin/env python3
"""leftpad linter — no ADD without registry evidence and an exit plan.

Exit 0 = PASS, 1 = FAIL, 2 = usage error.
"""
import re
import sys

REQUIRED_SECTIONS = [
    "## Need",
    "## Ladder",
    "## Registry Evidence",
    "## Exit Plan",
    "## Verdict",
]

HAND_WAVES = ["it's popular", "everyone uses it", "should be maintained", "widely used so it's fine"]
PKG_AT_VERSION = re.compile(r"Registry:\s*\S+@\S+")
LAST_PUBLISH = re.compile(r"Last publish:\s*\S+")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{4}\b")
VERDICT_RE = re.compile(r"^\s*(ADD|USE-STDLIB|USE-EXISTING|VENDOR|NO-NEED)\b", re.MULTILINE)


def section(text: str, header: str) -> str:
    m = re.search(re.escape(header) + r"\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    return m.group(1) if m else ""


def lint(text: str) -> list[str]:
    v: list[str] = []
    low = text.lower()

    for h in REQUIRED_SECTIONS:
        if h not in text:
            v.append(f"MISSING SECTION: {h}")

    for w in HAND_WAVES:
        if w in low:
            v.append(f"HAND WAVE: '{w}' — cite the registry, not the vibe")

    ladder = section(text, "## Ladder")
    if "## Ladder" in text:
        if not re.search(r"Stdlib check:\s*\S", ladder):
            v.append("STDLIB RUNG SKIPPED: add 'Stdlib check: <what was checked, result>'")
        if not re.search(r"Existing deps check:\s*\S", ladder):
            v.append("EXISTING-DEPS RUNG SKIPPED: add 'Existing deps check: <...>'")

    vd = section(text, "## Verdict")
    m = VERDICT_RE.search(vd)
    if "## Verdict" in text and not m:
        v.append("INVALID VERDICT: must be ADD, USE-STDLIB, USE-EXISTING, VENDOR, or NO-NEED")

    if m and m.group(1) == "ADD":
        ev = section(text, "## Registry Evidence")
        if not PKG_AT_VERSION.search(ev):
            v.append("ADD WITHOUT REGISTRY PROOF: need 'Registry: <name>@<version> on <registry>'")
        lp = LAST_PUBLISH.search(ev)
        if not lp or not DATE_RE.search(ev):
            v.append("ADD WITHOUT FRESHNESS: need 'Last publish:' with a date")
        exit_plan = section(text, "## Exit Plan").strip()
        if not exit_plan or exit_plan.lower().startswith("n/a"):
            v.append("ADD WITHOUT EXIT PLAN: name the fallback if this package dies")

    return v


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: linter.py <decision.md>", file=sys.stderr)
        return 2
    try:
        text = open(sys.argv[1], encoding="utf-8").read()
    except OSError as e:
        print(f"cannot read file: {e}", file=sys.stderr)
        return 2
    violations = lint(text)
    if violations:
        print(f"FAIL — {len(violations)} violation(s):")
        for x in violations:
            print(f"  - {x}")
        return 1
    print("PASS — dependency decision is grounded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
