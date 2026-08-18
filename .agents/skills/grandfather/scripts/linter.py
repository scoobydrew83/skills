#!/usr/bin/env python3
"""grandfather linter — no breaking change without a deprecation window.

Exit 0 = PASS, 1 = FAIL, 2 = usage error.
"""
import re
import sys

REQUIRED_SECTIONS = [
    "## Surface",
    "## Classification",
    "## Deprecation Path",
    "## Migration",
    "## Verdict",
]

HYRUM_VIOLATIONS = ["nobody uses this", "probably safe to remove", "no one depends on"]
CLASS_RE = re.compile(
    r"Change type:\s*(internal|additive|shim|breaking|security-breaking)\b", re.IGNORECASE
)
DEP_RE = re.compile(r"Deprecated in:\s*(\S+)")
REM_RE = re.compile(r"Removed in:\s*(\S+)")
VERDICT_RE = re.compile(r"^\s*(SHIP-WITH-SHIM|SHIP|NEEDS-WINDOW|BLOCK)\b", re.MULTILINE)


def section(text: str, header: str) -> str:
    m = re.search(re.escape(header) + r"\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    return m.group(1) if m else ""


def lint(text: str) -> list[str]:
    v: list[str] = []
    low = text.lower()

    for h in REQUIRED_SECTIONS:
        if h not in text:
            v.append(f"MISSING SECTION: {h}")

    for w in HYRUM_VIOLATIONS:
        if w in low:
            v.append(f"HYRUM'S LAW: '{w}' — if a user could depend on it, someone does")

    cls_m = CLASS_RE.search(section(text, "## Classification"))
    if "## Classification" in text and not cls_m:
        v.append("INVALID CLASSIFICATION: must be internal/additive/shim/breaking/security-breaking")
    cls = cls_m.group(1).lower() if cls_m else None

    dep_sec = section(text, "## Deprecation Path")
    mig_sec = section(text, "## Migration").strip()
    dep = DEP_RE.search(dep_sec)
    rem = REM_RE.search(dep_sec)

    if cls == "breaking":
        if not dep or not rem:
            v.append("BREAKING WITHOUT WINDOW: need both 'Deprecated in:' and 'Removed in:' versions")
        elif dep.group(1) == rem.group(1):
            v.append(
                f"SAME-VERSION REMOVAL: deprecated and removed in {dep.group(1)} — "
                "removal must be a later version"
            )
        if not mig_sec or mig_sec.lower().startswith("n/a"):
            v.append("BREAKING WITHOUT MIGRATION: callers need exact before/after steps")

    if cls == "security-breaking" and (not mig_sec or mig_sec.lower().startswith("n/a")):
        v.append("SECURITY BREAK WITHOUT MIGRATION NOTE: break fast, but hand users the path")

    vd = section(text, "## Verdict")
    m = VERDICT_RE.search(vd)
    if "## Verdict" in text and not m:
        v.append("INVALID VERDICT: must be SHIP, SHIP-WITH-SHIM, NEEDS-WINDOW, or BLOCK")
    if m and m.group(1) == "SHIP" and cls == "breaking":
        if not dep or not rem or (dep and rem and dep.group(1) == rem.group(1)):
            v.append("SHIP ON UNWINDOWED BREAK: verdict must be NEEDS-WINDOW or add the window")

    return v


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: linter.py <review.md>", file=sys.stderr)
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
    print("PASS — every caller has a path")
    return 0


if __name__ == "__main__":
    sys.exit(main())
