#!/usr/bin/env python3
"""hemlock linter — fails any verdict document that fakes rigor.

Exit 0 = PASS, exit 1 = FAIL (violations printed), exit 2 = usage error.
"""
import re
import sys

REQUIRED_SECTIONS = [
    "## Incumbent",
    "## Riskiest Assumption",
    "## Cheapest Decisive Test",
    "## Kill Bar",
    "## Result",
    "## Verdict",
]

WEASEL = [
    "no real competitors",
    "i'll know it when i see it",
    "should be fine",
    "probably fine",
    "everyone knows",
    "obviously better",
]

DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
NUMERIC_OR_BINARY = re.compile(
    r"(\d|>=|<=|>|<|==|\byes\b|\bno\b|\btrue\b|\bfalse\b|\bzero\b|\bany\b|\bexists\b|\bnone\b)",
    re.IGNORECASE,
)
VERDICT_RE = re.compile(r"^\s*(GO|NO-GO|CONDITIONAL-GO)\b", re.MULTILINE)
RANKED_ITEM = re.compile(r"^\s*\d+\.\s+\S", re.MULTILINE)


def section(text: str, header: str) -> str:
    """Return the body of a section (from header to next ## or EOF)."""
    m = re.search(re.escape(header) + r"\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    return m.group(1) if m else ""


def lint(text: str) -> list[str]:
    v: list[str] = []
    low = text.lower()

    for h in REQUIRED_SECTIONS:
        if h not in text:
            v.append(f"MISSING SECTION: {h}")

    for w in WEASEL:
        if w in low:
            v.append(f"WEASEL PHRASE: '{w}' — cite evidence or write a real bar")

    inc = section(text, "## Incumbent")
    if "## Incumbent" in text and not re.search(r"^Evidence:\s*\S+", inc, re.MULTILINE):
        v.append("INCUMBENT WITHOUT EVIDENCE: add 'Evidence: <url/registry/search-log>'")

    ra = section(text, "## Riskiest Assumption")
    if "## Riskiest Assumption" in text and len(RANKED_ITEM.findall(ra)) < 2:
        v.append("ASSUMPTIONS NOT RANKED: need >=2 numbered, ranked assumptions")

    kb = section(text, "## Kill Bar")
    if "## Kill Bar" in text:
        if not re.search(r"Pre-registered:\s*" + DATE_RE.pattern, kb):
            v.append("KILL BAR NOT PRE-REGISTERED: add 'Pre-registered: YYYY-MM-DD'")
        kill_line = re.search(r"KILL if:(.*)", kb)
        if not kill_line or not NUMERIC_OR_BINARY.search(kill_line.group(1)):
            v.append("KILL BAR NOT FALSIFIABLE: 'KILL if:' must state a numeric/binary condition")

    # Ordering: Kill Bar must precede Result (bar written before outcome)
    if "## Kill Bar" in text and "## Result" in text:
        if text.index("## Result") < text.index("## Kill Bar"):
            v.append("RESULT BEFORE KILL BAR: bar must be pre-registered before the result")

    vd = section(text, "## Verdict")
    if "## Verdict" in text:
        if not VERDICT_RE.search(vd):
            v.append("INVALID VERDICT: must be GO, NO-GO, or CONDITIONAL-GO")
        elif vd.strip().upper().startswith("CONDITIONAL-GO") and "next" not in vd.lower():
            v.append("CONDITIONAL-GO WITHOUT NEXT TEST: name the next assumption and its test")

    return v


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: linter.py <verdict.md>", file=sys.stderr)
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
    print("PASS — verdict document is honest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
